# Trading repository data rules

Before running, changing, or interpreting any backtest, run:

```bash
.venv/bin/python -m backtest.data_download.inventory
```

Treat `backtest/data_catalog.json` as the canonical source registry. Do not infer
coverage from filenames, comments in old scripts, or whichever Parquet file was
modified most recently.

## Current source roles

- Upstox `upstox_fixed_2026_h1` contains fixed-contract execution paths from
  2026-01-01 through 2026-07-21. It is approved for positional backtests.
- Dhan `dhan_rolling_2026_h2` contains reconstructed rolling-window observations
  from 2026-07-22 through 2026-11-25. It is approved for features and intraday
  research only when the selected path is complete.
- Dhan H2 must not be used as positional S03 execution data while its catalog
  quality audit reports `backtest_ready: false`.

Never concatenate provider datasets into one performance series without checking
the strategy policy in the catalog. Never fill missing option-contract candles
silently. Report source, coverage, quality status, and rejected trades with every
backtest result.
