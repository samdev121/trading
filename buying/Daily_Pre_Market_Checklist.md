# 📋 DAILY 2-MINUTE PRE-MARKET & TRADE CHECKLIST
**Trader:** shakhan32  
**Trading System:** Institutional Momentum & Liquidity Trap (IMLT) Framework  
**Standard Lot Size:** 65 Qty  
**Risk Per Trade:** Max 15–18 points on option (~₹1,000 – ₹1,200)  

---

## 🚀 PART 0: MANDATORY MORNING STARTUP PROTOCOL (09:00 - 09:05 AM)
*Rule: Whenever the trader says "start trading" or at the beginning of any trading session, the Co-Pilot MUST immediately issue this startup protocol:*

- [ ] **1. Open Groww Terminal (Strictly for Execution)**:
  - Account verified with ₹1,00,000 capital.
  - Watchlist ready with ATM CE & ATM PE.
- [ ] **2. Open `tv.dhan.co` (For Multi-Chart 2-Split View)**:
  - **Left Screen**: NIFTY Futures (5-Min + VWAP)
  - **Right Screen**: Active ATM/ITM Option Premium Chart (3-Min)
  *(Or use Groww Chart tab if preferred).*
- [ ] **3. Live Data Engine Handshake**:
  - Run `dhan_engine.py` to confirm live connection to DhanHQ Data API:
  - `[OK] DhanHQ API Authenticated (Client ID: 11******74)`
  - `[OK] Live Option Chain Feed & Real-time PCR Active`

---

## ☀️ PART 1: MORNING ROUTINE (09:10 - 09:15 AM)

- [ ] **1. Check Nifty Pre-Market Spot**: Note the opening level.
- [ ] **2. Identify Key Reference Levels**:
  - PDH (Previous Day High): `_____________`
  - PDL (Previous Day Low): `_____________`
  - PDC (Previous Day Close): `_____________`
  - CPR Width: [ ] Narrow (Trend Day expected) | [ ] Wide (Rangebound Day expected)
- [ ] **3. Check India VIX**:
  - India VIX Value: `_____________`
  - [ ] < 12 (Low Volatility - Option buying cautious)
  - [ ] 13 - 17 (Sweet Spot - Prime Option Buying Momentum)
  - [ ] > 18 (High Volatility - Fast moves, maintain discipline)
- [ ] **4. Check Put-Call Ratio (PCR)**:
  - PCR value: `_____________`
  - [ ] > 1.25 (Bullish bias - Look for CE Setups 1 & 4)
  - [ ] 0.90 - 1.10 (CHOP / Straddle Warning - Wait for clean breakout)
  - [ ] < 0.75 (Bearish bias - Look for PE Setups 2 & 5)
- [ ] **5. Add ATM Strikes to Groww Watchlist**:
  - ATM Call (CE): `_____________`
  - ATM Put (PE): `_____________`

---

## ⚡ PART 2: BEFORE CLICKING "BUY" ON GROWW (10-Second Pre-Flight Check)

Never enter a trade unless ALL 5 boxes are checked:

- [ ] **1. Setup Verified**: Is this one of the 5 Proven Institutional Setups?
  - [ ] Setup 1: Bullish Breakout & VWAP Bounce (CE)
  - [ ] Setup 2: Bearish Breakdown & VWAP Rejection (PE)
  - [ ] Setup 3: Liquidity Sweep & Fakeout Reversal (CE/PE)
  - [ ] Setup 4: Short-Covering Squeeze Blast (CE)
  - [ ] Setup 5: Consolidation Floor Breakdown Cascade (PE)
- [ ] **2. 5-Min Candle Confirmation**: Has the 5-min candle officially closed? (Never enter mid-candle).
- [ ] **3. Spot & VWAP Alignment**: Is Spot confirming the level and aligned with VWAP?
- [ ] **4. Position Size**: Strictly **1 Lot (65 Qty)**.
- [ ] **5. Option Point Stop-Loss Pre-Determined**: 
  - Stop-Loss is strictly set on **Option Premium Points** (Pre-determined 15–18 points max | Max Risk ₹1,000–₹1,200).
  - Placed into Groww immediately upon fill. No waiting for candle closes on SL.

---

## 🛑 PART 3: DAILY DISCIPLINE RULES

1. **Max Trades Per Day**: 2 clean trades max.
2. **2-Loss Daily Circuit Breaker**: If 2 trades hit Stop-Loss in a single day (Max loss -₹2,400), **CLOSE GROWW FOR THE DAY**.
3. **No Revenge Trading**: Never increase lot size to recover a loss.
4. **Target Discipline**: Once entered, sit tight and wait till Target 1 (+20 to +25 pts) is reached. Trail SL to Cost once Target 1 is hit.
5. **ZERO ASSUMPTIONS LAW**: Never trade or advise on unverified data. If Option Chain OI, VIX, or candle OHLC is not open on screen, the Co-Pilot must ask the trader immediately — never assume or extrapolate.
