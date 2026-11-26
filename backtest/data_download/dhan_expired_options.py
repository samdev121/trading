from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Iterable

import pandas as pd

from .nse_calendar import expiry_for_code, is_trading_day


UNDERLYINGS = {
    "NIFTY": {"security_id": 13, "exchange_segment": "NSE_FNO"},
    "SENSEX": {"security_id": 51, "exchange_segment": "BSE_FNO"},
}
REQUIRED_DATA = ["open", "high", "low", "close", "volume", "oi", "iv", "strike", "spot"]


def date_chunks(start: date, end: date, maximum_days: int = 30) -> Iterable[tuple[date, date]]:
    """Yield inclusive chunks while sending Dhan an exclusive to-date."""
    cursor = start
    while cursor <= end:
        chunk_end = min(end, cursor + timedelta(days=maximum_days - 1))
        yield cursor, chunk_end
        cursor = chunk_end + timedelta(days=1)


def strike_label(offset: int) -> str:
    if offset == 0:
        return "ATM"
    return f"ATM{offset:+d}"


def normalize_response(response: dict[str, Any], metadata: dict[str, Any]) -> pd.DataFrame:
    """Normalize one Dhan rolling-option response into minute rows."""
    payload: Any = response.get("data", response)
    while isinstance(payload, dict) and set(payload) == {"data"}:
        payload = payload["data"]

    option_type = metadata["option_type"]
    key = "ce" if option_type == "CE" else "pe"
    block = payload.get(key) if isinstance(payload, dict) else None
    if not isinstance(block, dict) or not block:
        return pd.DataFrame()

    lengths = {len(value) for value in block.values() if isinstance(value, list) and value}
    if not lengths:
        return pd.DataFrame()
    if len(lengths) != 1:
        raise ValueError(f"Dhan returned inconsistent column lengths: {sorted(lengths)}")
    row_count = next(iter(lengths))
    columns = {
        name: values
        for name, values in block.items()
        if isinstance(values, list) and len(values) == row_count
    }
    frame = pd.DataFrame(columns)
    if frame.empty:
        return frame

    frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="s", utc=True).dt.tz_convert("Asia/Kolkata")
    frame["date"] = frame["timestamp"].dt.date.astype(str)
    for name, value in metadata.items():
        frame[name] = value
    frame["underlying_price"] = frame.get("spot")
    frame["source"] = "dhan_rolling_expired_options"
    frame["granularity"] = "1min"
    return frame


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def request_with_retry(client, request: dict[str, Any], delay_seconds: float, attempts: int = 5) -> dict[str, Any]:
    """Throttle Dhan calls and retry the observed DH-904 rate-limit response."""
    response: dict[str, Any] = {}
    for attempt in range(attempts):
        response = client.expired_options_data(**request)
        time.sleep(delay_seconds)
        remarks = response.get("remarks") if isinstance(response, dict) else None
        error_code = remarks.get("error_code") if isinstance(remarks, dict) else None
        if error_code != "DH-904":
            return response
        time.sleep(delay_seconds * (2 ** attempt))
    return response


def download_rolling_options(
    underlying: str,
    start: date,
    end: date,
    output_root: Path,
    expiry_flag: str = "WEEK",
    expiry_codes: tuple[int, ...] = (1, 2),
    offsets: range = range(-10, 11),
    request_delay: float = 0.35,
    trading_days_only: bool = True,
) -> tuple[Path, Path]:
    """Download cached raw responses and create one deduplicated rolling dataset."""
    from dhanhq import DhanContext, dhanhq

    config = UNDERLYINGS[underlying]
    client_id = os.environ.get("DHAN_CLIENT_ID") or os.environ.get("DHAN_CLIENTID")
    access_token = os.environ.get("DHAN_ACCESS_TOKEN") or os.environ.get("DHAN_TOKEN")
    if not client_id or not access_token:
        raise RuntimeError("Dhan credentials are not configured.")
    client = dhanhq(DhanContext(client_id, access_token))

    raw_root = output_root / "raw" / underlying.lower()
    normalized_root = output_root / "normalized" / underlying.lower()
    raw_root.mkdir(parents=True, exist_ok=True)
    normalized_root.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []
    requests = 0

    failures: list[dict[str, Any]] = []
    # The endpoint returns both endpoints for adjacent dates. Pair consecutive
    # trading days to avoid downloading the second session twice. A weekend or
    # holiday starts a new request window.
    sessions = [day for day in pd.date_range(start, end, freq="D").date
                if not trading_days_only or is_trading_day(day)]
    request_windows: list[tuple[date, date]] = []
    position = 0
    while position < len(sessions):
        chunk_start = sessions[position]
        if position + 1 < len(sessions) and sessions[position + 1] == chunk_start + timedelta(days=1):
            chunk_end = sessions[position + 1]
            position += 2
        else:
            chunk_end = chunk_start
            position += 1
        request_windows.append((chunk_start, chunk_end))

    for chunk_start, chunk_end in request_windows:
        api_end = chunk_end if chunk_end > chunk_start else chunk_start + timedelta(days=1)
        for expiry_code in expiry_codes:
            for offset in offsets:
                label = strike_label(offset)
                for option_type, dhan_type in (("CE", "CALL"), ("PE", "PUT")):
                    request = {
                        "security_id": config["security_id"],
                        "exchange_segment": config["exchange_segment"],
                        "instrument_type": "OPTIDX",
                        "expiry_flag": expiry_flag,
                        "expiry_code": expiry_code,
                        "strike": label,
                        "drv_option_type": dhan_type,
                        "required_data": REQUIRED_DATA,
                        "from_date": chunk_start.isoformat(),
                        "to_date": api_end.isoformat(),
                        "interval": 1,
                    }
                    digest = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:16]
                    raw_path = raw_root / f"{chunk_start}_{chunk_end}_{digest}.json"
                    prior_paths = list(raw_root.glob(f"*_{digest}.json"))
                    if not raw_path.exists() and prior_paths:
                        raw_path = prior_paths[0]
                    response = json.loads(raw_path.read_text()) if raw_path.exists() else None
                    if not isinstance(response, dict) or response.get("status") == "failure":
                        response = request_with_retry(client, request, request_delay)
                        raw_path.write_text(json.dumps(response, separators=(",", ":"), default=str))
                        requests += 1
                    if not isinstance(response, dict) or response.get("status") == "failure":
                        failures.append({
                            "date": chunk_start.isoformat(), "expiry_code": expiry_code,
                            "strike": label, "option_type": option_type,
                            "remarks": response.get("remarks") if isinstance(response, dict) else str(response),
                        })
                        continue
                    frame = normalize_response(response, {
                        "underlying": underlying,
                        "expiry_flag": expiry_flag,
                        "expiry_code": expiry_code,
                        "strike_offset": offset,
                        "strike_request": label,
                        "option_type": option_type,
                    })
                    if not frame.empty:
                        frames.append(frame)

    if not frames:
        raise RuntimeError("Dhan returned no option rows.")
    rolling = pd.concat(frames, ignore_index=True)
    rolling = rolling[(rolling["timestamp"].dt.date >= start) & (rolling["timestamp"].dt.date <= end)]
    keys = ["timestamp", "expiry_flag", "expiry_code", "strike_offset", "option_type"]
    rolling = rolling.drop_duplicates(keys).sort_values(keys).reset_index(drop=True)
    rolling_path = normalized_root / f"rolling_{start}_{end}.parquet"
    rolling.to_parquet(rolling_path, index=False)

    manifest = {
        "underlying": underlying,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "expiry_flag": expiry_flag,
        "expiry_codes": list(expiry_codes),
        "strike_offsets": [offsets.start, offsets.stop - 1],
        "rows": len(rolling),
        "network_requests": requests,
        "request_delay_seconds": request_delay,
        "failed_or_unavailable_requests": len(failures),
        "failures": failures,
        "expiry_code_observation": "Rolling endpoint rejected 0; 1 and 2 were used for current and next expiry.",
    }
    manifest_path = rolling_path.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return rolling_path, manifest_path


def add_calendar_expiry(rolling_path: Path, output_path: Path) -> Path:
    """Attach 2026 NIFTY weekly expiries using the verified NSE holiday calendar."""
    rolling = pd.read_parquet(rolling_path)
    if not rolling["date"].str.startswith("2026-").all():
        raise ValueError("The bundled verified expiry calendar currently covers 2026 only.")
    calendar_end = date(2027, 1, 15)
    rolling["expiry"] = rolling.apply(
        lambda row: expiry_for_code(date.fromisoformat(row["date"]), int(row["expiry_code"]), calendar_end),
        axis=1,
    )
    rolling["expiry"] = rolling["expiry"].astype(str)
    fixed = rolling[rolling["expiry"] != "None"].drop_duplicates(
        ["timestamp", "expiry", "strike", "option_type"]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fixed.to_parquet(output_path, index=False)
    return output_path


def add_reference_expiry(rolling_path: Path, reference_path: Path, output_path: Path) -> Path:
    """Map Dhan rolling expiry codes to actual expiries observed in a reference chain."""
    rolling = pd.read_parquet(rolling_path)
    reference = pd.read_parquet(reference_path, columns=["date", "expiry"])
    reference["date"] = reference["date"].astype(str)
    reference["expiry"] = reference["expiry"].astype(str)
    available = (
        reference.drop_duplicates().query("expiry >= date").sort_values(["date", "expiry"])
        .groupby("date")["expiry"].apply(list).to_dict()
    )

    def resolve(row: pd.Series) -> str | None:
        expiries = available.get(row["date"], [])
        position = int(row["expiry_code"]) - 1
        return expiries[position] if position < len(expiries) else None

    rolling["expiry"] = rolling.apply(resolve, axis=1)
    fixed = rolling.dropna(subset=["expiry", "strike"])
    fixed = fixed.drop_duplicates(["timestamp", "expiry", "strike", "option_type"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fixed.to_parquet(output_path, index=False)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Dhan rolling expired options with actual strikes.")
    parser.add_argument("--underlying", choices=sorted(UNDERLYINGS), default="NIFTY")
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--output", type=Path, default=Path("backtest/data/dhan"))
    parser.add_argument("--env-file", type=Path, default=Path("dhan_automation/dhan_config.env"))
    parser.add_argument("--expiry-codes", type=int, nargs="+", default=[1, 2])
    parser.add_argument("--offset-min", type=int, default=-10)
    parser.add_argument("--offset-max", type=int, default=10)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--request-delay", type=float, default=0.35)
    parser.add_argument("--nse-2026-calendar", action="store_true")
    args = parser.parse_args()
    if args.end < args.start or args.offset_min > args.offset_max:
        parser.error("Invalid date range or strike-offset range.")
    load_env(args.env_file)
    rolling, manifest = download_rolling_options(
        args.underlying, args.start, args.end, args.output,
        expiry_codes=tuple(args.expiry_codes),
        offsets=range(args.offset_min, args.offset_max + 1),
        request_delay=args.request_delay,
    )
    print(f"Wrote rolling data: {rolling}")
    print(f"Wrote manifest: {manifest}")
    if args.reference:
        fixed = rolling.with_name(rolling.stem.replace("rolling_", "fixed_") + ".parquet")
        add_reference_expiry(rolling, args.reference, fixed)
        print(f"Wrote reference-mapped fixed contracts: {fixed}")
    elif args.nse_2026_calendar:
        fixed = rolling.with_name(rolling.stem.replace("rolling_", "fixed_") + ".parquet")
        add_calendar_expiry(rolling, fixed)
        print(f"Wrote calendar-mapped fixed contracts: {fixed}")


if __name__ == "__main__":
    main()
