# DhanHQ Automation & Live Data Engine
**Folder:** `dhan_automation/`  
**Purpose:** Dedicated engine for real-time DhanHQ WebSocket data feeds, live Option Chain (OI/PCR/Greeks), NIFTY Futures Session VWAP, and automated IMLT setup validation.

---

## 📁 Folder Structure:
* **`dhan_config.env.example`**: Template for your Dhan API credentials.
* **`dhan_config.env`**: Private local credentials file (contains `DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN`).
* **`dhan_engine.py`**: Shared DhanHQ client, option chain unwrapper, NIFTY front-future resolver, and `hlc3` Session VWAP calculator.
* **`market_pulse.py`**: Instant snapshot of Spot OHLC, India VIX regime, NIFTY Futures + Session VWAP, 5-min candles, OI walls, and Option Chain Greeks.
* **`live_ws_daemon.py`**: Persistent WebSocket daemon (`wss://api-feed.dhan.co`) streaming Spot, Front Futures, and ATM CE/PE; writes `live_pulse.json` & `alert.json`.
* **`start_daemon.sh`**: macOS launcher script (uses `.venv/bin/python` automatically).

---

## 🚀 Quick Start (macOS):
1. Copy `dhan_automation/dhan_config.env.example` to `dhan_automation/dhan_config.env`.
2. Add your **Client ID** and **Access Token** from [web.dhan.co](https://web.dhan.co/).
3. Test connection & live pulse:
   ```bash
   ./.venv/bin/python dhan_automation/dhan_engine.py
   ./.venv/bin/python dhan_automation/market_pulse.py
   ```
4. Launch the live WebSocket daemon before 09:15 AM IST:
   ```bash
   ./dhan_automation/start_daemon.sh
   ```
