# Dhan expired-options dataset

Before using any local market data, inspect `backtest/data_catalog.json`:

```bash
.venv/bin/python -m backtest.data_download.inventory
```

The catalog defines each provider's role and blocks the Dhan rolling dataset
from being treated as a positional fixed-contract replacement.

The downloader keeps Dhan raw responses and normalized rolling rows under
`backtest/data/`, which is ignored by Git. It never changes the existing
Upstox Parquet files.

## Overlap proof

Download a small range and map rolling expiry codes to actual expiries already
present in the Upstox reference dataset:

```bash
.venv/bin/python -m backtest.data_download.dhan_expired_options \
  --start 2026-06-01 \
  --end 2026-06-05 \
  --expiry-codes 1 2 \
  --offset-min -10 \
  --offset-max 10 \
  --reference backtest/data/NIFTY_2026_intraday.parquet
```

The downloader caches every raw API response, limits request frequency, retries
Dhan `DH-904` rate-limit responses, and writes a manifest next to each Parquet
file. Failed or unavailable strike requests remain visible in that manifest.

## Dataset meanings

- `rolling_*.parquet` preserves Dhan's expiry code and ATM-relative request.
- `fixed_*.parquet` adds a verified actual expiry and deduplicates observations
  by timestamp, expiry, actual strike, and option type.
- Actual `strike` from the API must be used for a held position. The
  `strike_request` value such as `ATM+3` is only the rolling selection rule.

## Extending beyond the Upstox archive

The Dhan response contains actual strike but no actual expiry date. A verified
NSE expiry calendar is therefore required before post-July rolling rows can be
promoted to fixed-contract backtest data. Holiday-adjusted expiries must not be
guessed from an ordinary weekday rule.

The rolling endpoint currently behaves differently from the public expiry-code
annexure. In the tested subscription, code `0` was rejected, while codes `1`
and `2` returned current and next-expiry data. This observation is recorded in
each manifest and must be rechecked if Dhan changes the endpoint.

## Positional Strategy 3 coverage gate

Rolling `ATM±10` data can lose a held fixed contract after a sufficiently large
underlying move. Audit every reconstructed dataset before an S03 backtest:

```bash
.venv/bin/python -m backtest.data_download.audit_s03_coverage \
  --data backtest/data/dhan-2026/normalized/nifty/fixed_2026-07-22_2026-11-25.parquet \
  --output backtest/data/dhan-2026/audits/s03_coverage
```

`backtest_ready` is true only when both the selected short call and its 200-point
hedge have complete minute paths from entry through expiry for every candidate.
Incomplete paths must not be silently filled or omitted from performance results.
