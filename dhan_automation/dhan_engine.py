"""
DhanHQ Institutional Engine for NIFTY Options
Author: Co-Pilot for shakhan32
System: Institutional Momentum & Liquidity Trap (IMLT) Framework
Location: trading/dhan_automation/dhan_engine.py
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Search for dhan_config.env in the current dhan_automation directory
CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_DIR / "dhan_config.env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

try:
    from dhanhq import dhanhq, DhanContext
except ImportError:
    print("Error: dhanhq library not installed. Please run: pip install dhanhq")
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
            masked_id = str(CLIENT_ID)[:2] + "******" + str(CLIENT_ID)[-2:] if CLIENT_ID and len(str(CLIENT_ID)) > 4 else "******"
            print(f"[OK] Authentication SUCCESSFUL!")
            print(f"    Client ID: {masked_id}")
            print(f"    Access Token: [PROTECTED / REDACTED]")
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
        # UnderSecurityId for NIFTY 50 Index is 13, Segment is IDX_I
        expiries = dhan.expiry_list(13, "IDX_I")
        if expiries.get("status") == "success":
            return expiries.get("data", [])
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
            exp_data = get_nifty_expiry_list()
            dates = []
            if isinstance(exp_data, list):
                dates = exp_data
            elif isinstance(exp_data, dict):
                dates = exp_data.get("data", [])

            if dates:
                expiry_date = str(dates[0])
            else:
                print(f"[!] Could not extract expiry date from: {exp_data}")
                return None

        chain_resp = dhan.option_chain(
            under_security_id=13,
            under_exchange_segment="IDX_I",
            expiry=expiry_date
        )

        if chain_resp.get("status") != "success":
            print(f"[!] Option Chain API error: {chain_resp.get('remarks', chain_resp)}")
            return None

        raw_data = chain_resp.get("data", {})
        if isinstance(raw_data, dict) and "data" in raw_data and isinstance(raw_data["data"], dict):
            data = raw_data["data"]
        else:
            data = raw_data if isinstance(raw_data, dict) else {}

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
                "pe_ltp": pe_ltp
            })

        pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0

        # Find closest ATM strike
        strikes_data.sort(key=lambda x: abs(x["strike"] - spot_price))
        atm_strike = strikes_data[0]["strike"] if strikes_data else None

        result = {
            "spot_price": spot_price,
            "expiry": expiry_date,
            "atm_strike": atm_strike,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "pcr": pcr,
            "atm_details": strikes_data[0] if strikes_data else {}
        }

        return result

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
        print(f"\n[!] 'dhan_config.env' is missing or empty in:")
        print(f"    {CURRENT_DIR}\\dhan_config.env")
        print("\n    Please create 'dhan_config.env' with:")
        print("    DHAN_CLIENT_ID=your_client_id")
        print("    DHAN_ACCESS_TOKEN=your_access_token")
    else:
        if test_connection():
            print("\n[+] Testing Live NIFTY Option Chain Data Feed...")
            chain = get_live_option_chain()
            if chain:
                print(f"[OK] Option Chain Data Feed CONNECTED!")
                print(f"    NIFTY Spot Reference: {chain.get('spot_price')}")
                print(f"    Expiry Tested: {chain.get('expiry')}")
                print(f"    ATM Strike: {chain.get('atm_strike')}")
                print(f"    Total Call OI: {chain.get('total_call_oi'):,}")
                print(f"    Total Put OI: {chain.get('total_put_oi'):,}")
                print(f"    Put-Call Ratio (PCR): {chain.get('pcr')}")
            else:
                print("[!] Could not retrieve Option Chain. Check if Data API subscription is active.")
