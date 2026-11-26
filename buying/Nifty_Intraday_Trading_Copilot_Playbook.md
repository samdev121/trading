# 🚀 NIFTY INTRADAY TRADING CO-PILOT SYSTEM
**Version:** 3.0 (Upgraded for `tv.dhan.co`, DhanHQ Institutional API Engine & ₹1,00,000 Capital)  
**Target Asset:** NIFTY 50 Index Options (Intraday Momentum & Scalping)  
**Execution Broker:** Strictly **GROWW** (All orders punched manually by trader on Groww Web / App)  
**Data & OI Engine:** DhanHQ Data API v2 (Local Python Engine for real-time OI, PCR, Greeks & Spot feeds)  
**Visual Charting:** `tv.dhan.co` (Multi-chart TradingView) or Groww Terminal Charts  
**Account Capital:** ₹1,00,000 in Groww (Strict Risk Limit: ₹1,000 – ₹1,200 per trade)  
**Standard Lot Size:** **Strictly 65 Qty (1 Lot)**  

---

## 📑 TABLE OF CONTENTS
1. [The Recommended Timeframe Engine (`tv.dhan.co` Split Layout)](#1-the-recommended-timeframe-engine)
2. [₹1,00,000 Capital & Position Sizing Rules](#2-100000-capital--position-sizing-rules)
3. [Daily Operational Schedule & Mandatory Startup Protocol](#3-daily-operational-schedule)
4. [Pre-Market Matrix (09:00 - 09:15 AM)](#4-pre-market-matrix-0900---0915-am)
5. [The 5 Institutional Trading Setups](#5-the-5-institutional-trading-setups)
6. [The Strict "NO TRADE TODAY" Filter](#6-the-strict-no-trade-today-filter)
7. [Strike Selection & Dhan / Groww Execution Protocol](#7-strike-selection--dhan--groww-execution-protocol)
8. [Live 5-Second Shorthand Sync Protocol](#8-live-5-second-shorthand-sync-protocol)
9. [Standard Execution Bracket Output](#9-standard-execution-bracket-output)
10. [Zero-Tolerance Precision Rule (The Anti-Guesswork Protocol)](#10-zero-tolerance-precision-rule)

---

## 1. THE RECOMMENDED TIMEFRAME ENGINE
### Why Single Timeframes Fail & The `tv.dhan.co` Dual-Screen Solution

* **The Problem with 1-Minute**: 80% of breakouts are retail traps, noise, and emotional whip-saws.
* **The Problem with 15-Minute**: Stop-losses become too wide (30–40 points on spot), destroying risk-reward.

### 🏆 The Professional Dual-Timeframe Setup on `tv.dhan.co`:
`tv.dhan.co` provides **Free Multi-Chart 2-Split Layout**, allowing simultaneous tracking on one screen without tab switching:

1. **LEFT PANEL $\rightarrow$ NIFTY FUTURES / SPOT (5-Minute Timeframe with VWAP)**:
   * Institutional structural filter: tracks candle closes, VWAP slope, and key support/resistance floors.
2. **RIGHT PANEL $\rightarrow$ ATM/ITM OPTION PREMIUM CHART (3-Minute Timeframe)**:
   * Execution & trigger anchor: times precise entries and allows **visual drag-and-drop Stop-Loss & Target lines** directly on the premium candlesticks.

> **Golden Rule**: Confirm setup and institutional footprint on the **5-Min Futures/Spot Chart (Left)**, execute and manage your stop-loss on the **3-Min Option Chart (Right)**.

---

## 2. ₹1,00,000 CAPITAL & POSITION SIZING RULES

Option buying with ₹1,00,000 capital requires strict sizing to prevent account blowouts:

| Metric | Rule for ₹1,00,000 Capital |
| :--- | :--- |
| **Max Capital Deployed Per Trade** | **₹12,000 to ₹18,000** (~15% of account). Keep ₹85,000 in cash. |
| **Standard Position Size** | **1 Lot (65 Qty)** (Never exceed 1 lot during scaling phase). |
| **Max Risk Per Trade (Stop-Loss)** | **15 to 18 Option Points = ₹975 to ₹1,170 maximum loss**. |
| **Max Daily Loss Limit** | **2 Trades SL = -₹2,340**. (If 2 trades hit SL, shut terminal for the day). |
| **Daily Target** | **+2.0% to +3.5% = +₹2,000 to +₹3,500** (1 to 2 clean trades). |

---

## 3. DAILY OPERATIONAL SCHEDULE

### 🚨 Mandatory Session Startup Protocol:
**Whenever the trader initiates a session (e.g., "start trading", "market open", or morning handshake), the Co-Pilot MUST ALWAYS FIRST initiate this 2-Step Handshake:**
1. **Primary Platform Reminder:** Open **`https://tv.dhan.co/`** (Set 2-Chart Split Layout: Left = NIFTY Futures with VWAP; Right = Active Option Strike).
2. **Live Data Engine Handshake:** Run `python trading/dhan_automation/dhan_engine.py` to verify:
   * `✓ DhanHQ API Connection: ACTIVE`
   * `✓ Live Option Chain Feed: CONNECTED`
   * `✓ Real-time NIFTY Spot & PCR: VERIFIED`
*Co-Pilot must verify these connections before providing any market bias or setup evaluation.*

| Time Window | Market Phase | Co-Pilot Focus | Trader Action on Groww |
| :--- | :--- | :--- | :--- |
| **08:50 – 09:15 AM** | Pre-Market | Check Global Cues (GIFT NIFTY, US/Asia, Macro events), CPR, PDH/PDL, Max OI walls | Add ATM CE & PE to Groww watchlist |
| **09:15 – 09:30 AM** | Opening Discovery | Track initial 15-min range (ORB), VWAP establishment | Observe, NO impulse trades |
| **09:30 – 11:30 AM** | **Prime Momentum Window** | Active hunting for Setup 1, 2, or 3 | Execute verified high-probability setups |
| **11:00 – 01:00 PM** | **Midday Window (Conditional / Optional)** | Hunt for A+ Setups (VWAP Rejection / Clean Floor Breakdown). **Agar confirmed setup mile toh zaroor alert karein.** | Execute ONLY on confirmed A+ setup with tight SL; ignore random chop |
| **01:00 – 03:00 PM** | **Afternoon Institutional Expansion** | Monitor short-covering rallies / breakdown continuation | Trade only with Next-Week contracts on expiry |
| **03:00 – 03:30 PM** | Market Close / Square-off | Intraday position closure | Mandatory 100% flat before closing bell |

---

## 4. PRE-MARKET MATRIX (09:00 - 09:15 AM)

Before 09:15 AM, the co-pilot locks in these reference levels:

### A. Key Reference Levels
* **PDH (Previous Day High)**: Resistance / Breakout Level
* **PDL (Previous Day Low)**: Support / Breakdown Level
* **PDC (Previous Day Close)**: Prior day equilibrium
* **Central Pivot Range (CPR)**:
  * Narrow CPR $\rightarrow$ Big directional trending move likely.
  * Wide CPR $\rightarrow$ Sideways / Mean-reversion day likely.

### B. Open Interest (OI) & Structural Walls
* **Max Call OI Strike**: The institutional "Hard Ceiling" (Heavy Call writing).
* **Max Put OI Strike**: The institutional "Hard Floor" (Heavy Put writing).
* **Put-Call Ratio (PCR)**:
  * `PCR > 1.25`: Strong Bullish bias (look for CE buying on pullbacks).
  * `0.90 <= PCR <= 1.10`: Neutral / Sideways (High theta decay danger).
  * `PCR < 0.75`: Strong Bearish bias (look for PE buying on pullbacks).

### C. India VIX (The Volatility Regime Meter)
India VIX measures market volatility expectations. For an intraday option buyer, it dictates whether premiums will expand rapidly or bleed to theta:
* **VIX < 12.0 (Sluggish / Low Volatility Regime)**:
  - Premiums move sluggishly; index movement does not translate into fast option gains.
  - High risk of theta crush.
  - Action: Avoid aggressive breakout buying. Take only A+ setups or stay in cash.
* **13.0 <= VIX <= 17.5 (The "Goldilocks Zone" - Prime Option Buying Momentum)**:
  - **Ideal environment for Option Buyers.**
  - Premiums expand smoothly and cleanly with delta (+20 to +40 points easily achievable).
  - Stop-Loss of 15–18 points works with maximum reliability.
  - Action: Full confidence in Setups 1 through 5.
* **VIX > 18.0 (Wild Volatility / Spike Regime)**:
  - Violent swings and erratic wicks.
  - Action: Quick booking at Target 1 (+20 pts); do not hold runners through deep pullbacks.

### D. Global & Macro Cues (08:50 – 09:05 AM)
* **GIFT NIFTY**: Estimates opening gap vs PDC (large gap >0.7% often triggers opening profit-booking or VWAP retest).
* **US Markets (S&P 500 / Nasdaq + US Futures)**: Sets overnight risk-on / risk-off sentiment.
* **Asian Markets (Nikkei, Hang Seng / China)**: Confirms whether Asia is extending or fading the US move.
* **Macro / Event Calendar**: Crude Oil spikes, USD/INR moves, US Fed / RBI policy / CPI prints (expect elevated wicks and wider swings).

---

## 5. THE 5 INSTITUTIONAL TRADING SETUPS (BIDIRECTIONAL ARSENAL)

Option buyers only trade when institutional capital is forcing immediate directional expansion. If the market is just wandering aimlessly sideways, **we do not trade (cash is a position)**.

---

### 🟢 Setup 1: Bullish Breakout & VWAP Pullback Bounce (The "Buy on Dip" CE Setup)
* **Market Regime**: Bullish Trend / Breakout Expansion.
* **What it looks like**: Nifty breaks out above resistance / PDH with above-average volume on the 5-min candle, then pulls back to test VWAP or the broken ceiling.
* **The Trap to Avoid**: Never chase the breakout green candle at its peak.
* **The Trigger**: Wait for a pullback toward the 9-EMA or VWAP that prints a rejection wick (holding the level). When the 5-min candle bounces and closes green off the support floor, we enter.
* **Option Entry**: Buy ATM Call (CE) (Delta ~0.50–0.55).
* **Stop-Loss (Index Structural)**: 5-min candle close back below VWAP / Support level.
* **Target**: Target 1: +20 to +25 pts | Target 2: +40 to +50 pts.
```text
       [Breakout!] ──▶   ▲
                         │
      [Ceiling/25,320] ──┼───────────────
                         │   ▼  ▲  ◀── [We Buy CE Here on the Bounce!]
                         └──────┘
```

---

### 🔴 Setup 2: Bearish Breakdown & VWAP Pullback Rejection (The "Sell on Rise" PE Setup)
* **Market Regime**: Bearish Trend / Downtrending Market (Below VWAP).
* **What it looks like**: Nifty is trading below VWAP. Buyers attempt a relief pullback rally pushing up toward the falling VWAP line from below.
* **Institutional Footprint**: Smart money algorithms use the bounce to add short positions; aggressive Call writing enters at upper strikes.
* **The Trigger**: The 5-minute candle approaches/touches VWAP, gets rejected with an upper selling wick, and **officially closes as a RED candle below VWAP**.
* **Option Entry**: Buy ATM Put (PE) (Delta ~0.50–0.55) upon confirmation of the 5-min close.
* **Stop-Loss (Index Structural)**: 5-min candle officially closes **above VWAP** (invalidation).
* **Target**: Retest of Day's Low / Support floor (Option Target 1: +20 to +25 pts | Target 2: +40 pts).
```text
                         ┌──────┐
                         │   ▲  ▼  ◀── [We Buy PE Here on VWAP Rejection!]
      [VWAP/25,280] ────┼───────────────
                         │
       [Plunge Down] ──▶ ▼
```

---

### 🔄 Setup 3: Liquidity Sweep & Fakeout Reversal (The "Trap & Reverse" Setup - Best R:R)
* **Market Regime**: Range Extremes / False Breakouts.
* **3A (Bull Trap $\rightarrow$ Buy PE)**: Nifty spikes above PDH / Day's High, lures in retail breakout buyers, and immediately prints an inverted hammer / shooting star closing **back inside the range** on the 5-min chart $\rightarrow$ **Buy ATM Put (PE)** as trapped buyers panic-sell.
* **3B (Bear Trap $\rightarrow$ Buy CE)**: Nifty plunges below PDL / Day's Low, lures in retail breakdown sellers, and immediately prints a hammer / pinbar closing **back inside the range** on the 5-min chart $\rightarrow$ **Buy ATM Call (CE)** as trapped shorts cover.
* **Target**: Retest of intraday VWAP or opposite range boundary.
```text
                 ▲ ◀── [Fake Spike! Lures in retail buyers]
                ┌┴┐
      ──────────┼─┼─────────────── [Broken Level]
                └─┘ ◀── [5-min candle closes back INSIDE the range]
                 ▼
                 ▼ ◀── [We Buy PUT (PE) as trapped buyers dump!]
```

---

### 🚀 Setup 4: Institutional Short-Covering Blast (The "Ceiling Explosion" CE Setup)
* **Market Regime**: Post-Compression Breakout / Trend Continuation.
* **What it looks like**: Nifty hovers right on top of VWAP or a flat ceiling for 30–45 minutes, coiling tightly like a spring (volatility compression).
* **The Trigger**: A sudden massive, full-bodied 5-min candle blasts through the ceiling and key strike level (e.g. 25,250) with volume > 2× 20-EMA.
* **Institutional Footprint**: Call writers panic and buy back their contracts at market price, fueling rapid vertical momentum.
* **Option Entry**: Immediate ATM Call (CE) buy on candle close for a rapid momentum scalp.
* **Target**: Full Gap-Fill / Next major strike hurdle (+25 to +40 pts).

---

### 🩸 Setup 5: Consolidation Floor Breakdown Cascade (The "Long-Unwinding Plunge" PE Setup)
* **Market Regime**: Heavy Supply / Support Failure.
* **What it looks like**: Nifty consolidates sideways below VWAP for 30–60 minutes, repeatedly testing a horizontal support floor (e.g., 25,225).
* **The Trigger**: The horizontal floor finally cracks — a decisive 5-minute candle **breaks and closes BELOW the support floor** with expanding volume.
* **Institutional Footprint**: Long buyers are forced to dump positions (stop-loss trigger run), while fresh institutional shorting accelerates the cascade.
* **Option Entry**: Buy ATM Put (PE) upon official 5-minute candle close below the floor.
* **Stop-Loss (Index Structural)**: 5-minute candle closes back above the broken floor level.
* **Target**: +25 to +45 points rapid expansion on Put premium.
```text
      [Consolidation] ── [=== Floor 25,225 ===]
                                │
                                ▼ ◀── [5-Min Close BELOW Floor: Buy PE!]
                                ▼
                                ▼ ◀── [Long Unwinding Cascade Plunge!]
```

---

## 6. THE STRICT "NO TRADE TODAY" FILTER

**Rule #1 is Capital Preservation.** The co-pilot will explicitly issue a **`NO TRADE TODAY`** warning when:
1. **VWAP Whipsaw**: Spot crosses above and below VWAP multiple times within 30 minutes with overlapping candles.
2. **Straddle Writing Dominance**: Both ATM CE and PE are adding massive OI simultaneously (institutions locking the market in a tight range to harvest theta).
3. **Mid-Range Dead Zone**: Spot is hovering in the middle between PDH and PDL with no nearby support/resistance.
4. **PCR Neutrality**: PCR is stuck between 0.90 and 1.10 with no directional expansion.
5. **Unpriced Global Shock / Major Macro Event**: Sudden overnight US/China crash or major RBI/Fed/CPI announcement causing erratic opening whipsaws and wide bid-ask spreads.

---

## 7. STRIKE SELECTION & GROWW EXECUTION PROTOCOL (POWERED BY DHAN DATA)

### A. Strike Selection (Delta Rule)
* **Delta Target**: **0.50 to 0.60** (Deep At-The-Money or Slight In-The-Money).
  * *Bullish Example (Nifty Spot @ 25,310)*: Select **25,300 CE** or **25,250 CE**.
  * *Bearish Example (Nifty Spot @ 25,290)*: Select **25,300 PE** or **25,350 PE**.
* **Strict Ban**: Never buy Out-Of-The-Money (OTM) options (Delta < 0.35). Cheap premiums lose value to theta decay even if the market moves in your direction.
* **Expiry Afternoon Rule**: If trading on Expiry day after **1:00 PM**, strictly shift to the **Next Week Expiry** contract to avoid 0-DTE gamma crush.

### B. Standard Execution on Groww Terminal (Strictly 65 Qty / 1 Lot)
1. **Watchlist Preparation**: Add both ATM CE and ATM PE to Groww watchlist by 09:15 AM.
2. **Limit Order Entry**: Co-pilot issues the pre-calculated bracket card. Trader punches the **Limit Order** on Groww Web/App.
3. **Immediate Groww Stop-Loss (Within 10 seconds of fill)**:
   * Go to "Positions" on Groww $\rightarrow$ Click position $\rightarrow$ Select **"Add Stop Loss"**.
   * Enter **SL-Limit** with pre-determined **15–18 points** risk (Max loss ₹1,000–₹1,200).
   * Confirm order. Capital is now mechanically protected. No waiting for candle closes.
4. **Target 1 Management**: Once Target 1 (+20 to +25 pts) is hit, book profit or modify Groww Stop-Loss to Entry Price (Cost) for a risk-free runner.

---

## 8. LIVE 5-SECOND SHORTHAND SYNC PROTOCOL

During live market hours, use these fast shorthand commands in chat:

### Trader to Co-Pilot:
| Command | What It Means |
| :--- | :--- |
| `!scan` | Co-pilot analyzes the current regime, levels, and tells you whether to wait or stay alert. |
| `!bias [spot]` | e.g. `!bias 25310` $\rightarrow$ Checks position vs VWAP, key walls, and returns instant bias. |
| `!plan CE [level]` | e.g. `!plan CE 25320` $\rightarrow$ Generates an immediate ready-to-execute Call trade bracket. |
| `!plan PE [level]` | e.g. `!plan PE 25280` $\rightarrow$ Generates an immediate ready-to-execute Put trade bracket. |
| `!trail [entry] [current]`| e.g. `!trail 145 170` $\rightarrow$ Calculates updated trailing stop-loss levels. |
| `[Screenshot]` | Drop a screenshot of your Groww/TradingView chart; co-pilot reads price action and levels directly. |

### Co-Pilot to Trader (Binary Micro-Checks):
The co-pilot will only ask **Yes/No** questions:
* *"Nifty is retesting 25,320. Is the 3-min candle rejecting lower prices with a wick? (Y/N)"*
* *"Is spot currently trading above VWAP? (Y/N)"*

---

## 9. STANDARD EXECUTION BRACKET OUTPUT

When a trade is ready, the co-pilot delivers this single actionable card:

```text
======================================================
🎯 NIFTY TRADE BRACKET: [CALL BUY / PUT BUY]
======================================================
- Instrument:        NIFTY [STRIKE] [CE/PE] ([Current/Next] Expiry)
- Quantity on Groww: 1 Lot (65 Qty)
- Setup Type:        [Breakout Retest / Liquidity Trap / Momentum Surge]
- Quality Grade:     [A+ / A / B]
------------------------------------------------------
- Ideal Entry Zone:  ₹[XXX] - ₹[XXX]
- Max Chase Price:   ₹[XXX] (DO NOT ENTER ABOVE THIS)
- Option Stop-Loss:  ₹[XXX] (Strict 15-18 pts | Max risk ₹975 - ₹1,170)
- Spot Invalidation: Below/Above ₹[XX,XXX] on 5-min close (Exit early if broken)
------------------------------------------------------
- Target 1 (Book Profit & SL to Cost): ₹[XXX] (+20-25 pts | ₹1,300 - ₹1,625 profit)
- Target 2 (Runner):                   ₹[XXX] (+40-50 pts | ₹2,600 - ₹3,250 profit)
======================================================
```

---

## 10. ZERO-TOLERANCE PRECISION RULE (THE ANTI-GUESSWORK PROTOCOL)

**MANDATORY LAW: In live intraday trading, an error of 10 points or 10 minutes can blow up a trade. Visual guessing from unzoomed charts is strictly prohibited.**

### The 4 Absolute Rules for the Co-Pilot & Trader:

1. **NO VISUAL GUESSWORK FROM ZOOMED-OUT CHARTS**:
   * Never estimate candle times or price peaks by eyeballing a multi-day or compressed chart.
   * On Groww, the chart during market hours must be zoomed into **Today's Session Only** so each 5-min candle is large, distinct, and unambiguous.

2. **RAW OHLC DATA EXTRACTION AS GROUND TRUTH**:
   * Every level, peak, and trigger must be confirmed against the **exact numbers in Groww's OHLC header box** (e.g., `O: 25,374.60, H: 25,380.45, L: 25,361.10, C: 25,366.50`).
   * No level is accepted until its exact decimal value is verified from the DOM or crosshair reading.

3. **MANDATORY 3-POINT DATA VERIFICATION BEFORE TRADE EMISSION**:
   Before the Co-Pilot outputs any trade bracket (`!plan CE` or `!plan PE`), it must explicitly confirm:
   - `✓ Confirmed Spot Price: [Exact Number]`
   - `✓ Confirmed 5-Min Close / Level: [Exact Number]`
   - `✓ Confirmed VWAP Benchmark: [Exact Number]`
   *If any single number is unverified, NO TRADE will be issued.*

4. **THE 2-SECOND LIVE HANDSHAKE**:
   * Trader places crosshair on the active/key candle or states exact spot (e.g. `!scan Spot 25,340`).
   * Co-pilot calculates brackets based strictly on that factual number, leaving 0% margin for error.

5. **THE Y-AXIS GRID TRAP (CASE LESSON: 25,146 vs. 25,163)**:
   * **The Flaw**: Reading background Y-axis grid marks (e.g. 25,146.00) instead of the candle's actual OHLC value (25,163.00). A 17-point error destroys option risk management.
   * **The Law**: Background axis grid lines are strictly forbidden for calculating entries, stop-losses, or invalidations. Ground truth is exclusively the candle's real-time OHLC tooltip or the trader's direct confirmed spot input.

6. **STRICT 09:15 - 09:30 AM OBSERVATION ENFORCEMENT**:
   * No matter how massive or explosive the opening 09:15 AM candle is, it is mathematically inside the forbidden discovery window. No trades are permitted until 09:30 AM has passed and a verified pullback/setup forms.

7. **THE ABSOLUTE "ZERO ASSUMPTIONS" DATA INTEGRITY LAW (MANDATORY)**:
   * **Never Assume or Extrapolate**: The Co-Pilot is strictly forbidden from assuming, inventing, simulating, or claiming ANY market data that is not actively visible or open on screen (including Option Chain Open Interest, PCR, India VIX, or candle OHLC).
   * **Ask Immediately If Data Is Missing**: If any key metric (e.g. Option Chain / Strike OI buildup / VIX) is required to evaluate a trade and the tab or tool is not currently open, the Co-Pilot **MUST EXPLICITLY ASK THE TRADER** to open the tab (e.g., click "Chain" on Groww Terminal) or provide the number.
   * **Real Capital Principle**: Options trading involves real hard-earned capital. Zero tolerance for theoretical assumptions disguised as live facts. If it is not on the screen, it does not exist until verified.

---
*Created for shakhan32. Saved in buying/Nifty_Intraday_Trading_Copilot_Playbook.md*
