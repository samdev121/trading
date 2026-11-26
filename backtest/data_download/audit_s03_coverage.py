from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def audit(path: Path) -> tuple[pd.DataFrame, dict[str, float | int | bool]]:
    columns = ["date", "timestamp", "expiry", "strike", "option_type", "underlying_price"]
    frame = pd.read_parquet(path, columns=columns)
    frame = frame[
        frame["option_type"].eq("CE")
        & (frame["timestamp"].dt.strftime("%H:%M") <= "15:15")
    ].copy()
    frame["expiry"] = pd.to_datetime(frame["expiry"]).dt.date
    frame["session"] = pd.to_datetime(frame["date"]).dt.date
    session_clocks = {
        session: set(group["timestamp"])
        for session, group in frame.groupby("session")
    }

    rows: list[dict] = []
    for session, day in frame.groupby("session"):
        entry_chain = day[day["timestamp"].dt.strftime("%H:%M").eq("10:00")]
        expiries = sorted(expiry for expiry in entry_chain["expiry"].unique() if expiry >= session)
        if not expiries:
            continue
        expiry = expiries[0] if expiries[0] > session else (expiries[1] if len(expiries) > 1 else expiries[0])
        chain = entry_chain[entry_chain["expiry"].eq(expiry)]
        if chain.empty:
            continue
        spot = float(chain["underlying_price"].median())
        short_strike = min(chain["strike"].unique(), key=lambda strike: abs(strike - spot * 1.007))
        hedge_strike = short_strike + 200
        expected = {
            timestamp
            for day_date, clocks in session_clocks.items()
            if session <= day_date <= expiry
            for timestamp in clocks
            if day_date > session or timestamp.strftime("%H:%M") >= "10:00"
        }
        coverage = {}
        for name, strike in (("short", short_strike), ("hedge", hedge_strike)):
            actual = set(frame[
                frame["expiry"].eq(expiry)
                & frame["strike"].eq(strike)
                & frame["timestamp"].isin(expected)
            ]["timestamp"])
            coverage[name] = len(actual) / len(expected) if expected else 0.0
        rows.append({
            "session": session, "expiry": expiry, "spot": spot,
            "short_strike": short_strike, "hedge_strike": hedge_strike,
            "expected_minutes": len(expected), "short_coverage": coverage["short"],
            "hedge_coverage": coverage["hedge"],
            "both_complete": coverage["short"] == 1.0 and coverage["hedge"] == 1.0,
        })

    details = pd.DataFrame(rows)
    complete = int(details["both_complete"].sum()) if not details.empty else 0
    summary = {
        "candidate_trades": len(details),
        "complete_trades": complete,
        "complete_pct": round(100 * complete / len(details), 2) if len(details) else 0.0,
        "median_short_coverage_pct": round(100 * details["short_coverage"].median(), 2) if len(details) else 0.0,
        "median_hedge_coverage_pct": round(100 * details["hedge_coverage"].median(), 2) if len(details) else 0.0,
        "minimum_short_coverage_pct": round(100 * details["short_coverage"].min(), 2) if len(details) else 0.0,
        "minimum_hedge_coverage_pct": round(100 * details["hedge_coverage"].min(), 2) if len(details) else 0.0,
        "backtest_ready": bool(len(details) and complete == len(details)),
    }
    return details, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit fixed-contract coverage required by positional S03.")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    details, summary = audit(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    details.to_csv(args.output.with_suffix(".csv"), index=False)
    args.output.with_suffix(".json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
