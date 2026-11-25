"""
Fetch real-time snapshot of strikes around Spot for institutional setup analysis.
"""
import sys
from pathlib import Path

# Add current dir to path
sys.path.append(str(Path(__file__).resolve().parent))
from dhan_engine import get_dhan_client, get_nifty_expiry_list

dhan = get_dhan_client()
if not dhan:
    sys.exit(1)

exp_data = get_nifty_expiry_list()
dates = []
if isinstance(exp_data, list):
    dates = exp_data
elif isinstance(exp_data, dict):
    dates = exp_data.get("data", [])

expiry = str(dates[0]) if dates else "2026-11-23"

resp = dhan.option_chain(13, "IDX_I", expiry)
if resp.get("status") != "success":
    print("Failed to get chain:", resp)
    sys.exit(1)

raw_data = resp.get("data", {})
if "data" in raw_data and isinstance(raw_data["data"], dict):
    data = raw_data["data"]
else:
    data = raw_data

spot = float(data.get("last_price", 0))
oc = data.get("oc", {})

print(f"=== NIFTY LIVE SNAPSHOT (Expiry: {expiry}) ===")
print(f"Spot LTP: {spot:.2f}\n")

print(f"{'Strike':^8} | {'CE LTP':^8} | {'CE OI':^12} | {'PE LTP':^8} | {'PE OI':^12}")
print("-" * 56)

# Get sorted strikes around spot (spot - 200 to spot + 200)
sorted_strikes = sorted([float(k) for k in oc.keys() if abs(float(k) - spot) <= 200])

for s in sorted_strikes:
    info = oc.get(str(int(s))) or oc.get(f"{s:.6f}") or oc.get(str(s))
    if not info:
        continue
    ce = info.get("ce", {})
    pe = info.get("pe", {})
    ce_ltp = ce.get("last_price", 0)
    ce_oi = ce.get("oi", 0)
    pe_ltp = pe.get("last_price", 0)
    pe_oi = pe.get("oi", 0)
    marker = " <-- ATM" if abs(s - spot) < 25 else ""
    print(f"{int(s):^8} | {ce_ltp:^8.2f} | {ce_oi:^12,d} | {pe_ltp:^8.2f} | {pe_oi:^12,d}{marker}")
