from datetime import date
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from backtest.data_download.dhan_expired_options import date_chunks, normalize_response, strike_label
from backtest.data_download.validate import validate_option_file
from backtest.data_download.nse_calendar import expiry_for_code, nifty_weekly_expiries


class DhanExpiredOptionsTest(unittest.TestCase):
    def test_nse_holiday_adjusted_expiries(self):
        expiries = nifty_weekly_expiries(date(2026, 10, 1), date(2026, 11, 30))
        self.assertIn(date(2026, 10, 19), expiries)
        self.assertIn(date(2026, 11, 9), expiries)
        self.assertIn(date(2026, 11, 23), expiries)
        self.assertNotIn(date(2026, 10, 20), expiries)
        self.assertEqual(expiry_for_code(date(2026, 11, 4), 1, date(2027, 1, 15)), date(2026, 11, 9))
        self.assertEqual(expiry_for_code(date(2026, 11, 4), 2, date(2027, 1, 15)), date(2026, 11, 17))

    def test_date_chunks_and_labels(self):
        self.assertEqual(list(date_chunks(date(2026, 1, 1), date(2026, 2, 1))), [
            (date(2026, 1, 1), date(2026, 1, 30)),
            (date(2026, 1, 31), date(2026, 2, 1)),
        ])
        self.assertEqual([strike_label(x) for x in (-2, 0, 3)], ["ATM-2", "ATM", "ATM+3"])

    def test_normalization_preserves_actual_strike(self):
        response = {"status": "success", "data": {"data": {"ce": {
            "timestamp": [1780295100], "open": [100], "high": [102], "low": [99],
            "close": [101], "strike": [23650], "spot": [23640], "oi": [10],
        }, "pe": None}}}
        frame = normalize_response(response, {
            "underlying": "NIFTY", "expiry_flag": "WEEK", "expiry_code": 1,
            "strike_offset": 0, "strike_request": "ATM", "option_type": "CE",
        })
        self.assertEqual(frame.loc[0, "strike"], 23650)
        self.assertEqual(frame.loc[0, "option_type"], "CE")

    def test_validation_does_not_count_overnight_as_missing(self):
        frame = pd.DataFrame({
            "timestamp": pd.to_datetime(["2026-01-01 15:29", "2026-01-02 09:15"]),
            "expiry_code": [1, 1], "strike": [25000, 25000], "option_type": ["CE", "CE"],
            "open": [1, 1], "high": [1, 1], "low": [1, 1], "close": [1, 1],
        })
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.parquet"
            frame.to_parquet(path, index=False)
            report = validate_option_file(path)
        self.assertEqual(report.missing_session_minutes, 0)


if __name__ == "__main__":
    unittest.main()
