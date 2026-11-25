# 🛡️ GROWW EXECUTION & ₹1 LAKH CAPITAL RISK BLUEPRINT
*(Powered by DhanHQ Real-Time Data Engine)*

**Account Size:** ₹1,00,000 in Groww  
**Execution Broker:** Strictly **GROWW** (All orders punched by trader on Groww Web/App)  
**Data & OI Engine:** DhanHQ Data API v2 (`trading/dhan_automation/dhan_engine.py`)  
**Visual Charting:** `https://tv.dhan.co/` (Multi-chart TradingView) or Groww Terminal  
**Standard Lot Size:** **Strictly 65 Qty (1 Lot)**  

---

## 1. THE GOLDEN RULES FOR 1 LAKH CAPITAL

Most beginners with ₹1 Lakh make the fatal mistake of buying ₹50,000–₹80,000 worth of options in one trade. A single 20-point stop-loss or sudden reversal wipes out 25% of their capital, triggering panic and revenge trading.

### 🔑 The 3 Non-Negotiable Capital Laws:
1. **Never Deploy More than 15–20% Capital**:
   * Out of your ₹1,00,000, only **₹12,000 to ₹18,000** should be in an active position.
   * The remaining **₹82,000 to ₹88,000 remains in cash** as your shield.
2. **Fixed Risk Per Trade (Strict Option Points)**:
   * Maximum loss on any single trade is capped at **15–18 points on Option Premium** (Max **₹1,000 to ₹1,200** loss on 65 qty).
   * **Direct Execution Rule**: Stop-Loss order is placed directly into Groww immediately upon fill. We do NOT wait for candle closes on SL.
3. **The 2-Loss Daily Circuit Breaker**:
   * If you take **2 consecutive losses in a day (Max -₹2,340)**, **close Groww immediately**. You are done for the day. No exceptions.

---

## 2. LOT SIZING MATRIX (NIFTY LOT SIZE = 65 QTY)

| Setup Grade | Lots | Quantity | Average Premium | Capital Used | Stop Loss (Option Pts) | Max Risk (₹) | Target 1 (+20 pts) | Target 2 (+40 pts) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B Grade** | **1 Lot** | 65 | ₹160 | ₹10,400 | 12 pts | **-₹780** | **+₹1,300** | **+₹2,600** |
| **A Grade** | **1 Lot** | 65 | ₹180 | ₹11,700 | 15 pts | **-₹975** | **+₹1,300** | **+₹2,600** |
| **A+ Prime** | **1 Lot** | 65 | ₹180 | ₹11,700 | 18 pts | **-₹1,170** | **+₹1,500** | **+₹3,000** |

> 💡 **Recommendation**: Trade strictly **1 Lot (65 qty)**. Consistency and disciplined execution come first.

---

## 3. HOW TO EXECUTE WITH PRECISION ON GROWW TERMINAL

### Step 1: Pre-Market Watchlist Setup (09:10 AM)
1. Open Groww Web or App.
2. Check NIFTY spot price (e.g. 25,300).
3. Add 2 contracts to your Groww watchlist:
   * **ATM Call**: e.g., `NIFTY 25300 CE`
   * **ATM Put**: e.g., `NIFTY 25300 PE`

### Step 2: Placing the Entry Order on Groww
* **Order Type**: Always select **Intraday** and **Limit Order**.
* Avoid Market orders: During 9:30–10:30 AM volatility, Market orders can cause a 3–5 point slippage.
* Co-pilot calculates the exact entry bracket via Dhan live feeds. Trader punches the limit order on Groww.

### Step 3: Placing the Stop-Loss on Groww (Within 10 seconds of fill)
As soon as the order fills:
1. Go to **Positions** tab on Groww.
2. Tap on your open NIFTY position and select **"Add Stop Loss" / "Exit"**.
3. Choose **SL (Stop Loss Limit)**:
   * **Trigger Price**: Entry minus **15–18 points** (e.g., if bought at 150, Trigger = 133.00). Max risk capped at ₹1,000–₹1,200.
   * **Limit Price**: 1–2 points below trigger to ensure execution (e.g., Limit = 131.00).
4. Tap **Confirm**. Your capital is now 100% mechanically protected in Groww. No waiting for candle closes.

### Step 4: Booking Profits & Trailing (Patience Till Target)
* **Target 1 reached (+20 to +25 points)**:
  * Book profit, or immediately modify your open Stop Loss order in Groww to your **Entry Price (Cost)**. The trade is now 100% Risk-Free.
* **Target 2 reached (+40 to +50 points)**:
  * Exit the remaining quantity completely. Close Groww with a green day.

---

## 4. REALISTIC MONTHLY EXPECTATIONS

With ₹1,00,000 capital and disciplined 1-lot trading:
* Daily Target: **+₹1,500 to +₹2,500** on winning days.
* Average Risk: **-₹1,125** on losing days.
* Target Win Rate with Co-Pilot: **65%–70%**.
* Over 20 trading days:
  * 13 Winning Days $\approx$ +₹26,000
  * 7 Losing Days $\approx$ -₹8,000
  * **Net Monthly P&L $\approx$ +₹18,000 (~18% account growth)** without ever risking account health!
