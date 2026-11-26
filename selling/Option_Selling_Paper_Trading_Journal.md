# 📓 OPTION SELLING PAPER TRADING JOURNAL
**Trader:** shakhan32  
**Trading System:** Mathematical Probability & Theta Harvesting (MP-TH) Engine  
**Paper Trading Capital:** **₹10,00,000.00**  
**Current Paper Balance:** **₹10,05,545.50**  
**Max Risk Per Trade:** ₹10,000 to ₹15,000 (1.0% to 1.5% of Capital)  
**Target Monthly Return:** +4.0% to +6.0% (+₹40,000 to +₹60,000)  

---

## 📊 PAPER TRADING PERFORMANCE SCORECARD

| Metric | Target Benchmark | Current Paper Stat | Status |
| :--- | :---: | :---: | :---: |
| **Total Paper Trades** | — | **1 Closed / 1 Active** | In Progress |
| **Win Rate (POP)** | **$\ge$ 80.0%** | **100.0%** *(1W / 0L)* | Above Target |
| **Profit Factor (Gross Win / Gross Loss)** | **$\ge$ 1.80** | **$\infty$** | Zero Losses |
| **Gross Profit Collected** | — | **₹5,752.50** | — |
| **Gross Loss Incurred** | — | **₹0.00** | — |
| **Net Realized P&L** | — | **`+₹5,545.50` (+0.55% ROI)** | 🟢 Green |
| **Max Drawdown Observed** | **$\le$ 3.0%** | **0.0%** | Pristine |
| **Average Winning Trade** | +₹2,500 – +₹5,000 | **+₹5,545.50** | Above Target |
| **Average Losing Trade** | -₹4,000 – -₹7,000 | — | — |

---

## 🎯 STRATEGY BREAKDOWN MATRIX

Track which strategy generates the highest risk-adjusted yield:

| Strategy | Trades Taken | Wins | Losses | Win Rate % | Net P&L (₹) | Avg P&L / Trade |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Iron Condor (Defined Risk)** | 0 | 0 | 0 | 0.0% | ₹0.00 | ₹0.00 |
| **Bull Put Credit Spread** | 0 | 0 | 0 | 0.0% | ₹0.00 | ₹0.00 |
| **Bear Call Credit Spread** | 0 | 0 | 0 | 0.0% | ₹0.00 | ₹0.00 |
| **0DTE Expiry Theta Harvest** | 0 | 0 | 0 | 0.0% | ₹0.00 | ₹0.00 |
| **Iron Fly (ATM + Wings)** | 0 | 0 | 0 | 0.0% | ₹0.00 | ₹0.00 |
| **Jade Lizard (Zero Upside Risk)** | 0 | 0 | 0 | 0.0% | ₹0.00 | ₹0.00 |
| **Mechanical Straddle (25% SL)** | 1 | 1 | 0 | 100.0% | +₹5,545.50 | +₹5,545.50 |
| **Short Strangle (Deep OTM)** | 0 | 0 | 0 | 0.0% | ₹0.00 | ₹0.00 |

---

## 📝 CHRONOLOGICAL PAPER TRADE LOG

### 🟡 Paper Trade #4: 26-Nov-2026 | NIFTY 01-Dec VWAP Bull Put Spread (`25,750 PE / 25,550 PE`) — **OPEN**

| Parameter | Planned Setup | Live Execution Details |
| :--- | :--- | :--- |
| **Date & Time** | 26-Nov-2026 at 10:57 AM IST | **Entry: 10:57 AM IST** (Active) |
| **Instrument & Expiry** | `NIFTY 50` (01-Dec-2026 Expiry) | **1 Lot (65 Qty)** |
| **Strategy Type** | **Strategy 10: VWAP-Confirmed Bull Put Spread** | Strike ID: `cmwx421hv0001u80rjqf01gd6` |
| **Short Put Leg** | Sell `25,750 PE` @ Live Bid | Sold @ **₹108.00** *(2× Override: ₹216.00)* |
| **Long Put Hedge** | Buy `25,550 PE` @ Live Ask | Bought @ **₹59.25** *(200-pt wing)* |
| **Net Credit Collected** | **+48.75 Points** × 65 Qty | **Total Credit: +₹3,168.75** |
| **Planned Target** | **50% Decay** | Close Spread @ **₹24.35** (`+₹1,586` gross) |
| **Planned Hard Stop** | **1.0× Credit / VWAP Close** | Cut if MTM hits **`-₹3,169`** or 5-min Spot < `25,900` / VWAP |
| **Trade Status** | **OPEN / ACTIVE 🟡** | — |

---

### 🟡 Paper Trade #3: 26-Nov-2026 | NIFTY 01-Dec Intraday Regime-Gated Straddle (`25,850 CE + PE`) — **OPEN**

| Parameter | Planned Setup | Live Execution Details |
| :--- | :--- | :--- |
| **Date & Time** | 26-Nov-2026 at 10:18 AM IST | **Entry: 10:18 AM IST** (Active) |
| **Instrument & Expiry** | `NIFTY 50` (01-Dec-2026 Expiry) | **1 Lot (65 Qty)** |
| **Strategy Type** | **Strategy 7: Intraday Regime-Gated Straddle (20% Per-Leg SL)** | Strike ID: `cmwx2nrri00009l0rd8w3avan` |
| **Call Leg** | Sell `25,850 CE` @ Live Bid | Sold @ **₹214.30** *(20% Hard SL: ₹257.15)* |
| **Put Leg** | Sell `25,850 PE` @ Live Bid | Sold @ **₹189.80** *(20% Hard SL: ₹227.75)* |
| **Combined Straddle** | **404.10 Points** × 65 Qty | **Total Credit: ₹26,266.50** |
| **Planned Target** | **30% Combined Decay** | Close Combined @ **₹282.85** (`+₹7,913.75` gross) |
| **Cutoff & Trail** | Trail survivor to cost if 1 leg hits 20% SL | Mandatory Square-Off: **03:15 PM IST** |
| **Trade Status** | **OPEN / ACTIVE 🟡** | — |

---

### 🟡 Paper Trade #1: 25-Nov-2026 | NIFTY 01-Dec Iron Condor (25,200 PE / 26,600 CE)

| Parameter | Planned Setup | Live Execution Details |
| :--- | :--- | :--- |
| **Date & Time** | 25-Nov-2026 at 11:50 AM IST | **Entry: 11:50 AM IST** (Active) |
| **Instrument & Expiry** | `NIFTY 50` (01-Dec-2026 Tuesday Expiry) | 6 Lots (390 Qty) |
| **Strategy Type** | **Delta-Neutral Iron Condor (Defined Risk)** | — |
| **Underlying Spot & VIX** | Spot: `25,941.95` \| India VIX: `17.98` | PCR: `1.14` (Ceiling: 26,000 \| Floor: 25,500) |
| **Short Leg 1 (Call)** | Sell `26,600 CE` (Delta `0.16`) | Sold @ **₹49.15** |
| **Hedge Leg 1 (Call)** | Buy `26,800 CE` (Delta `0.09`) | Bought @ **₹26.25** *(Call Spread: +22.90 pts)* |
| **Short Leg 2 (Put)** | Sell `25,200 PE` (Delta `-0.11`) | Sold @ **₹34.70** |
| **Hedge Leg 2 (Put)** | Buy `25,000 PE` (Delta `-0.07`) | Bought @ **₹20.90** *(Put Spread: +13.80 pts)* |
| **Net Credit Collected** | **+36.70 Points** × 390 Qty | **Total Inflow: `+₹14,313.00`** *(Max Profit)* |
| **Margin Deployed** | ~₹2,60,000 (26% of Capital) | Cash Buffer Left: **~₹7,40,000 (74% ✅)** |
| **Breakeven Zone** | **25,163.30 to 26,636.70** | **1,473-Point Safe Channel** |
| **Planned Target** | **80% Decay** (Law #7) | Close Combined @ **₹7.30** (`+₹11,466.00`) |
| **Planned Hard Stop** | **1.0× Credit** / Structural Breach | Cut if MTM hits **`-₹14,300`** or Spot breaks `26,400` / `25,400` |
| **Trade Status** | **OPEN / ACTIVE 🟡** | — |

#### 🔍 ENTRY RATIONALE & RULE COMPLIANCE CHECK:
1. **70:30 Margin Rule:** Deployed only ~26% margin (₹2.6L), keeping 74% (₹7.4L) untouched cash cushion.
2. **Delta & IVR Edge:** India VIX at `17.98` provided elevated OTM premiums with ~85%–89% POP.
3. **Defined Risk:** Both sides fully hedged with 200-pt wings; zero naked blowout risk.

---

### 🟢 Paper Trade #2: 25-Nov-2026 | NIFTY 01-Dec Intraday Mechanical Straddle (`25,950 CE + PE`) — **CLOSED (+₹5,545.50 Net)**

| Parameter | Planned Setup | Live Execution Details |
| :--- | :--- | :--- |
| **Date & Time** | 25-Nov-2026 at 11:54 AM IST | **Entry: 11:54 AM** \| **Final Exit: 13:29:37 IST** |
| **Instrument & Expiry** | `NIFTY 50` (01-Dec-2026 Expiry) | **2 Lots (130 Qty)** |
| **Strategy Type** | **Strategy 7: Intraday Mechanical Straddle (25% Per-Leg SL)** | — |
| **Underlying Spot & VIX** | Entry Spot: `25,922.25` \| Exit Spot: `25,715.75` | India VIX: `17.98` $\rightarrow$ `17.90` |
| **Call Leg** | Sell `25,950 CE` | Sold @ **₹254.95** $\rightarrow$ **Trailed Profit SL HIT @ ₹155.45 (13:29:37)** (`+₹12,935.00`) |
| **Put Leg** | Sell `25,950 PE` | Sold @ **₹221.00** $\rightarrow$ **25% SL HIT @ ₹276.25 (12:31 PM)** (`-₹7,182.50`) |
| **Combined Straddle** | **475.95 Points** × 130 Qty | Gross P&L: **`+₹5,752.50`** |
| **Est. Brokerage & Taxes** | 4 Orders × ₹20 + STT/Exch/GST | **`-₹207.00`** |
| **Net Realized P&L** | **+₹5,545.50 (+0.55% ROI)** | Margin Freed: **~₹1,75,000** |
| **Trade Status** | **CLOSED — WIN 🟢** | Trailed Profit SL (`₹155.00`) locked in winning CE leg on afternoon bounce |

#### 🔍 ENTRY RATIONALE & RULE COMPLIANCE CHECK:
1. **70:30 Portfolio Rule:** Total combined margin across Trade #1 + Trade #2 is ~43.5% (₹4.35L), keeping 56.5% (₹5.65L) untouched buffer.
2. **Risk Cap (1.5% Max Loss):** Sized strictly at 2 Lots so even a worst-case double SL hits max ~₹15,470 (1.5% of ₹10L capital).
3. **Timeframe Discipline:** Strictly intraday; mandatory square-off at 03:15 PM IST.

---

### 📋 PAPER TRADE ENTRY TEMPLATE (COPY & PASTE FOR NEW TRADES)

```markdown
### [🟢/🔴] Paper Trade #X: [Date] | [Instrument] - [Strategy Name]

| Parameter | Planned Setup | Actual Execution |
| :--- | :--- | :--- |
| **Date & Time** | DD-Mon-YYYY at HH:MM AM/PM | Entry: HH:MM $\rightarrow$ Exit: HH:MM |
| **Instrument & Expiry** | e.g. NIFTY 28-Nov-2026 / SILVERM | Expiry Date |
| **Strategy Type** | Iron Condor / Bull Put / Bear Call / Strangle | — |
| **Underlying Spot at Entry** | Index Spot / Futures LTP | e.g. 25,250 |
| **Short Leg 1 (CE/PE)** | Strike & Entry LTP (Delta ~0.12) | Sold @ ₹LTP |
| **Short Leg 2 (CE/PE)** | Strike & Entry LTP (Delta ~0.12) | Sold @ ₹LTP |
| **Hedge Legs (if Spread)** | Long Strike & Premium Paid | Bought @ ₹LTP |
| **Net Credit Collected** | Combined Points × Qty | Total Inflow: ₹X,XXX |
| **Margin Deployed** | ₹ Margin Used (Exchange SPAN) | Cash Buffer Left: ₹X,XXX (>=30%) |
| **Planned Target** | 80% Decay (Exit @ 20% of credit) | Target Price: ₹X |
| **Planned Hard Stop** | 2.0× Premium / Structural Level | Stop-Loss Price: ₹X |
| **Exit Trigger** | Target 80% Hit / Stop Hit / Time Cutoff | e.g. Target Hit at 10:15 AM |
| **Exit Prices** | Buy to Close Prices for all legs | Short Legs closed @ ₹X |
| **Gross P&L** | Points Captured × Qty | **₹ Gross Amount** |
| **Estimated Brokerage & Taxes** | ₹20/order + CTT + GST | ~₹100 to ₹150 |
| **Net Realized P&L** | Gross P&L − Total Charges | **`+₹X,XXX.00` (+X.X% ROI)** |
| **Trade Status** | **CLOSED (WIN / LOSS)** | — |

#### 🔍 EXECUTION QUALITY AUDIT & POST-MORTEM:
1. **Did Market Stay Within Boundary?**: 
2. **Was 70:30 Margin Rule Respected?**: 
3. **Were Adjustments / Defense Executed?**: 
4. **Key Lesson for Real Capital Deployment**: 
```

---

## 🛡️ PAPER TRADING RULES OF ENGAGEMENT
1. **Treat Virtual Capital Like Real Money:** Never take a paper trade that you wouldn't take with real cash.
2. **Strict Slippage & Commission Deduction:** Always deduct standard ₹20/order brokerage, 0.1% STT/exchange/GST, and realistic **0.5–1.0 pt Limit-order slippage** so paper results reflect live net expectancy.
3. **Never Paper Trade With Unrealistic Prices:** Enter and exit only at live BID/ASK prices fetched from the Dhan API.
4. **Minimum 20 Trades Before Scaling Real Capital:** We will run at least 20 documented paper trades and require **positive Net Expectancy (Avg Net P&L > 0) & controlled Max Drawdown** — not win rate alone — before deploying real capital.
