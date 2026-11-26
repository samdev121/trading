from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ValidationReport:
    rows: int
    contracts: int
    duplicate_rows: int
    invalid_ohlc_rows: int
    missing_session_minutes: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def validate_option_file(path: Path) -> ValidationReport:
    frame = pd.read_parquet(path)
    required = {"timestamp", "open", "high", "low", "close", "strike", "option_type"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing: {', '.join(sorted(missing))}")
    contract_keys = [key for key in ("expiry", "expiry_code", "strike", "option_type") if key in frame]
    row_keys = ["timestamp", *contract_keys]
    duplicates = int(frame.duplicated(row_keys).sum())
    prices = frame[["open", "high", "low", "close"]]
    invalid = int(((frame["high"] < prices.max(axis=1)) |
                   (frame["low"] > prices.min(axis=1)) |
                   prices.le(0).any(axis=1)).sum())

    minute_frame = frame[["timestamp", *contract_keys]].copy()
    minute_frame["session"] = pd.to_datetime(minute_frame["timestamp"]).dt.date
    minute_frame = minute_frame.drop_duplicates().sort_values([*contract_keys, "session", "timestamp"])
    gaps = minute_frame.groupby([*contract_keys, "session"])["timestamp"].diff()
    missing_minutes = int(gaps.dt.total_seconds().div(60).sub(1).clip(lower=0).sum())
    contracts = int(frame[contract_keys].drop_duplicates().shape[0])
    return ValidationReport(len(frame), contracts, duplicates, invalid, missing_minutes)
