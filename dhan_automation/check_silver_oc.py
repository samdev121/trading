"""
Inspect live Silver Mini Option Chain for 23-Nov-2026 expiry.
"""
import os
import sys
import json
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, "dhan_config.env"))

from dhanhq import dhanhq as DhanHQ, DhanContext

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

ctx = DhanContext(client_id, access_token)
dhan = DhanHQ(ctx)

chain = dhan.option_chain(
    under_security_id=483080,
    under_exchange_segment="MCX_COMM",
    expiry="2026-11-23"
)

raw = chain.get("data", {})
if isinstance(raw, str):
    raw = json.loads(raw)
data = raw.get("data", raw) if isinstance(raw, dict) else raw
if isinstance(data, str):
    data = json.loads(data)

spot = data.get("last_price", 0)
oc = data.get("oc", {})

print(f"=== SILVER MINI OPTION CHAIN (23-Nov-2026 Expiry) ===")
print(f"Underlying Futures Price: ₹{spot:,.2f}")
print(f"Total Strikes: {len(oc)}")

sorted_strikes = sorted([float(k) for k in oc.keys()])
near_strikes = [s for s in sorted_strikes if abs(s - spot) <= 6000]

print(f"\n{'Strike':>8} | {'CE LTP':>8} | {'CE Volume':>9} | {'CE OI':>7} | {'PE LTP':>8} | {'PE Volume':>9} | {'PE OI':>7}")
print("-" * 75)

for s in near_strikes:
    k = f"{s:.6f}"
    info = oc.get(k) or oc.get(str(int(s))) or {}
    ce = info.get("ce", {})
    pe = info.get("pe", {})
    ce_ltp = ce.get("last_price", 0)
    ce_vol = ce.get("volume", 0)
    ce_oi = ce.get("oi", 0)
    pe_ltp = pe.get("last_price", 0)
    pe_vol = pe.get("volume", 0)
    pe_oi = pe.get("oi", 0)
    marker = " <== ATM" if abs(s - spot) < 500 else ""
    print(f"{s:8.0f} | {ce_ltp:8.1f} | {ce_vol:9d} | {ce_oi:7d} | {pe_ltp:8.1f} | {pe_vol:9d} | {pe_oi:7d}{marker}")
