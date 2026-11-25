"""
DhanHQ Institutional Engine for NIFTY Options & Futures
Author: Co-Pilot for shakhan32
System: Institutional Momentum & Liquidity Trap (IMLT) Framework
Location: trading/dhan_automation/dhan_engine.py
"""

import csv
import datetime
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_DIR / "dhan_config.env"
FUT_CACHE_PATH = CURRENT_DIR / ".nifty_future_cache.json"
IST_OFFSET = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

try:
    from dhanhq import dhanhq, DhanContext
except ImportError:
    print("Error: dhanhq library not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)


def get_dhan_client():
    """Initializes and returns the authenticated DhanHQ client."""
    client_id = os.getenv("DHAN_CLIENT_ID")
    access_token = os.getenv("DHAN_ACCESS_TOKEN")

    if not client_id or not access_token:
        print(f"[!] Missing credentials in {ENV_PATH}")
        print("    Please ensure DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN are set.")
        return None

    ctx = DhanContext(client_id, access_token)
    return dhanhq(ctx)


def unwrap_option_chain_data(chain_resp):
    """Safely unwraps DhanHQ option_chain responses including double-encoded JSON strings."""
    if not isinstance(chain_resp, dict):
        return {}
    raw = chain_resp.get("data", {})
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return {}
    data = raw.get("data", raw) if isinstance(raw, dict) else {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return {}
    return data if isinstance(data, dict) else {}


def unwrap_expiry_dates(exp_resp):
    """Normalizes DhanHQ expiry_list responses into a flat list of date strings."""
    if isinstance(exp_resp, dict):
        dates = exp_resp.get("data", [])
    elif isinstance(exp_resp, list):
        dates = exp_resp
    else:
        return []

    if isinstance(dates, dict):
        dates = dates.get("data", list(dates.values()))
    if dates and isinstance(dates[0], list):
        dates = dates[0]
    return [str(d) for d in dates] if isinstance(dates, list) else []


def compute_session_vwap(highs, lows, closes, volumes):
    """
    Computes cumulative session VWAP using hlc3 typical price:
    sum(((H + L + C) / 3) * V) / sum(V).
    Returns (vwap_series, latest_vwap).
    """
    cum_pv = 0.0
    cum_vol = 0.0
    series = []
    for h, l, c, v in zip(highs, lows, closes, volumes):
        vol = float(v or 0)
        tp = (float(h) + float(l) + float(c)) / 3.0
        if vol > 0:
            cum_pv += tp * vol
            cum_vol += vol
        vwap = (cum_pv / cum_vol) if cum_vol > 0 else tp
        series.append(round(vwap, 2))
    return series, (series[-1] if series else 0.0)


def resolve_nifty_front_future(force_refresh=False):
    """
    Resolves the active front-month NIFTY FUTIDX security ID from Dhan's scrip master CSV.
    Caches the resolved contract locally for the current IST day.
    Returns dict {security_id, trading_symbol, expiry_date, lot_size} or None.
    """
    today_ist = datetime.datetime.now(IST_OFFSET).date()
    today_str = today_ist.strftime("%Y-%m-%d")

    if not force_refresh and FUT_CACHE_PATH.exists():
        try:
            cached = json.loads(FUT_CACHE_PATH.read_text(encoding="utf-8"))
            if cached.get("cached_date") == today_str and cached.get("expiry_date", "") >= today_str:
                return cached
        except Exception:
            pass

    try:
        resp = requests.get(dhanhq.COMPACT_CSV_URL, stream=True, timeout=20)
        resp.raise_for_status()
        lines = (line.decode("utf-8", "ignore") for line in resp.iter_lines())
        reader = csv.DictReader(lines)

        candidates = []
        for row in reader:
            if (
                row.get("SEM_EXM_EXCH_ID") == "NSE"
                and row.get("SEM_SEGMENT") == "D"
                and row.get("SEM_INSTRUMENT_NAME") == "FUTIDX"
                and str(row.get("SEM_TRADING_SYMBOL", "")).startswith("NIFTY-")
            ):
                exp_raw = str(row.get("SEM_EXPIRY_DATE", "")).split(" ")[0].strip()
                if exp_raw >= today_str:
                    candidates.append({
                        "security_id": str(row.get("SEM_SMST_SECURITY_ID", "")).strip(),
                        "trading_symbol": str(row.get("SEM_TRADING_SYMBOL", "")).strip(),
                        "expiry_date": exp_raw,
                        "lot_size": float(row.get("SEM_LOT_UNITS", 65) or 65),
                        "cached_date": today_str,
                    })

        if not candidates:
            return None

        candidates.sort(key=lambda x: x["expiry_date"])
        front = candidates[0]
        try:
            FUT_CACHE_PATH.write_text(json.dumps(front, indent=2), encoding="utf-8")
        except Exception:
            pass
        return front
    except Exception as e:
        print(f"[!] Could not resolve NIFTY front future: {e}")
        return None


def test_connection():
    """Tests authentication and prints account details & live data connectivity."""
    dhan = get_dhan_client()
    if not dhan:
        return False

    print("\n[+] Authenticating with DhanHQ Data API...")
    try:
        funds = dhan.get_fund_limits()
        if funds.get("status") == "success":
            data = funds.get("data", {})
            avail = data.get("availabelBalance", data.get("availableBalance", "N/A"))
            client_id = os.getenv("DHAN_CLIENT_ID") or CLIENT_ID or ""
            masked_id = f"{client_id[:2]}******{client_id[-2:]}" if len(client_id) > 4 else "******"
            print("[OK] Authentication SUCCESSFUL!")
            print(f"    Client ID: {masked_id}")
            print("    Access Token: [PROTECTED / REDACTED]")
            print(f"    Available Ledger Balance: Rs. {avail}")
            return True
        else:
            print(f"[FAIL] Authentication FAILED: {funds.get('remarks', funds)}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection Error: {e}")
        return False


def get_nifty_expiry_list():
    """Fetches upcoming expiry dates for NIFTY options."""
    dhan = get_dhan_client()
    if not dhan:
        return []

    try:
        expiries = dhan.expiry_list(13, "IDX_I")
        if expiries.get("status") == "success":
            return unwrap_expiry_dates(expiries)
        else:
            print(f"[!] Expiry list response: {expiries}")
            return []
    except Exception as e:
        print(f"[!] Error fetching expiry list: {e}")
        return []


def get_live_option_chain(expiry_date=None):
    """
    Fetches real-time Option Chain data from DhanHQ Data API.
    Returns structured metrics: ATM strike, Total Call OI, Total Put OI, PCR.
    """
    dhan = get_dhan_client()
    if not dhan:
        return None

    try:
        if not expiry_date:
            dates = get_nifty_expiry_list()
            if dates:
                expiry_date = dates[0]
            else:
                print("[!] Could not extract expiry date.")
                return None

        chain_resp = dhan.option_chain(
            under_security_id=13,
            under_exchange_segment="IDX_I",
            expiry=expiry_date,
        )

        if chain_resp.get("status") != "success":
            print(f"[!] Option Chain API error: {chain_resp.get('remarks', chain_resp)}")
            return None

        data = unwrap_option_chain_data(chain_resp)
        oc = data.get("oc", {})
        spot_price = float(data.get("last_price", 0))

        total_call_oi = 0
        total_put_oi = 0
        strikes_data = []

        for strike_str, strike_info in oc.items():
            strike_price = float(strike_str)
            ce_data = strike_info.get("ce", {})
            pe_data = strike_info.get("pe", {})

            ce_oi = ce_data.get("oi", 0)
            pe_oi = pe_data.get("oi", 0)
            ce_ltp = ce_data.get("last_price", 0)
            pe_ltp = pe_data.get("last_price", 0)

            total_call_oi += ce_oi
            total_put_oi += pe_oi

            strikes_data.append({
                "strike": strike_price,
                "ce_oi": ce_oi,
                "ce_ltp": ce_ltp,
                "pe_oi": pe_oi,
                "pe_ltp": pe_ltp,
            })

        pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0

        strikes_data.sort(key=lambda x: abs(x["strike"] - spot_price))
        atm_strike = strikes_data[0]["strike"] if strikes_data else None

        return {
            "spot_price": spot_price,
            "expiry": expiry_date,
            "atm_strike": atm_strike,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "pcr": pcr,
            "atm_details": strikes_data[0] if strikes_data else {},
        }

    except Exception as e:
        import traceback
        print(f"[!] Error processing option chain: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("DHANHQ INSTITUTIONAL TRADING ENGINE (INITIALIZATION CHECK)")
    print("=" * 60)

    if not CLIENT_ID or not ACCESS_TOKEN:
        print(f"\n[!] 'dhan_config.env' is missing or empty at:\n    {ENV_PATH}")
        print("\n    Please create 'dhan_config.env' with:")
        print("    DHAN_CLIENT_ID=your_client_id")
        print("    DHAN_ACCESS_TOKEN=your_access_token")
    else:
        if test_connection():
            fut = resolve_nifty_front_future()
            if fut:
                print(f"\n[OK] Active NIFTY Future: {fut['trading_symbol']} (SecID={fut['security_id']}, Exp={fut['expiry_date']})")
            print("\n[+] Testing Live NIFTY Option Chain Data Feed...")
            chain = get_live_option_chain()
            if chain:
                print("[OK] Option Chain Data Feed CONNECTED!")
                print(f"    NIFTY Spot Reference: {chain.get('spot_price')}")
                print(f"    Expiry Tested: {chain.get('expiry')}")
                print(f"    ATM Strike: {chain.get('atm_strike')}")
                print(f"    Total Call OI: {chain.get('total_call_oi'):,}")
                print(f"    Total Put OI: {chain.get('total_put_oi'):,}")
                print(f"    Put-Call Ratio (PCR): {chain.get('pcr')}")
            else:
                print("[!] Could not retrieve Option Chain. Check if Data API subscription is active.")
