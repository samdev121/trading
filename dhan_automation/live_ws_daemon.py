"""
╔══════════════════════════════════════════════════════════════╗
║       LIVE WEBSOCKET DAEMON — IMLT FRAMEWORK                 ║
║       Trader: shakhan32  |  System: DhanHQ MarketFeed v2     ║
║       Runs: 09:15 AM -> 15:30 PM IST (auto-stops)            ║
╚══════════════════════════════════════════════════════════════╝

Architecture:
  - WebSocket persistent connection to wss://api-feed.dhan.co
  - Streams: NIFTY Spot + NIFTY Front Futures (ATP/VWAP) + ATM CE + ATM PE
  - Builds 5-min OHLC candles in memory
  - On candle CLOSE (after 09:30 IST freeze) -> runs IMLT setup detection rules
  - Writes live_pulse.json (throttled to <=1/sec) & alert.json on setup trigger
  - Watchdog thread enforces 15:30 IST stop, 15-min ATM-shift check, stale-tick check
"""

import datetime
import json
import os
import sys
import threading
import time
import traceback
from pathlib import Path
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

ENV_PATH = CURRENT_DIR / "dhan_config.env"
PULSE_FILE = CURRENT_DIR / "live_pulse.json"
ALERT_FILE = CURRENT_DIR / "alert.json"
CANDLE_FILE = CURRENT_DIR / "candles.json"
LOG_FILE = CURRENT_DIR / "daemon.log"

load_dotenv(ENV_PATH)

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

try:
    from dhanhq import DhanContext, MarketFeed, dhanhq
except ImportError:
    print("[FATAL] dhanhq not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

from dhan_engine import (
    IST_OFFSET,
    compute_session_vwap,
    resolve_nifty_front_future,
    unwrap_expiry_dates,
    unwrap_option_chain_data,
)


def now_ist():
    return datetime.datetime.now(IST_OFFSET)


def ist_time(h, m):
    t = now_ist()
    return t.replace(hour=h, minute=m, second=0, microsecond=0)


def log(msg):
    ts = now_ist().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class CandleBuilder:
    """Builds 5-minute OHLC candles from tick stream."""

    def __init__(self, interval_minutes=5):
        self.interval = interval_minutes
        self.candles = {}
        self.current = {}

    def _candle_start(self, ts: datetime.datetime) -> datetime.datetime:
        total_minutes = ts.hour * 60 + ts.minute
        floored = (total_minutes // self.interval) * self.interval
        return ts.replace(hour=floored // 60, minute=floored % 60, second=0, microsecond=0)

    def feed(self, symbol: str, ltp: float, ts: datetime.datetime):
        """Feed a tick. Returns closed candle dict if a new candle just opened, else None."""
        if ltp <= 0:
            return None
        candle_ts = self._candle_start(ts)

        if symbol not in self.current:
            self.current[symbol] = {"ts": candle_ts, "o": ltp, "h": ltp, "l": ltp, "c": ltp, "ticks": 1}
            self.candles.setdefault(symbol, [])
            return None

        cur = self.current[symbol]
        if candle_ts > cur["ts"]:
            closed = dict(cur)
            closed["close_ts"] = candle_ts.strftime("%H:%M")
            self.candles[symbol].append(closed)
            self.candles[symbol] = self.candles[symbol][-40:]
            self.current[symbol] = {"ts": candle_ts, "o": ltp, "h": ltp, "l": ltp, "c": ltp, "ticks": 1}
            return closed

        cur["h"] = max(cur["h"], ltp)
        cur["l"] = min(cur["l"], ltp)
        cur["c"] = ltp
        cur["ticks"] += 1
        return None

    def last_candle(self, symbol):
        candles = self.candles.get(symbol, [])
        return candles[-1] if candles else None

    def current_candle(self, symbol):
        return self.current.get(symbol)


class IMTLSetupDetector:
    """
    Checks IMLT setup conditions on each 5-min candle close.
    Enforces the 09:15-09:30 AM Opening Discovery Freeze, VWAP alignment, and PCR checks.
    """

    def __init__(self):
        self.alerts_fired = set()

    def check(
        self,
        ts: datetime.datetime,
        spot_candles: list,
        fut_candles: list,
        fut_vwap: float,
        fut_ltp: float,
        ce_oi: int,
        pe_oi: int,
        ce_oi_delta: int,
        pe_oi_delta: int,
        spot_ltp: float,
        atm_ce_ltp: float,
        atm_pe_ltp: float,
        atm_strike: int,
    ):
        alerts = []
        now = ts.strftime("%H:%M")

        # Strict 09:15 - 09:30 AM Opening Discovery Freeze
        if ts.hour < 9 or (ts.hour == 9 and ts.minute < 30):
            return alerts

        if len(spot_candles) < 3:
            return alerts

        c1 = spot_candles[-3]
        c2 = spot_candles[-2]
        c_last = spot_candles[-1]
        pcr = round(pe_oi / ce_oi, 2) if ce_oi > 0 else 0.0

        above_vwap = (fut_ltp > fut_vwap) if (fut_ltp > 0 and fut_vwap > 0) else None
        below_vwap = (fut_ltp < fut_vwap) if (fut_ltp > 0 and fut_vwap > 0) else None
        vwap_label = f"Fut={fut_ltp:.1f} vs VWAP={fut_vwap:.1f}" if fut_vwap > 0 else "VWAP=N/A"

        # ── Setup 1: Bullish Breakout & VWAP Bounce / ORB High Break ───────────
        orb_high = spot_candles[0]["h"]
        orb_low = spot_candles[0]["l"]
        bull_candle = c_last["c"] > c_last["o"]
        bear_candle = c_last["c"] < c_last["o"]

        if c_last["c"] > orb_high and bull_candle and pcr >= 1.0 and (above_vwap is not False):
            key = f"SETUP1_BULL_{now}"
            if key not in self.alerts_fired:
                self.alerts_fired.add(key)
                alerts.append({
                    "setup": "Setup 1: Bullish ORB / VWAP Trend Breakout",
                    "direction": "LONG (Buy 1 Lot = 65 Qty)",
                    "strike_suggest": f"{int(atm_strike)} CE",
                    "entry_zone": f"₹{atm_ce_ltp:.1f}",
                    "trigger": f"5m Spot closed {c_last['c']:.1f} > ORB High {orb_high:.1f} ({vwap_label})",
                    "pcr_bias": f"PCR {pcr} (Bullish Put Support)",
                })

        # ── Setup 2: Bearish Breakdown & VWAP Rejection ────────────────────────
        # Price rallies toward/tests VWAP or ORB Low, prints upper wick & closes red below
        fut_last = fut_candles[-1] if fut_candles else None
        vwap_reject = (
            fut_last is not None
            and fut_vwap > 0
            and fut_last["h"] >= fut_vwap - 5
            and fut_last["c"] < fut_vwap
            and fut_last["c"] < fut_last["o"]
        )
        if (vwap_reject or c_last["c"] < orb_low) and bear_candle and pcr <= 1.0 and (below_vwap is not False):
            key = f"SETUP2_BEAR_{now}"
            if key not in self.alerts_fired:
                self.alerts_fired.add(key)
                alerts.append({
                    "setup": "Setup 2: Bearish VWAP Rejection / Breakdown",
                    "direction": "SHORT (Buy PE | 1 Lot = 65 Qty)",
                    "strike_suggest": f"{int(atm_strike)} PE",
                    "entry_zone": f"₹{atm_pe_ltp:.1f}",
                    "trigger": f"5m close {c_last['c']:.1f} below ORB/VWAP ({vwap_label})",
                    "pcr_bias": f"PCR {pcr} (Bearish Call Resistance)",
                })

        # ── Setup 3: Liquidity Sweep & Fakeout Reversal ────────────────────────
        # 3A Bull Trap (wick > prior high, closes red back below prior high)
        if c_last["h"] > c2["h"] and c_last["c"] < c2["h"] and bear_candle:
            key = f"SETUP3_BULL_TRAP_{now}"
            if key not in self.alerts_fired:
                self.alerts_fired.add(key)
                alerts.append({
                    "setup": "Setup 3A: Liquidity Sweep Bull Trap",
                    "direction": "SHORT (Buy PE | 1 Lot = 65 Qty)",
                    "strike_suggest": f"{int(atm_strike)} PE",
                    "entry_zone": f"₹{atm_pe_ltp:.1f}",
                    "trigger": f"Swept {c2['h']:.1f} (H={c_last['h']:.1f}) and closed back inside @ {c_last['c']:.1f}",
                    "pcr_bias": f"PCR {pcr} | {vwap_label}",
                })
        # 3B Bear Trap (wick < prior low, closes green back above prior low)
        elif c_last["l"] < c2["l"] and c_last["c"] > c2["l"] and bull_candle:
            key = f"SETUP3_BEAR_TRAP_{now}"
            if key not in self.alerts_fired:
                self.alerts_fired.add(key)
                alerts.append({
                    "setup": "Setup 3B: Liquidity Sweep Bear Trap",
                    "direction": "LONG (Buy CE | 1 Lot = 65 Qty)",
                    "strike_suggest": f"{int(atm_strike)} CE",
                    "entry_zone": f"₹{atm_ce_ltp:.1f}",
                    "trigger": f"Swept {c2['l']:.1f} (L={c_last['l']:.1f}) and closed back inside @ {c_last['c']:.1f}",
                    "pcr_bias": f"PCR {pcr} | {vwap_label}",
                })

        # ── Setup 4: Institutional Short-Covering Blast ────────────────────────
        # Strong breakout above recent 2-candle ceiling with Call OI unwinding (or strong above-VWAP surge)
        recent_high = max(c1["h"], c2["h"])
        if (
            c_last["c"] > recent_high
            and bull_candle
            and (above_vwap is True or fut_vwap == 0)
            and (ce_oi_delta < 0 or c_last["c"] > c2["c"] * 1.001)
        ):
            key = f"SETUP4_SC_BLAST_{now}"
            if key not in self.alerts_fired:
                self.alerts_fired.add(key)
                alerts.append({
                    "setup": "Setup 4: Short-Covering Blast ⚡",
                    "direction": "LONG (Buy CE | 1 Lot = 65 Qty)",
                    "strike_suggest": f"{int(atm_strike)} CE",
                    "entry_zone": f"₹{atm_ce_ltp:.1f}",
                    "trigger": f"5m closed {c_last['c']:.1f} > {recent_high:.1f} (ΔCE_OI={ce_oi_delta:+,} | {vwap_label})",
                    "pcr_bias": f"PCR {pcr}",
                })

        # ── Setup 5: Consolidation Floor Breakdown Cascade ─────────────────────
        recent_low = min(c1["l"], c2["l"])
        if c_last["c"] < recent_low and bear_candle and (below_vwap is True or fut_vwap == 0):
            key = f"SETUP5_FLOOR_BREAK_{now}"
            if key not in self.alerts_fired:
                self.alerts_fired.add(key)
                alerts.append({
                    "setup": "Setup 5: Floor Breakdown Cascade",
                    "direction": "SHORT (Buy PE | 1 Lot = 65 Qty)",
                    "strike_suggest": f"{int(atm_strike)} PE",
                    "entry_zone": f"₹{atm_pe_ltp:.1f}",
                    "trigger": f"5m closed {c_last['c']:.1f} < floor {recent_low:.1f} ({vwap_label})",
                    "pcr_bias": f"PCR {pcr}",
                })

        return alerts


state = {
    "spot_ltp": 0.0,
    "fut_ltp": 0.0,
    "fut_vwap": 0.0,
    "fut_atp": 0.0,
    "fut_secid": None,
    "fut_symbol": None,
    "atm_strike": 0,
    "atm_ce_ltp": 0.0,
    "atm_pe_ltp": 0.0,
    "atm_ce_secid": None,
    "atm_pe_secid": None,
    "ce_oi": 0,
    "pe_oi": 0,
    "prev_ce_oi": 0,
    "prev_pe_oi": 0,
    "last_tick_ts": None,
    "session_pnl": 0.0,
    "active_trade": None,
    "connected": False,
    "expiry": None,
}

candle_builder = CandleBuilder(interval_minutes=5)
detector = IMTLSetupDetector()
lock = threading.Lock()
_last_pulse_write = 0.0


def write_pulse(force=False):
    """Writes latest state to live_pulse.json (throttled to <=1 write/sec unless forced)."""
    global _last_pulse_write
    now_mono = time.monotonic()
    if not force and (now_mono - _last_pulse_write) < 1.0:
        return
    _last_pulse_write = now_mono

    with lock:
        s = dict(state)
    ts = now_ist().strftime("%Y-%m-%d %H:%M:%S IST")
    active_vwap = s["fut_vwap"] or s["fut_atp"]
    basis = round(s["fut_ltp"] - s["spot_ltp"], 2) if (s["fut_ltp"] and s["spot_ltp"]) else 0.0
    pulse = {
        "ts": ts,
        "spot_ltp": s["spot_ltp"],
        "fut_symbol": s["fut_symbol"],
        "fut_ltp": s["fut_ltp"],
        "fut_vwap": active_vwap,
        "fut_atp": s["fut_atp"],
        "basis": basis,
        "atm_strike": s["atm_strike"],
        "atm_ce_ltp": s["atm_ce_ltp"],
        "atm_pe_ltp": s["atm_pe_ltp"],
        "ce_oi": s["ce_oi"],
        "pe_oi": s["pe_oi"],
        "ce_oi_delta": s["ce_oi"] - s["prev_ce_oi"],
        "pe_oi_delta": s["pe_oi"] - s["prev_pe_oi"],
        "pcr": round(s["pe_oi"] / s["ce_oi"], 2) if s["ce_oi"] > 0 else 0,
        "expiry": s["expiry"],
        "connected": s["connected"],
        "active_trade": s["active_trade"],
        "spot_candle": candle_builder.current_candle("SPOT"),
        "last_closed_candle": candle_builder.last_candle("SPOT"),
        "fut_candle": candle_builder.current_candle("FUT"),
    }
    try:
        PULSE_FILE.write_text(json.dumps(pulse, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        log(f"[!] Pulse write error: {e}")


def write_alert(alert: dict):
    """Writes setup alert to alert.json."""
    alerts = []
    if ALERT_FILE.exists():
        try:
            alerts = json.loads(ALERT_FILE.read_text(encoding="utf-8"))
        except Exception:
            alerts = []
    alert["ts"] = now_ist().strftime("%H:%M:%S IST")
    alerts.append(alert)
    ALERT_FILE.write_text(json.dumps(alerts, indent=2, default=str), encoding="utf-8")


def save_candles():
    """Saves candle history to candles.json."""
    try:
        data = {
            sym: [
                {**c, "ts": c["ts"].strftime("%H:%M") if hasattr(c["ts"], "strftime") else str(c["ts"])}
                for c in candles
            ]
            for sym, candles in candle_builder.candles.items()
        }
        CANDLE_FILE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        log(f"[!] Candle save error: {e}")


def resolve_atm_strikes():
    """Resolves ATM CE/PE security IDs via REST option_chain."""
    log("[*] Resolving ATM strikes via REST option_chain...")
    try:
        ctx = DhanContext(CLIENT_ID, ACCESS_TOKEN)
        dhan = dhanhq(ctx)

        dates = unwrap_expiry_dates(dhan.expiry_list(13, "IDX_I"))
        if not dates:
            log("[!] Could not fetch expiry_list from Dhan API.")
            return None
        expiry = dates[0]
        log(f"[*] Using expiry: {expiry}")

        chain_resp = dhan.option_chain(13, "IDX_I", expiry)
        data = unwrap_option_chain_data(chain_resp)
        spot = float(data.get("last_price", 0))
        oc = data.get("oc", {})

        atm = round(spot / 50) * 50
        log(f"[*] Spot: {spot:.2f} -> ATM Strike: {atm}")

        for s in [atm, atm - 50, atm + 50, atm - 100, atm + 100]:
            key = f"{float(s):.6f}"
            info = oc.get(key) or oc.get(str(int(s)))
            if info:
                ce = info.get("ce", {})
                pe = info.get("pe", {})
                ce_secid = str(ce.get("security_id", ""))
                pe_secid = str(pe.get("security_id", ""))
                if ce_secid and pe_secid:
                    log(f"[OK] ATM={s} | CE SecID={ce_secid} LTP={ce.get('last_price')} OI={ce.get('oi', 0):,}")
                    log(f"[OK] ATM={s} | PE SecID={pe_secid} LTP={pe.get('last_price')} OI={pe.get('oi', 0):,}")
                    return (
                        int(s),
                        ce_secid,
                        pe_secid,
                        expiry,
                        float(ce.get("last_price", 0)),
                        float(pe.get("last_price", 0)),
                        int(ce.get("oi", 0)),
                        int(pe.get("oi", 0)),
                        spot,
                    )

        log("[!] ATM strike not found in option chain keys. Check API response.")
        return None

    except Exception as e:
        log(f"[FATAL] resolve_atm_strikes failed: {e}")
        traceback.print_exc()
        return None


def seed_today_futures_vwap(fut_secid: str):
    """Seeds today's 5-min Futures VWAP from intraday_minute_data if daemon starts mid-session."""
    try:
        ctx = DhanContext(CLIENT_ID, ACCESS_TOKEN)
        dhan = dhanhq(ctx)
        today_str = now_ist().strftime("%Y-%m-%d")
        resp = dhan.intraday_minute_data(
            security_id=fut_secid,
            exchange_segment="NSE_FNO",
            instrument_type="FUTIDX",
            from_date=today_str,
            to_date=today_str,
            interval=5,
            oi=False,
        )
        if resp.get("status") == "success":
            idata = resp.get("data", {})
            if idata.get("timestamp") and idata.get("volume"):
                _, latest_vwap = compute_session_vwap(
                    idata.get("high", []),
                    idata.get("low", []),
                    idata.get("close", []),
                    idata.get("volume", []),
                )
                with lock:
                    state["fut_vwap"] = latest_vwap
                    if idata.get("close"):
                        state["fut_ltp"] = float(idata["close"][-1])
                log(f"[OK] Seeded Futures Session VWAP(hlc3): {latest_vwap:.2f}")
    except Exception as e:
        log(f"[!] Could not seed Futures VWAP: {e}")


def on_tick(*args):
    """
    Called by MarketFeed on every incoming packet.
    Supports both (feed, data) in dhanhq>=2.2 and (data,) signatures.
    """
    data = args[-1] if args else None
    if not isinstance(data, dict):
        return

    try:
        secid = str(data.get("security_id", ""))
        ltp = float(data.get("LTP", 0) or data.get("last_price", 0) or 0)
        oi = int(data.get("OI", 0) or data.get("oi", 0) or 0)
        atp = float(data.get("avg_price", 0) or 0)
        ts = now_ist()
        closed_spot = None

        with lock:
            if secid == "13":
                if ltp > 0:
                    state["spot_ltp"] = ltp
                    state["last_tick_ts"] = ts
                    closed_spot = candle_builder.feed("SPOT", ltp, ts)

            elif state["fut_secid"] and secid == state["fut_secid"]:
                state["last_tick_ts"] = ts
                if ltp > 0:
                    state["fut_ltp"] = ltp
                    candle_builder.feed("FUT", ltp, ts)
                if atp > 0:
                    state["fut_atp"] = atp
                    state["fut_vwap"] = atp

            elif secid == state["atm_ce_secid"]:
                if ltp > 0:
                    state["atm_ce_ltp"] = ltp
                    candle_builder.feed("CE", ltp, ts)
                if oi > 0:
                    state["prev_ce_oi"] = state["ce_oi"]
                    state["ce_oi"] = oi

            elif secid == state["atm_pe_secid"]:
                if ltp > 0:
                    state["atm_pe_ltp"] = ltp
                    candle_builder.feed("PE", ltp, ts)
                if oi > 0:
                    state["prev_pe_oi"] = state["pe_oi"]
                    state["pe_oi"] = oi

        if closed_spot:
            _on_candle_close(closed_spot, ts)
            write_pulse(force=True)
        else:
            write_pulse(force=False)

    except Exception as e:
        log(f"[!] Tick handler error: {e} | raw={data}")


def _on_candle_close(closed_candle, ts):
    """Called when a 5-min SPOT candle closes. Runs IMLT setup detection."""
    ctime = ts.strftime("%H:%M")
    log(
        f"🕯️  CANDLE CLOSE [{ctime}] O={closed_candle['o']:.0f} H={closed_candle['h']:.0f} "
        f"L={closed_candle['l']:.0f} C={closed_candle['c']:.0f}"
    )
    save_candles()

    with lock:
        s = dict(state)
    spot_candles = list(candle_builder.candles.get("SPOT", []))
    fut_candles = list(candle_builder.candles.get("FUT", []))
    active_vwap = s["fut_vwap"] or s["fut_atp"]
    ce_delta = s["ce_oi"] - s["prev_ce_oi"]
    pe_delta = s["pe_oi"] - s["prev_pe_oi"]

    alerts = detector.check(
        ts=ts,
        spot_candles=spot_candles,
        fut_candles=fut_candles,
        fut_vwap=active_vwap,
        fut_ltp=s["fut_ltp"],
        ce_oi=s["ce_oi"],
        pe_oi=s["pe_oi"],
        ce_oi_delta=ce_delta,
        pe_oi_delta=pe_delta,
        spot_ltp=s["spot_ltp"],
        atm_ce_ltp=s["atm_ce_ltp"],
        atm_pe_ltp=s["atm_pe_ltp"],
        atm_strike=s["atm_strike"],
    )

    for alert in alerts:
        log(f"\n{'=' * 55}")
        log(f"🚨 SETUP ALERT: {alert['setup']}")
        log(f"   Direction  : {alert['direction']}")
        log(f"   Strike     : {alert['strike_suggest']}")
        log(f"   Entry Zone : {alert.get('entry_zone', 'N/A')}")
        log(f"   Trigger    : {alert['trigger']}")
        if "pcr_bias" in alert:
            log(f"   PCR / Bias : {alert['pcr_bias']}")
        log(f"{'=' * 55}\n")
        write_alert(alert)

    pcr = round(s["pe_oi"] / s["ce_oi"], 2) if s["ce_oi"] > 0 else 0
    log(
        f"📊 PULSE [{ctime}] Spot={s['spot_ltp']:.2f} | Fut={s['fut_ltp']:.2f} (VWAP={active_vwap:.2f}) | "
        f"CE={s['atm_ce_ltp']:.1f}(ΔOI={ce_delta:+,}) | "
        f"PE={s['atm_pe_ltp']:.1f}(ΔOI={pe_delta:+,}) | PCR={pcr}"
    )


def maybe_resubscribe(ts):
    """Every 15 minutes, checks if ATM has shifted by >= 50 pts."""
    with lock:
        spot = state["spot_ltp"]
        cur_atm = state["atm_strike"]

    if spot <= 0:
        return
    new_atm = round(spot / 50) * 50
    if new_atm != cur_atm and abs(new_atm - cur_atm) >= 50:
        log(f"⚠️  ATM SHIFTED: {cur_atm} -> {new_atm} | Spot={spot:.2f}")
        log("   ACTION NEEDED: Restart daemon to resubscribe to new ATM strikes.")
        log(f"   New CE/PE to watch: {new_atm} CE / {new_atm} PE")
        write_alert({
            "setup": "ATM SHIFT ALERT",
            "direction": "RESUBSCRIBE",
            "trigger": f"ATM moved from {cur_atm} to {new_atm}. Restart daemon.",
            "spot": spot,
        })


def run_daemon():
    log("=" * 55)
    log("  IMLT LIVE WS DAEMON STARTING")
    log(f"  Client: {CLIENT_ID[:4]}****{CLIENT_ID[-2:]}")
    log("=" * 55)

    result = resolve_atm_strikes()
    if not result:
        log("[FATAL] Could not resolve ATM. Exiting.")
        sys.exit(1)

    atm, ce_secid, pe_secid, expiry, ce_ltp, pe_ltp, ce_oi, pe_oi, spot = result
    fut = resolve_nifty_front_future()

    with lock:
        state["spot_ltp"] = spot
        state["atm_strike"] = atm
        state["atm_ce_secid"] = ce_secid
        state["atm_pe_secid"] = pe_secid
        state["expiry"] = expiry
        state["atm_ce_ltp"] = ce_ltp
        state["atm_pe_ltp"] = pe_ltp
        state["ce_oi"] = ce_oi
        state["pe_oi"] = pe_oi
        state["prev_ce_oi"] = ce_oi
        state["prev_pe_oi"] = pe_oi
        if fut:
            state["fut_secid"] = fut["security_id"]
            state["fut_symbol"] = fut["trading_symbol"]

    instruments = [
        (MarketFeed.IDX, "13", MarketFeed.Ticker),
        (MarketFeed.NSE_FNO, ce_secid, MarketFeed.Full),
        (MarketFeed.NSE_FNO, pe_secid, MarketFeed.Full),
    ]
    if fut:
        seed_today_futures_vwap(fut["security_id"])
        instruments.append((MarketFeed.NSE_FNO, fut["security_id"], MarketFeed.Full))

    log("[*] Subscribing to:")
    log("    NIFTY Spot  -> SecID=13 (IDX_I)")
    if fut:
        log(f"    {fut['trading_symbol']} -> SecID={fut['security_id']} (NSE_FNO Full/VWAP)")
    log(f"    {atm} CE     -> SecID={ce_secid} (NSE_FNO Full)")
    log(f"    {atm} PE     -> SecID={pe_secid} (NSE_FNO Full)")
    log(f"    Expiry: {expiry}")

    ctx = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    market_end = ist_time(15, 30)
    next_atm_check = now_ist() + datetime.timedelta(minutes=15)
    stop_event = threading.Event()
    feed = None

    log("[*] Connecting to DhanHQ MarketFeed WebSocket...")
    log("[*] Waiting for ticks... (Ctrl+C to stop)\n")

    try:
        feed = MarketFeed(ctx, instruments, version="v2", on_message=on_tick)
        with lock:
            state["connected"] = True

        log("[OK] WebSocket INITIALIZED ✅")
        log(f"[*] Session runs until {market_end.strftime('%H:%M')} IST\n")
        write_pulse(force=True)

        def watchdog():
            nonlocal next_atm_check
            while not stop_event.wait(30):
                ts = now_ist()
                if ts >= market_end:
                    log("\n🔔 15:30 IST — Market closed. Daemon stopping.")
                    with lock:
                        state["connected"] = False
                    write_pulse(force=True)
                    try:
                        feed.close_connection()
                    except Exception:
                        pass
                    break

                if ts >= next_atm_check:
                    maybe_resubscribe(ts)
                    next_atm_check = ts + datetime.timedelta(minutes=15)

                with lock:
                    last = state["last_tick_ts"]
                if last and (ts - last).total_seconds() > 60:
                    log(f"⚠️  No tick for {int((ts - last).total_seconds())}s — possible disconnect")

        t = threading.Thread(target=watchdog, daemon=True)
        t.start()

        # Blocking event loop (runs until close_connection() or Ctrl+C)
        feed.run()

    except KeyboardInterrupt:
        log("\n[*] Stopped by user (Ctrl+C).")
    except Exception as e:
        log(f"[FATAL] WebSocket error: {e}")
        traceback.print_exc()
    finally:
        stop_event.set()
        if feed is not None:
            try:
                feed.close_connection()
            except Exception:
                pass
        with lock:
            state["connected"] = False
        write_pulse(force=True)
        log("[*] Daemon exited. Final pulse written.")


if __name__ == "__main__":
    if not CLIENT_ID or not ACCESS_TOKEN:
        print("[FATAL] Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN in dhan_config.env")
        sys.exit(1)

    run_daemon()
