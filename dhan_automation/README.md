# DhanHQ Automation & Live Data Engine
**Folder:** `trading/dhan_automation/`  
**Purpose:** Dedicated engine for real-time DhanHQ WebSocket data feeds, live Option Chain (OI/PCR/Greeks), and automated setup validation.

---

## 📁 Folder Structure:
* **`dhan_config.env.example`**: Template for your Dhan API credentials.
* **`dhan_config.env`**: Private local credentials file (Contains your `DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN`).
* **`dhan_engine.py`**: The main Python script that:
  * Connects to DhanHQ Data API.
  * Fetches real-time NIFTY Spot, Futures, and Option Chain.
  * Calculates ATM Strike, Call vs Put OI accumulation, and PCR.
  * Evaluates the 5 institutional setups with zero assumptions.

---

## 🚀 Quick Start:
1. Copy `dhan_config.env.example` to `dhan_config.env`.
2. Add your **Client ID** and **Access Token** from [web.dhan.co](https://web.dhan.co/).
3. Test connection:
   ```powershell
   python dhan_engine.py
   ```
