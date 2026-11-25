"""
Fetch last 30 days daily OHLC and percentage difference for Silver Mini (MCX) from DhanHQ API.
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
    print("Error: Missing credentials in dhan_config.env")
    sys.exit(1)

ctx = DhanContext(client_id, access_token)
dhan = DhanHQ(ctx)

ist = pytz.timezone("Asia/Kolkata")

# SILVERM NOV FUT security ID: 483080, segment: MCX_COMM, instrument: FUTCOM
security_id = "483080"
exchange_segment = "MCX_COMM"
instrument_type = "FUTCOM"

# Fetch daily historical data
resp = dhan.historical_daily_data(
    security_id=security_id,
    exchange_segment=exchange_segment,
    instrument_type=instrument_type,
    from_date="2026-09-25",
    to_date="2026-11-23"
)

if resp.get("status") != "success":
    print("API Error:", resp)
    sys.exit(1)

data = resp.get("data", {})
ts_list = data.get("timestamp", [])
opens = data.get("open", [])
highs = data.get("high", [])
lows = data.get("low", [])
closes = data.get("close", [])

rows = []
for i in range(len(ts_list)):
    dt_utc = datetime.fromtimestamp(ts_list[i], tz=timezone.utc)
    dt_ist = dt_utc.astimezone(ist)
    date_str = dt_ist.strftime("%d-%b-%Y")
    rows.append({
        "date": date_str,
        "open": opens[i],
        "high": highs[i],
        "low": lows[i],
        "close": closes[i]
    })

# Fetch today's live candle (23-Nov-2026) via OHLC data
try:
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
except Exception as e:
    pass

# Filter to the last 30 trading sessions
rows = rows[-30:]

print("| # | Date | Open (₹) | High (₹) | Low (₹) | Close (₹) | Diff (C - O) | Intraday % | Day Change % |")
print("|---|---|---|---|---|---|---|---|---|")

prev_close = None
for idx, r in enumerate(rows, 1):
    o = r["open"]
    h = r["high"]
    l = r["low"]
    c = r["close"]
    
    # Intraday difference: Close vs Open
    diff_co = c - o
    pct_co = (diff_co / o) * 100 if o else 0
    
    # Day Change vs Previous Close
    if prev_close is not None and prev_close > 0:
        day_diff = c - prev_close
        pct_prev = (day_diff / prev_close) * 100
        day_chg_str = f"{pct_prev:+.2f}%"
    else:
        day_chg_str = "N/A"
        
    prev_close = c
    
    sign_co = "+" if pct_co > 0 else ""
    print(f"| {idx:02d} | {r['date']} | {o:,.0f} | {h:,.0f} | {l:,.0f} | {c:,.0f} | {diff_co:+,.0f} | {sign_co}{pct_co:.2f}% | {day_chg_str} |")
