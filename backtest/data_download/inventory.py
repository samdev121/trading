from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


def inspect_catalog(catalog_path: Path) -> dict:
    catalog = json.loads(catalog_path.read_text())
    report = {"catalog": str(catalog_path), "datasets": []}
    for dataset in catalog["datasets"]:
        path = Path(dataset["path"])
        item = {
            "id": dataset["id"],
            "provider": dataset["provider"],
            "path": str(path),
            "exists": path.exists(),
            "contract_model": dataset["contract_model"],
            "approved_uses": dataset["approved_uses"],
            "blocked_uses": dataset["blocked_uses"],
        }
        if path.exists():
            metadata = pq.ParquetFile(path).metadata
            dates = pd.read_parquet(path, columns=["date"])["date"].astype(str)
            item.update({
                "rows": metadata.num_rows,
                "actual_start": dates.min(),
                "actual_end": dates.max(),
                "sessions": dates.nunique(),
                "coverage_matches_catalog": (
                    dates.min() == dataset["expected_start"]
                    and dates.max() == dataset["expected_end"]
                ),
            })
        if dataset.get("quality_audit"):
            audit_path = Path(dataset["quality_audit"])
            item["quality_audit_exists"] = audit_path.exists()
            if audit_path.exists():
                item["quality_audit"] = json.loads(audit_path.read_text())
        report["datasets"].append(item)
    report["strategy_policies"] = catalog.get("strategy_policies", {})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify local backtest datasets against the canonical catalog.")
    parser.add_argument("--catalog", type=Path, default=Path("backtest/data_catalog.json"))
    args = parser.parse_args()
    print(json.dumps(inspect_catalog(args.catalog), indent=2))


if __name__ == "__main__":
    main()
