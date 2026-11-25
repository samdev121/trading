"""
Unified Institutional Market Pulse for NIFTY 50 (Buying & Selling Co-Pilot)
Fetches Spot OHLC, India VIX, Today's 5-min candles, and Option Chain with Greeks & OI Walls.
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, "dhan_config.env"))

from dhanhq import dhanhq as DhanHQ, DhanContext

ctx = DhanContext(os.getenv("DHAN_CLIENT_ID"), os.getenv("DHAN_ACCESS_TOKEN"))
dhan = DhanHQ(ctx)


def get_pulse():
    # 1. Spot & India VIX OHLC
    q_idx = dhan.ohlc_data(securities={"IDX_I": [13, 21]})
    idx_data = q_idx.get("data", {}).get("data", {}).get("IDX_I", {})
    nifty = idx_data.get("13", {})
    vix = idx_data.get("21", {})

    spot = nifty.get("last_price", 0)
    ohlc = nifty.get("ohlc", {})
    vix_ltp = vix.get("last_price", 0)

    print("=" * 88)
    print(f"NIFTY 50 LIVE PULSE | {datetime.now().strftime('%d-%b-%Y %H:%M:%S IST')}")
    print("=" * 88)
    print(f"NIFTY Spot : {spot:,.2f}  (O: {ohlc.get('open',0):,.2f} | H: {ohlc.get('high',0):,.2f} | L: {ohlc.get('low',0):,.2f} | PrevC: {ohlc.get('close',0):,.2f})")
    print(f"India VIX  : {vix_ltp:.2f}")

    # 2. Today's 5-min intraday candles
    today_str = datetime.now().strftime("%Y-%m-%d")
    intra = dhan.intraday_minute_data(
        security_id="13",
        exchange_segment="IDX_I",
        instrument_type="INDEX",
        from_date=today_str,
        to_date=today_str,
        interval=5
    )
    if intra.get("status") == "success":
        idata = intra.get("data", {})
        ts_list = idata.get("timestamp", [])
        opens = idata.get("open", [])
        highs = idata.get("high", [])
        lows = idata.get("low", [])
        closes = idata.get("close", [])
        if ts_list:
            print(f"\nRecent 5-Min Candles (Last 6 bars of {len(ts_list)} total):")
            for i in range(max(0, len(ts_list) - 6), len(ts_list)):
                dt_str = datetime.fromtimestamp(ts_list[i]).strftime("%H:%M")
                print(f"  [{dt_str}] O={opens[i]:.2f}  H={highs[i]:.2f}  L={lows[i]:.2f}  C={closes[i]:.2f}")

    # 3. Expiry & Option Chain
    exp_resp = dhan.expiry_list(13, "IDX_I")
    exp_data = exp_resp.get("data", [])
    if isinstance(exp_data, dict):
        exp_data = exp_data.get("data", [])
    expiry = str(exp_data[0]) if exp_data else "2026-12-01"

    chain = dhan.option_chain(13, "IDX_I", expiry)
    raw = chain.get("data", {})
    if isinstance(raw, str):
        raw = json.loads(raw)
    data = raw.get("data", raw) if isinstance(raw, dict) else raw
    if isinstance(data, str):
        data = json.loads(data)

    oc = data.get("oc", {})
    total_ce_oi = 0
    total_pe_oi = 0
    all_strikes = []

    for k, info in oc.items():
        s = float(k)
        ce = info.get("ce", {})
        pe = info.get("pe", {})
        ce_oi = ce.get("oi", 0)
        pe_oi = pe.get("oi", 0)
        total_ce_oi += ce_oi
        total_pe_oi += pe_oi
        all_strikes.append((s, ce, pe))

    pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
    print(f"\nExpiry: {expiry} | Total CE OI: {total_ce_oi:,} | Total PE OI: {total_pe_oi:,} | PCR: {pcr}")

    # Top 3 OI Walls
    top_ce = sorted(all_strikes, key=lambda x: x[1].get("oi", 0), reverse=True)[:3]
    top_pe = sorted(all_strikes, key=lambda x: x[2].get("oi", 0), reverse=True)[:3]
    print("Top Call Resistance Walls : " + " | ".join([f"{int(s)} ({c.get('oi',0):,})" for s, c, _ in top_ce]))
    print("Top Put Support Floors    : " + " | ".join([f"{int(s)} ({p.get('oi',0):,})" for s, _, p in top_pe]))

    print(f"\n{'Strike':>7} | {'CE LTP':>7} | {'CE Δ':>6} | {'CE IV':>5} | {'CE OI':>11} | {'PE LTP':>7} | {'PE Δ':>6} | {'PE IV':>5} | {'PE OI':>11}")
    print("-" * 88)
    for s, ce, pe in sorted(all_strikes, key=lambda x: x[0]):
        if abs(s - spot) <= 450:
            cg = ce.get("greeks", {})
            pg = pe.get("greeks", {})
            mark = " <-- ATM" if abs(s - spot) < 25 else ""
            print(
                f"{int(s):7d} | {ce.get('last_price',0):7.2f} | {cg.get('delta',0):6.2f} | "
                f"{ce.get('implied_volatility',0):5.1f} | {ce.get('oi',0):11,d} | "
                f"{pe.get('last_price',0):7.2f} | {pg.get('delta',0):6.2f} | "
                f"{pe.get('implied_volatility',0):5.1f} | {pe.get('oi',0):11,d}{mark}"
            )


if __name__ == "__main__":
    get_pulse()
