# 🛡️ SELLING RISK & MONEY MANAGEMENT BLUEPRINT
**Target Capital:** ₹1,00,000 to ₹10,00,000  
**Discipline Mandate:** Zero Account Blowouts | Mathematical Capital Preservation  
**System:** Institutional Momentum & Liquidity Trap (Selling Engine)  

---

## 🏛️ THE 10 UNBREAKABLE LAWS OF OPTION SELLING

### LAW #1: THE 70% MARGIN CEILING LAW
Never utilize more than **70% of total account capital** for option selling margin. The remaining **30% must sit completely unencumbered as cash buffer** to absorb temporary intraday IV expansions and gamma fluctuations.

### LAW #2: THE ZERO MARKET ORDER MANDATE
**Never punch a MARKET order on out-of-the-money (OTM) options.** 
Always use a **LIMIT order** priced at or 1–2 ticks above current bid/ask. Deep OTM option books have wide spreads; market orders can cause instantaneous 20%–50% execution slippage.

### LAW #3: THE 2.0× PREMIUM HARD STOP-LOSS
If the premium of any sold option **doubles (hits 2.0× of entry price)**, the trade thesis is invalidated. Exit that leg mechanically. Never sit and "hope" that an expanding gamma spike reverses.

### LAW #4: THE MCX 10:15 PM CLOCK RULE
For MCX commodity options (Silver, Gold, Crude) on expiry day, **all positions must be closed by 10:15 PM – 10:25 PM IST**.
* Under no circumstances shall an open position be carried past 10:30 PM.
* Broker RMS scripts auto-execute around 10:30–11:00 PM with heavy market order slippage and auto-square off fees.
* In-The-Money (ITM) options devolve into physical futures contracts requiring ₹2.5L+ delivery margins.

### LAW #5: THE STRUCTURAL DEFENSE LINE
Before entering any short call or short put, mark the **Day's High (PDH)** and **Day's Low (PDL)** on the underlying futures chart. 
* If spot breaches the Day's High on a 15-minute close $\rightarrow$ **Exit Short Calls immediately**.
* If spot breaches the Day's Low on a 15-minute close $\rightarrow$ **Exit Short Puts immediately**.

### LAW #6: NEVER AVERAGE DOWN A LOSING SHORT LEG
Averaging down on a losing option buyer position only loses premium; averaging down on a losing option seller position creates exponential, unlimited blowout risk. **If a leg is wrong, cut it. Never add lots to a tested strike.**

### LAW #7: THE 80% PROFIT HARVESTING RULE
Do not wait for the final ₹0.00 to squeeze out the last 2% of profit. When a sold option decays to **80%–90% of its initial value** (e.g. ₹50 premium falls to ₹3–₹5), place a limit buy order and close the trade. Taking the remaining 5 points exposes you to 100% of sudden tail risk.

### LAW #8: SEPARATE CASH FROM PLEDGED COLLATERAL
Collateral margin (pledged shares/liquid funds) covers exchange intraday margin, but **all daily MTM losses, brokerages, and CTT taxes are settled strictly in CASH**. Always maintain at least ₹5,000 – ₹10,000 in unencumbered cash ledger balance.

### LAW #9: DELTA-NEUTRAL STRANGLE SYMMETRY
When selling a Strangle, ensure the Put Delta and Call Delta are balanced (e.g. 0.10 Delta Put vs 0.10 Delta Call). If one side is significantly closer to spot, you are taking a hidden directional gamble.

### LAW #10: THE MANDATORY POST-EXIT COOL-DOWN
After executing an emergency defensive stop-loss on a tested leg, **enforce an automatic 15-minute terminal lock**. No new orders may be placed for 15 minutes to eliminate emotional revenge trading.

### LAW #11: ZERO MEMORY ASSUMPTION ON EXCHANGE RULES
**Never rely on memory for expiry days, holiday shifts, lot sizes, or SEBI/NSE/MCX circulars.**
Every session must verify live contract expiry dates via **DhanHQ API (`expiry_list`)** or live web verification before initiating any setup (e.g., NIFTY 50 Weekly/Monthly = **Tuesday**; SENSEX = **Thursday**).

---

## 📊 POSITION SIZING & MARGIN MATRIX

### For ₹10,00,000 Capital:
* **Max Total Margin Allowed:** **₹7,00,000**
* **Mandatory Cash Buffer:** **₹3,00,000**

| Setup | Max Lot Sizing | Margin Used | Max Acceptable Loss (1.5% Cap) | Profit Target |
| :--- | :---: | :---: | :---: | :---: |
| **NIFTY Weekly Iron Condor** | **1 to 2 Lots** *(Paper/Validation)* | ~₹0.8L – ₹1.4L | -₹15,000 | +₹2,500 to +₹5,000 |
| **NIFTY Credit Spread** | 8 to 10 Lots | ~₹4.0L – ₹5.0L | -₹12,000 | +₹10,000 to +₹15,000 |
| **Silver Mini Strangle (MCX)** | **4 Lots Max** | ~₹5.5L – ₹6.5L | **-₹6,000** | **+₹1,500 to +₹2,500** |
| **Silver Mini Credit Spread** | 4 to 5 Lots | ~₹3.0L – ₹4.0L | -₹8,000 | +₹2,000 to +₹3,500 |

---

## ⏱️ OPERATIONAL CHECKLIST BEFORE PUNCHING AN ORDER

```
[ ] 1. Is total margin deployment strictly <= 70% of account?
[ ] 2. Is order type set to LIMIT (Never Market)?
[ ] 3. Is Delta within the strategy's mandated range? (0.08–0.15 for Condors/Strangles; ~0.50 for ATM Straddles/Flies; 0.20–0.30 for directional Credit Spreads/Jade Lizard)
[ ] 4. Has the Day's High/Low structural defense line been marked on the chart?
[ ] 5. If MCX: Is current time before 9:00 PM (No entries in the final 90 mins)?
[ ] 6. Has a GTT/Limit Buy order been prepared at the strategy target (50% decay for Spreads/Condors; 30% for Straddles; 80-90% for 0DTE)?
```

---

## 🌅 DAILY MORNING ROUTINE & STRATEGY SELECTION (09:00 AM – 03:15 PM IST)

1. **08:50 – 09:15 AM IST (Global Cues, System & Pre-Market Check):**
   * **Global & Macro Cues (08:50 – 09:05 AM):** Check **GIFT NIFTY** (expected opening gap), **US overnight close & Futures** (S&P 500 / Nasdaq), **Asian Markets** (Nikkei, Hang Seng / China), **Crude Oil / USD-INR**, and any **RBI / US Fed / CPI macro events** today *(if major event day $\rightarrow$ avoid aggressive ATM/naked selling)*.
   * Verify **DhanHQ API token** (`dhan_config.env`) and run `market_pulse.py` to confirm live Spot, India VIX, and Option Chain connectivity.
   * Check overnight positional MTM (e.g., open Iron Condors) and mark **PDH / PDL / PDC**, **OI Walls**, and expiry calendar (NSE NIFTY = Tuesday; BSE SENSEX = Thursday).
2. **09:15 – 09:28 AM IST (Opening Discovery — Observe Only):**
   * Track opening gap, bid-ask spreads, and 5-min VWAP on `tv.dhan.co`. **Zero impulse entries** during opening whipsaw.
3. **09:30 AM IST (Live Strategy Selection & Execution):**
   * **Sideways + High VIX (`> 16` / `IVR > 35`):** Strategy 1 (*Iron Condor, 1–2 Lots, 50% tgt, 1× SL*) or Strategy 7 (*Regime-Gated Straddle, 20% SL, 30% tgt, 10:15+ only*).
   * **Sideways + Low VIX (`< 15`):** Strategy 8 (*Intraday Hedged Iron Fly — strict Limit orders, Wide CPR, `0.90 <= PCR <= 1.15`, 1–2 Lots*) or Strategy 4 on expiry afternoon.
   * **Directional Trend Holding VWAP:** Strategy 3 (*Bear Call Spread — primary positive-expectancy setup*) or Strategy 10 (*VWAP-Confirmed Credit Spread*); avoid Strategy 2 (*Bull Put*) in bearish macro regimes.
   * **Expiry Afternoon (`12:30 PM – 03:15 PM`):** Strategy 4 (*0DTE Expiry Harvest*).
   * Size strictly within the **70:30 Margin Rule**, launch the **30s zero-token watcher (`check_paper_trades.py --watch`)**, and log every trade in the journal.
4. **03:15 PM IST (Mandatory Intraday Cutoff):**
   * Square off all intraday legs strictly by **03:15 PM IST**; carry only pre-defined hedged positional trades overnight.
