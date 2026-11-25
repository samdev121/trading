"""
Fetch last 30 days daily OHLC and sort descending by Day Change % for Silver Mini (MCX).
"""
import os
import sys
from datetime import datetime, timezone
import pytz
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, "dhan_config.env"))

from dhanhq import dhanhq as DhanHQ, DhanContext

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

if not client_id or not access_token:
    print("Error: Missing credentials")
    sys.exit(1)

ctx = DhanContext(client_id, access_token)
dhan = DhanHQ(ctx)

ist = pytz.timezone("Asia/Kolkata")
security_id = "483080"
exchange_segment = "MCX_COMM"
instrument_type = "FUTCOM"

# Fetch historical data
resp = dhan.historical_daily_data(
    security_id=security_id,
    exchange_segment=exchange_segment,
    instrument_type=instrument_type,
    from_date="2026-10-08",
    to_date="2026-11-23"
)

data = resp.get("data", {})
ts_list = data.get("timestamp", [])
opens = data.get("open", [])
highs = data.get("high", [])
lows = data.get("low", [])
closes = data.get("close", [])

rows = []
for i in range(len(ts_list)):
    dt = datetime.fromtimestamp(ts_list[i], tz=timezone.utc).astimezone(ist)
    rows.append({
        "date": dt.strftime("%d-%b-%Y"),
        "open": opens[i],
        "high": highs[i],
        "low": lows[i],
        "close": closes[i]
    })

# Add today's live data
quote = dhan.ohlc_data(securities={"MCX_COMM": [int(security_id)]})
mcx_data = quote.get("data", {}).get("data", {}).get("MCX_COMM", {}).get(security_id, {})
if mcx_data:
    today_ohlc = mcx_data.get("ohlc", {})
    today_ltp = mcx_data.get("last_price", 0)
    rows.append({
        "date": "23-Nov-2026 (Live)",
        "open": float(today_ohlc.get("open", 0)),
        "high": float(today_ohlc.get("high", 0)),
        "low": float(today_ohlc.get("low", 0)),
        "close": float(today_ltp)
    })

# Compute day change % vs previous close for every row
for i in range(1, len(rows)):
    prev_c = rows[i-1]["close"]
    c = rows[i]["close"]
    diff = c - prev_c
    pct = (diff / prev_c) * 100
    rows[i]["day_chg_pts"] = diff
    rows[i]["day_chg_pct"] = pct

# Select exactly the last 30 trading sessions
last_30 = [r for r in rows if "day_chg_pct" in r][-30:]

# Sort descending: Highest gain % to Lowest (deepest loss %)
sorted_rows = sorted(last_30, key=lambda x: x["day_chg_pct"], reverse=True)

print("| Rank | Date | Open (₹) | High (₹) | Low (₹) | Close (₹) | Day Change (₹) | Day Change % | Intraday % (C - O) |")
print("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
for rank, r in enumerate(sorted_rows, 1):
    o = r["open"]
    h = r["high"]
    l = r["low"]
    c = r["close"]
    day_pts = r["day_chg_pts"]
    day_pct = r["day_chg_pct"]
    co_pts = c - o
    co_pct = (co_pts / o) * 100
    emoji = "🟢" if day_pct >= 0 else "🔴"
    d_str = r["date"]
    print(f"| **{rank:02d}** | {d_str} | {o:,.0f} | {h:,.0f} | {l:,.0f} | {c:,.0f} | {day_pts:+,.0f} | **{day_pct:+.2f}%** {emoji} | {co_pct:+.2f}% |")
