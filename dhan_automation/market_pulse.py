"""
Unified Institutional Market Pulse for NIFTY 50 (Buying & Selling Co-Pilot)
Fetches Spot OHLC, India VIX, NIFTY Futures + Session VWAP, 5-min candles,
and Option Chain with Greeks & OI Walls.
"""
import datetime as dt
import sys
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from dhan_engine import (
    IST_OFFSET,
    compute_session_vwap,
    get_dhan_client,
    get_nifty_expiry_list,
    resolve_nifty_front_future,
    unwrap_option_chain_data,
)


def _vix_regime(vix_val: float) -> str:
    if vix_val <= 0:
        return "UNKNOWN"
    if vix_val < 12.0:
        return "LOW / SLUGGISH (<12: Theta Risk for Buyers)"
    if vix_val <= 17.5:
        return "GOLDILOCKS (13-17.5: Ideal Buying Momentum)"
    if vix_val <= 18.0:
        return "ELEVATED (17.5-18: Tight Risk / Quick T1)"
    return "HIGH VOLATILITY (>18: Fast Moves / Book T1 Quick)"


def get_pulse():
    dhan = get_dhan_client()
    if not dhan:
        sys.exit(1)

    now_ist = dt.datetime.now(IST_OFFSET)
    today_str = now_ist.strftime("%Y-%m-%d")

    # 1. Spot & India VIX OHLC
    q_idx = dhan.ohlc_data(securities={"IDX_I": [13, 21]})
    if not isinstance(q_idx, dict) or q_idx.get("status") != "success":
        print(f"[!] Failed to fetch Spot/VIX OHLC: {q_idx}")
        sys.exit(1)
    q_outer = q_idx.get("data", {})
    idx_data = (q_outer.get("data", {}) if isinstance(q_outer, dict) else {}).get("IDX_I", {})
    nifty = idx_data.get("13", {})
    vix = idx_data.get("21", {})

    spot = float(nifty.get("last_price", 0) or 0)
    ohlc = nifty.get("ohlc", {})
    vix_ltp = float(vix.get("last_price", 0) or 0)

    print("=" * 94)
    print(f"NIFTY 50 LIVE PULSE | {now_ist.strftime('%d-%b-%Y %H:%M:%S IST')}")
    print("=" * 94)
    print(
        f"NIFTY Spot : {spot:,.2f}  "
        f"(O: {ohlc.get('open', 0):,.2f} | H: {ohlc.get('high', 0):,.2f} | "
        f"L: {ohlc.get('low', 0):,.2f} | PrevC: {ohlc.get('close', 0):,.2f})"
    )
    print(f"India VIX  : {vix_ltp:.2f}  [{_vix_regime(vix_ltp)}]")

    # 2. NIFTY Front-Month Futures Quote + Session VWAP
    fut = resolve_nifty_front_future()
    fut_vwap = 0.0
    fut_ltp = 0.0
    fut_series = []
    fut_intra = {}

    if fut:
        fut_secid = fut["security_id"]
        try:
            q_fut = dhan.quote_data(securities={"NSE_FNO": [int(fut_secid)]})
            fut_quote = q_fut.get("data", {}).get("data", {}).get("NSE_FNO", {}).get(fut_secid, {})
            fut_ltp = float(fut_quote.get("last_price", 0) or 0)
            fut_atp = float(fut_quote.get("average_price", 0) or 0)
        except Exception:
            fut_atp = 0.0

        try:
            fut_intra_resp = dhan.intraday_minute_data(
                security_id=fut_secid,
                exchange_segment="NSE_FNO",
                instrument_type="FUTIDX",
                from_date=today_str,
                to_date=today_str,
                interval=5,
                oi=True,
            )
            if fut_intra_resp.get("status") == "success":
                fut_intra = fut_intra_resp.get("data", {})
                f_vols = fut_intra.get("volume", [])
                if fut_intra.get("timestamp") and f_vols:
                    fut_series, fut_vwap = compute_session_vwap(
                        fut_intra.get("high", []),
                        fut_intra.get("low", []),
                        fut_intra.get("close", []),
                        f_vols,
                    )
                    if fut_ltp == 0 and fut_intra.get("close"):
                        fut_ltp = float(fut_intra["close"][-1])
        except Exception as e:
            print(f"[!] Futures intraday fetch warning: {e}")

        active_vwap = fut_vwap or fut_atp
        basis = fut_ltp - spot if (fut_ltp and spot) else 0.0
        vwap_diff = fut_ltp - active_vwap if (fut_ltp and active_vwap) else 0.0
        vwap_bias = "ABOVE VWAP (Bullish Structure)" if vwap_diff > 0 else "BELOW VWAP (Bearish Structure)"
        print(
            f"NIFTY Fut  : {fut_ltp:,.2f} ({fut['trading_symbol']}) | "
            f"Basis: {basis:+.2f} | VWAP(hlc3): {fut_vwap:,.2f} | ATP: {fut_atp:,.2f} -> {vwap_bias} ({vwap_diff:+.2f})"
        )
    else:
        print("[!] NIFTY Front Future could not be resolved; VWAP unavailable.")

    # 3. Today's 5-min Spot (and Futures) intraday candles
    intra = dhan.intraday_minute_data(
        security_id="13",
        exchange_segment="IDX_I",
        instrument_type="INDEX",
        from_date=today_str,
        to_date=today_str,
        interval=5,
    )
    if intra.get("status") == "success":
        idata = intra.get("data", {})
        ts_list = idata.get("timestamp", [])
        opens = idata.get("open", [])
        highs = idata.get("high", [])
        lows = idata.get("low", [])
        closes = idata.get("close", [])
        if ts_list:
            print(f"\nRecent 5-Min Spot Candles (Last 6 bars of {len(ts_list)} total):")
            f_closes = fut_intra.get("close", [])
            f_vols = fut_intra.get("volume", [])
            for i in range(max(0, len(ts_list) - 6), len(ts_list)):
                dt_str = dt.datetime.fromtimestamp(ts_list[i], tz=IST_OFFSET).strftime("%H:%M")
                fut_info = ""
                if i < len(f_closes) and i < len(fut_series):
                    vol_val = int(f_vols[i]) if i < len(f_vols) else 0
                    fut_info = f" | FutC={f_closes[i]:.2f} VWAP={fut_series[i]:.2f} Vol={vol_val:,}"
                print(f"  [{dt_str}] O={opens[i]:.2f} H={highs[i]:.2f} L={lows[i]:.2f} C={closes[i]:.2f}{fut_info}")

    # 4. Expiry & Option Chain (retry once on Dhan's 3s rate limit)
    dates = get_nifty_expiry_list()
    expiry = dates[0] if dates else "2026-12-01"

    chain = dhan.option_chain(13, "IDX_I", expiry)
    data = unwrap_option_chain_data(chain)
    oc = data.get("oc", {})
    if not oc:
        time.sleep(3.1)
        chain = dhan.option_chain(13, "IDX_I", expiry)
        data = unwrap_option_chain_data(chain)
        oc = data.get("oc", {})
    if not oc:
        print(f"\n[!] Option Chain unavailable for {expiry}: {chain.get('remarks', chain)}")
        return

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
    pcr_tag = "BULLISH (>1.25)" if pcr > 1.25 else ("BEARISH (<0.75)" if pcr < 0.75 else "NEUTRAL/CHOP (0.75-1.25)")
    print(f"\nExpiry: {expiry} | Total CE OI: {total_ce_oi:,} | Total PE OI: {total_pe_oi:,} | PCR: {pcr} [{pcr_tag}]")

    top_ce = sorted(all_strikes, key=lambda x: x[1].get("oi", 0), reverse=True)[:3]
    top_pe = sorted(all_strikes, key=lambda x: x[2].get("oi", 0), reverse=True)[:3]
    print("Top Call Resistance Walls : " + " | ".join([f"{int(s)} ({c.get('oi', 0):,})" for s, c, _ in top_ce]))
    print("Top Put Support Floors    : " + " | ".join([f"{int(s)} ({p.get('oi', 0):,})" for s, _, p in top_pe]))

    print(f"\n{'Strike':>7} | {'CE LTP':>7} | {'CE Δ':>6} | {'CE IV':>5} | {'CE OI':>11} | {'PE LTP':>7} | {'PE Δ':>6} | {'PE IV':>5} | {'PE OI':>11}")
    print("-" * 94)
    for s, ce, pe in sorted(all_strikes, key=lambda x: x[0]):
        if abs(s - spot) <= 450:
            cg = ce.get("greeks", {})
            pg = pe.get("greeks", {})
            mark = " <-- ATM" if abs(s - spot) < 25 else ""
            print(
                f"{int(s):7d} | {ce.get('last_price', 0):7.2f} | {cg.get('delta', 0):6.2f} | "
                f"{ce.get('implied_volatility', 0):5.1f} | {ce.get('oi', 0):11,d} | "
                f"{pe.get('last_price', 0):7.2f} | {pg.get('delta', 0):6.2f} | "
                f"{pe.get('implied_volatility', 0):5.1f} | {pe.get('oi', 0):11,d}{mark}"
            )


if __name__ == "__main__":
    get_pulse()
