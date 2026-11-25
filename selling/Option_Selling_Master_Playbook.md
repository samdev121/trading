# 🏛️ INSTITUTIONAL OPTION SELLING MASTER PLAYBOOK
**System:** Mathematical Probability, Volatility Skew & Theta Harvesting (MP-TH) Framework  
**Target Instruments:** NIFTY 50 Index Options (NSE) & MCX Commodity Options (Silver Mini, Crude Oil, Gold)  
**Execution Broker:** Groww / Dhan  
**Data & Greeks Engine:** DhanHQ Data API v2  

---

## 📑 TABLE OF CONTENTS
1. [The Option Seller's Edge (Why 85%+ POP Works)](#1-the-option-sellers-edge)
2. [Capital Allocation & Margin Buffer Engine (The 70:30 Rule)](#2-capital-allocation--margin-buffer-engine)
3. [The 10 Institutional Selling Strategies](#3-the-10-institutional-selling-strategies)
4. [Strike Selection & Volatility Filters (Delta & IVR Rules)](#4-strike-selection--volatility-filters)
5. [Index (NIFTY) vs Commodity (MCX) Rule Matrix](#5-index-vs-commodity-rule-matrix)
6. [Defense & Adjustment Playbook (The Firefighting Protocol)](#6-defense--adjustment-playbook)
7. [The 5 Deadly Mistakes & Immediate Disqualifiers](#7-the-5-deadly-mistakes)

---

## 1. THE OPTION SELLER'S EDGE
### Why Math & Time Beat Guesswork

* **Option Buyers rely on 3 things simultaneously going right:**
  1. Direction must be right.
  2. Move magnitude must exceed theta decay.
  3. Timing must be immediate.
* **Option Sellers win in 4 out of 5 market scenarios:**
  1. Market moves in our favor $\rightarrow$ **WIN** (Delta + Theta).
  2. Market stays completely flat $\rightarrow$ **WIN** (Pure Theta).
  3. Market moves slightly against us $\rightarrow$ **WIN** (Theta > Small Delta move).
  4. Market volatility (IV) crashes $\rightarrow$ **WIN** (Vega crush).
  5. Market moves aggressively against us $\rightarrow$ **DEFEND OR EXIT** (Controlled risk).

> **Institutional Law #1:** We do not trade for a 10x lottery ticket. We harvest consistent, high-probability cash flow (1.0% to 2.5% return on capital per week) with capped, mathematically controlled downside.

---

## 2. CAPITAL ALLOCATION & MARGIN BUFFER ENGINE
### The Mandatory 70:30 Margin Preservation Rule

Option selling blowouts happen when traders deploy 100% of their ledger to collect maximum premium. When an intraday spike occurs, margin requirements expand, triggering instant broker RMS auto-square off penalties.

| Capital Tier | Max Margin Deployed (70%) | Mandatory Cash Buffer (30%) | Max Sizing (NIFTY) | Max Sizing (Silver Mini) |
| :--- | :---: | :---: | :---: | :---: |
| **₹1,00,000** | ₹65,000 – ₹70,000 | ₹30,000 – ₹35,000 | 1 Lot Credit Spread | ❌ (Insufficient Margin) |
| **₹5,00,000** | ₹3,50,000 | ₹1,50,000 | 3–4 Lots Spreads / Condors | 2 Lots Credit Spreads |
| **₹10,00,000** | **₹7,00,000** | **₹3,00,000** | **6–8 Lots Spreads / Condors** | **4–5 Lots Strangle / Spreads** |

* **Zero-Leverage Rule:** Never utilize more than **70% of total account margin** at any given moment.
* **Buffer Utility:** The remaining **30% buffer** absorbs intraday Implied Volatility (IV) spikes without triggering margin calls.

---

## 3. THE 10 INSTITUTIONAL SELLING STRATEGIES

```
                       ┌─────────────────────────────────────────┐
                       │       WHICH STRATEGY TO DEPLOY?         │
                       └────────────────────┬────────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
      [Range-Bound / Chop]         [Directional Trend]           [Expiry Day Special]
               │                            │                            │
      ┌────────┴────────┐          ┌────────┴────────┐          ┌────────┴────────┐
      ▼                 ▼          ▼                 ▼          ▼                 ▼
 [Iron Condor]     [Strangle]  [Bull Put]       [Bear Call]   [0DTE Decay]  [Credit Spread]
 (High IV / Flat)  (Deep OTM)  (Support Hold)   (Ceiling Res) (Delta <0.10) (Strict 10:15 Exit)
```

---

### 🛡️ Strategy 1: The Delta-Neutral Iron Condor (Defined Risk / Range-Bound)
* **Market Regime:** Sideways market, Post-Event Volatility Crush, High IV Percentile (IVR > 35).
* **Construction (4 Legs):**
  1. Sell 1 OTM Call (Delta 0.12 – 0.15).
  2. Buy 1 Far OTM Call (Hedge / Wing).
  3. Sell 1 OTM Put (Delta 0.12 – 0.15).
  4. Buy 1 Far OTM Put (Hedge / Wing).
* **Target:** 80% decay of maximum premium collected (per Law #7 — e.g., ₹50 credit → close at ₹10).
* **Stop-Loss:** Total loss on condor reaches **1.0× of initial credit collected** (e.g., if ₹10,000 collected, cut trade at -₹10,000 loss).

---

### 🟢 Strategy 2: Bull Put Credit Spread (Directional Support Defense)
* **Market Regime:** Bullish Trend / Retest of Key Structural Floor / High Put Skew.
* **Construction (2 Legs):**
  1. **Sell ATM/OTM Put** below major support (Delta 0.25 – 0.30).
  2. **Buy Far OTM Put** 150–200 points lower (Hedge / Margin reducer).
* **Stop-Loss:** Underlying 5-min candle officially closes **below the short put strike**, OR short put premium reaches **2.0× entry price** (Law #3 override) — whichever triggers first.

---

### 🔴 Strategy 3: Bear Call Credit Spread (Directional Resistance Defense)
* **Market Regime:** Bearish Trend / Rejection from Overhead Ceiling / Call Writing Expansion.
* **Construction (2 Legs):**
  1. **Sell ATM/OTM Call** above major resistance (Delta 0.25 – 0.30).
  2. **Buy Far OTM Call** 150–200 points higher (Hedge / Margin reducer).
* **Stop-Loss:** Underlying 5-min candle officially closes **above the short call strike**, OR short call premium reaches **2.0× entry price** (Law #3 override) — whichever triggers first.

---

### ⚡ Strategy 4: 0DTE Expiry Theta Harvest (Pure Time Decay)
* **Market Regime:** Expiry Day afternoon:
  * **NSE NIFTY 50 Expiry:** **TUESDAY** (12:30 PM – 3:15 PM) *(Shifted from Thursday per NSE/SEBI circular)*
  * **BSE SENSEX Expiry:** **THURSDAY** (12:30 PM – 3:15 PM)
  * **MCX Commodity Expiry:** Designate Expiry Date (7:00 PM – 10:15 PM)
* **Strike Criteria:** Ultra-Deep OTM strikes (**Delta $\le$ 0.08**, > 1.5 standard deviations from spot).
* **The Golden Exit Rule:** Never hold till the final bell. Close at **₹2.00 – ₹5.00** to lock in 90% of profit and eliminate tail risk.

---

### 🦋 Strategy 5: The Iron Fly (Max ATM Theta + Capped Risk)
* **Market Regime:** Low-to-Moderate VIX (`11.0 – 14.5`) or pinned expiry afternoon near Max Pain / VWAP.
* **Construction (4 Legs):**
  1. **Sell 1 ATM Call** & **Sell 1 ATM Put** (Same strike — Straddle core).
  2. **Buy 1 OTM Call** (150–250 pts higher) & **Buy 1 OTM Put** (150–250 pts lower) as cheap protective wings.
* **Edge:** Captures maximum ATM time decay while cheap wings cap worst-case tail loss and slash margin requirement by ~60%.
* **Target:** 30%–40% of net credit collected (do not wait for pinpoint expiry).
* **Stop-Loss:** Exit if net MTM loss reaches **1.0× of expected target** or spot breaks outside the breakeven tent.

---

### 🦎 Strategy 6: The Jade Lizard (Zero Upside Risk Setup)
* **Market Regime:** Bullish/Neutral bias OR high Put skew (Put IV significantly higher than Call IV).
* **Construction (3 Legs):**
  1. **Sell 1 OTM Put** (Delta ~0.20).
  2. **Sell 1 OTM Call** + **Buy 1 Far OTM Call** (Bear Call Credit Spread).
* **Golden Construction Rule:** **Total Credit Collected (Put + Call Spread) MUST exceed the width of the Call Spread.**
* **Edge:** Because total credit > Call spread width, you have **ZERO upside risk** even if the market shoots up vertically.
* **Stop-Loss:** Downside breakeven (`Short Put Strike - Total Credit`) on a 15-minute candle close, OR naked short put premium reaches **2.0× entry price** (Law #3 override) — whichever triggers first.

---

### ⚙️ Strategy 7: Intraday Mechanical Straddle (25% Per-Leg SL)
* **Market Regime:** Standard non-event NIFTY mornings (9:30 AM – 3:15 PM IST).
* **Construction (2 Legs - Strictly NIFTY Cash-Settled):**
  1. At **9:30 AM**, sell 1 ATM Call and 1 ATM Put simultaneously.
  2. Immediately place **25% to 30% Hard Stop-Loss (SL-L)** on **each leg individually** (e.g., if CE sold at ₹100, SL = ₹125).
* **Edge:** Purely rule-based with zero directional bias required. If NIFTY trends, the losing leg cuts cleanly at +25% while the winning leg decays toward zero and pays for both.
* **Mandatory Cutoff:** Square off any open leg strictly by **3:15 PM IST**.

---

### 🦋 Strategy 8: Intraday Hedged Iron Fly (Low-VIX / Tight Range)
* **Market Regime:** Low-to-moderate VIX (`< 15`) or tight opening range (`9:30 AM – 3:15 PM IST`).
* **Construction (4 Legs - Strictly NIFTY Cash-Settled):**
  1. At **9:30 AM**, sell 1 ATM Call and 1 ATM Put.
  2. Immediately buy 200–250 pt OTM Call and Put wings (cuts margin by ~60% and caps tail risk).
* **Target & Stop-Loss:** Book at **30%–40% of net credit**; exit if net MTM loss hits **1.0× expected target** or at **3:15 PM IST**.

---

### 🎯 Strategy 9: Intraday 20-Delta OTM Strangle (30% Per-Leg SL)
* **Market Regime:** Elevated VIX (`> 16`) or wide-CPR rangebound mornings (`9:30 AM – 3:15 PM IST`).
* **Construction (2 Legs - Strictly NIFTY Cash-Settled):**
  1. Sell **0.18–0.22 Delta OTM Call** and **0.18–0.22 Delta OTM Put** for a wider buffer than an ATM straddle.
  2. Place **+30% Hard Stop-Loss (SL-L)** on each leg individually.
* **Adjustment & Cutoff:** If one leg stops out, trail the surviving leg to cost/profit and close by **3:15 PM IST**.

---

### 📈 Strategy 10: VWAP-Confirmed Intraday Credit Spread (Trend-Following Selling)
* **Market Regime:** Clear directional intraday trend holding cleanly above or below VWAP (`10:00 AM – 2:30 PM IST`).
* **Construction (2 Legs):**
  1. **Bullish above VWAP:** Sell `0.25–0.30` Delta Put + buy 150–200 pt lower Put wing.
  2. **Bearish below VWAP:** Sell `0.25–0.30` Delta Call + buy 150–200 pt higher Call wing.
* **Target & Stop-Loss:** Book at **50%–60% decay**; exit if a 5-min candle closes back across VWAP/short strike or by **3:15 PM IST**.

---

## 4. STRIKE SELECTION & VOLATILITY FILTERS

```
                            -2σ (95.4% Probability)
                                      │
   147,000 PE (Delta 0.08)            ▼            165,000 CE (Delta 0.08)
 ─────────▲───────────────────────────────●───────────────────────────────▲─────────
      Put Wing                       CURRENT SPOT                     Call Wing
    (High Put IV)                     (Equilibrium)                  (Moderate IV)
```

1. **Delta Selection Rules:**
   * **Conservative / High POP:** Delta **0.08 to 0.12** (Win rate: ~88%–92%).
   * **Balanced / Standard:** Delta **0.15 to 0.20** (Win rate: ~80%–85%).
   * **Aggressive Directional Spreads:** Delta **0.25 to 0.30** (Win rate: ~70%).
2. **Implied Volatility Rank (IVR) Check:**
   * `IVR > 40`: High IV environment $\rightarrow$ **Sell Strangles / Unhedged Spreads** (High premium edge).
   * `IVR < 20`: Low IV environment $\rightarrow$ **Sell ONLY tight Credit Spreads** (Avoid naked selling; premiums are too cheap to compensate for tail risk).

---

## 5. INDEX (NIFTY) VS COMMODITY (MCX) RULE MATRIX

| Parameter | NIFTY Index Selling (NSE) | Commodity Selling (MCX: Silver/Crude) |
| :--- | :--- | :--- |
| **Settlement Type** | **100% Cash Settled** (No physical risk) | **Devolvement into Futures** (Extreme physical risk) |
| **Trading Hours** | 09:15 AM – 03:30 PM IST | 09:00 AM – 11:30 PM IST |
| **Overnight Spikes** | Zero intraday overnight gap risk | High volatility during US COMEX Open (7:30–9:00 PM) |
| **Mandatory Exit Cutoff** | **03:15 PM IST** | **10:15 PM – 10:25 PM IST** (Never hold past 10:30 PM) |
| **Hedge Requirement** | Naked allowed with proper margin | **Hedging (Credit Spreads) strongly recommended** |

---

## 6. DEFENSE & ADJUSTMENT PLAYBOOK
### The "Firefighting" Protocol When Tested

> **⚠️ UNIVERSAL OVERRIDE (Law #3):** Regardless of any strategy-specific stop-loss rule, if ANY sold option's premium reaches **2.0× of entry price**, exit that leg immediately. This applies to ALL 10 strategies without exception — whichever SL triggers first (structural, percentage, or 2× premium) is the exit signal.

When an underlying asset makes an aggressive move toward your short strike, **hope is not a strategy**. We execute mechanical adjustments:

```text
SCENARIO: Market rallies violently toward your Short Call
             
Step 1: [Do Nothing Zone]   ──▶ Spot is > 3.0% away from strike (Normal fluctuations).
Step 2: [Roll Untested Leg] ──▶ Roll PUT leg closer to spot to collect credit and cut delta.
Step 3: [Add Long Hedge]    ──▶ Buy ATM/OTM Call debit to cap upside runaway risk.
Step 4: [HARD STOP LINE]    ──▶ Spot breaches predefined structural level ──▶ CUT CALL IMMEDIATELY.
```

1. **The Roll-In Rule:** If Call is tested, roll the Put strike UP toward spot to harvest extra premium and reduce net delta.
2. **The 2× Premium Stop-Loss:** If any short option premium **doubles from entry (2.0×)**, cut that leg immediately.
3. **The Predefined Structural Defense Line:** Identify the Day's High/Low before entering. If spot breaks that level on a 15-minute close, exit immediately (e.g., our 155,500 Silver exit rule).

---

## 7. THE 5 DEADLY MISTAKES & DISQUALIFIERS

1. ❌ **Selling Naked Options on Expiry Night Past 10:30 PM** (Guaranteed route to broker RMS penalty and devolvement panic).
2. ❌ **Deploying 100% Margin** (Leaving zero buffer for IV expansion).
3. ❌ **Using Market Orders on Deep OTM Contracts** (Suffering brutal 20–50% slippage on illiquid books).
4. ❌ **Averaging Down on a Losing Short Leg** (Adding size to a runaway breakout).
5. ❌ **Revenge Trading After a Stop-Loss** (Entering a rushed late-night trade to "recover" a loss).

---

## 8. OFFICIAL EXCHANGE EXPIRY SCHEDULE & VERIFICATION RULE

Per SEBI / NSE Circulars (effective Sept 1, 2025):
* **NSE NIFTY 50 (Weekly & Monthly):** **TUESDAY** *(if Tuesday is a trading holiday, shifts to the previous trading day)*.
* **BSE SENSEX (Weekly & Monthly):** **THURSDAY**.
* **BANKNIFTY / FINNIFTY / MIDCPNIFTY:** **Monthly Expiry Only** (weekly contracts discontinued by SEBI's 1-index-per-exchange rule).
* **MCX Commodities (Silver/Crude/Gold):** Designated exchange calendar dates (exit strictly by **10:15 PM IST**).

> **Verification Mandate:** Never assume expiry dates, lot sizes, or exchange circulars from memory. Always verify live contract expiry dates directly via **DhanHQ API (`expiry_list`)** or **official web search** before planning any trade.
