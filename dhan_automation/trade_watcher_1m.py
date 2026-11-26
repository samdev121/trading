"""
Zero-token 1-minute background scanner for NEW Option Selling trade setups.
Polls DhanHQ every 60s; exits (and notifies agent) ONLY when a new setup triggers:
  1. #3 / #10 Bear Call Spread: Fut < VWAP, Spot < 25,800, PCR <= 0.90
  2. #2 / #10 Bull Put Spread: Fut > VWAP, Spot > 25,925, PCR >= 1.00
  3. 15:15 IST mandatory cutoff
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
load_dotenv(os.path.join(CURRENT_DIR, "dhan_config.env"))

from dhanhq import dhanhq as DhanHQ, DhanContext
from dhan_automation.dhan_engine import (
    unwrap_option_chain_data,
    compute_session_vwap,
    resolve_nifty_front_future,
)


def poll_once(dhan: DhanHQ, fut_secid: str) -> tuple[bool, str]:
    now_str = datetime.now().strftime("%H:%M:%S IST")
    if datetime.now().strftime("%H:%M") >= "15:15":
        return True, f"[{now_str}] 15:15 IST CUTOFF REACHED — Scanner stopped."

    q_idx = dhan.ohlc_data(securities={"IDX_I": [13, 21]})
    idx_data = (q_idx.get("data") or {}).get("data", {}).get("IDX_I", {})
    spot = float(idx_data.get("13", {}).get("last_price", 0))
    vix = float(idx_data.get("21", {}).get("last_price", 0))

    today_str = datetime.now().strftime("%Y-%m-%d")
    fut_close, fut_vwap = 0.0, 0.0
    if fut_secid:
        fut_resp = dhan.intraday_minute_data(
            security_id=fut_secid,
            exchange_segment="NSE_FNO",
            instrument_type="FUTIDX",
            from_date=today_str,
            to_date=today_str,
            interval=5,
            oi=True,
        )
        if fut_resp.get("status") == "success":
            fi = fut_resp.get("data", {})
            vols = fi.get("volume", [])
            if fi.get("timestamp") and vols:
                _, fut_vwap = compute_session_vwap(
                    fi.get("high", []),
                    fi.get("low", []),
                    fi.get("close", []),
                    vols,
                )
                if fi.get("close"):
                    fut_close = float(fi["close"][-1])

    chain = dhan.option_chain(13, "IDX_I", "2026-12-01")
    oc = unwrap_option_chain_data(chain)

    tot_ce = sum(float(v.get("ce", {}).get("oi", 0) or 0) for v in oc.values())
    tot_pe = sum(float(v.get("pe", {}).get("oi", 0) or 0) for v in oc.values())
    pcr = (tot_pe / tot_ce) if tot_ce > 0 else 0.0

    alerts = []
    if fut_vwap > 0 and fut_close < fut_vwap and spot < 25800 and 0 < pcr <= 0.90:
        alerts.append(
            f"NEW SETUP #3/#10 BEAR CALL SPREAD: Spot={spot:.2f} < 25,800 | "
            f"Fut={fut_close:.2f} < VWAP={fut_vwap:.2f} | PCR={pcr:.2f}"
        )
    if fut_vwap > 0 and fut_close > fut_vwap and spot > 25925 and pcr >= 1.00:
        alerts.append(
            f"NEW SETUP #2/#10 BULL PUT SPREAD: Spot={spot:.2f} > 25,925 | "
            f"Fut={fut_close:.2f} > VWAP={fut_vwap:.2f} | PCR={pcr:.2f}"
        )

    summary = f"[{now_str}] Spot={spot:.2f} | VIX={vix:.2f} | Fut={fut_close:.2f} | VWAP={fut_vwap:.2f} | PCR={pcr:.2f}"
    if alerts:
        return True, summary + "\n" + "\n".join(f">>> ALERT: {a}" for a in alerts)
    return False, summary


def main():
    ctx = DhanContext(os.getenv("DHAN_CLIENT_ID"), os.getenv("DHAN_ACCESS_TOKEN"))
    dhan = DhanHQ(ctx)
    fut = resolve_nifty_front_future()
    fut_secid = fut["security_id"] if fut else ""
    log_path = os.path.join(CURRENT_DIR, "watcher_1m_live.txt")

    while True:
        try:
            triggered, msg = poll_once(dhan, fut_secid)
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(msg + "\n")
            if triggered:
                print(msg, flush=True)
                break
        except Exception as e:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Watcher error: {e}\n")
        time.sleep(60)


if __name__ == "__main__":
    main()
