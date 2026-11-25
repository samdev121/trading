"""
Live MTM Monitor for Active Paper Trades (#1 Iron Condor & #2 Intraday Straddle).
Checks live DhanHQ API quotes and triggers SL / Target alerts.
"""
import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, "dhan_config.env"))

from dhanhq import dhanhq as DhanHQ, DhanContext

ctx = DhanContext(os.getenv("DHAN_CLIENT_ID"), os.getenv("DHAN_ACCESS_TOKEN"))
dhan = DhanHQ(ctx)


def check_trades():
    # Spot & VIX
    q_idx = dhan.ohlc_data(securities={"IDX_I": [13, 21]})
    idx_data = q_idx.get("data", {}).get("data", {}).get("IDX_I", {})
    spot = idx_data.get("13", {}).get("last_price", 0)
    vix = idx_data.get("21", {}).get("last_price", 0)

    # Option Chain 2026-12-01
    chain = dhan.option_chain(13, "IDX_I", "2026-12-01")
    raw = chain.get("data", {})
    if isinstance(raw, str):
        raw = json.loads(raw)
    data = raw.get("data", raw) if isinstance(raw, dict) else raw
    if isinstance(data, str):
        data = json.loads(data)
    oc = data.get("oc", {})

    def ltp(strike, side):
        return float(oc.get(f"{strike:.6f}", {}).get(side, {}).get("last_price", 0))

    # --- PAPER TRADE #1: Iron Condor (6 Lots = 390 Qty) ---
    ce_short = ltp(26600, "ce")
    ce_long = ltp(26800, "ce")
    pe_short = ltp(25200, "pe")
    pe_long = ltp(25000, "pe")

    ic_entry = 36.70
    ic_cur = (ce_short - ce_long) + (pe_short - pe_long)
    ic_pts = ic_entry - ic_cur
    ic_pnl = ic_pts * 390

    # --- PAPER TRADE #2: Intraday Straddle (2 Lots = 130 Qty) - CLOSED ---
    # 25950 PE hit 25% SL at 12:31 IST (Closed @ 276.25 = -7,182.50 realized)
    # 25950 CE hit Trailed Profit SL at 13:29:37 IST (Closed @ 155.45 = +12,935.00 realized)
    st_total_pnl = 5752.50

    now_str = datetime.now().strftime("%H:%M:%S IST")
    print(f"=== LIVE PAPER MTM [{now_str}] | Spot: {spot:,.2f} | VIX: {vix:.2f} ===")
    print(f"[Trade #1 Iron Condor | 390 Qty] Entry: 36.70 | Current: {ic_cur:.2f} | MTM: {ic_pnl:+,.2f} ({ic_pts:+.2f} pts)")
    if ic_cur <= 7.30:
        print("  >>> ALERT: TRADE #1 TARGET HIT (<= 7.30)! BOOK PROFIT!")
    elif ic_pnl <= -14300:
        print("  >>> ALERT: TRADE #1 HARD SL HIT (<= -14,300)! EXIT NOW!")

    print(f"[Trade #2 Straddle 25950 | 130 Qty] CLOSED | CE @ 155.45 (+12,935.00) | PE @ 276.25 (-7,182.50) | Realized Gross: +5,752.50 (Net: +5,545.50)")
    print(f"Total Paper Portfolio MTM: {ic_pnl + st_total_pnl:+,.2f}")

    alert = (
        ic_cur <= 7.30
        or ic_pnl <= -14300
        or datetime.now().strftime("%H:%M") >= "15:15"
    )
    return alert


def watch_loop():
    """Zero-token silent background loop. Polls every 30s; exits immediately on alert or 15:15 IST."""
    log_path = os.path.join(CURRENT_DIR, "paper_mtm_live.txt")
    while True:
        try:
            # Capture check_trades output to log file
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                alert = check_trades()
            out = buf.getvalue()
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(out)
            if alert:
                print(out, flush=True)
                break
        except Exception as e:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"Error at {datetime.now()}: {e}\n")
        time.sleep(30)


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch_loop()
    else:
        check_trades()
