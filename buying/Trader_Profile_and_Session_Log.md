# 🧑‍💻 TRADER PROFILE & PERSISTENT CONTEXT LOG

**Trader:** shakhan32  
**Trading System:** Institutional Momentum & Liquidity Trap (IMLT) Framework  
**Current Phase:** 🧪 **PHASE 1: PAPER TRADING / FORWARD-TESTING (Zero Real Money at Risk)**  
**Target Milestone:** 20 Paper Trades with >= 65% Win Rate before graduating to Real Capital  
**Broker:** Groww (Groww Terminal / Web / TradingView)  
**Weekly Expiry Day:** Tuesday  
**Virtual Capital:** ₹1,00,000 (Allocated trade size: 1 Lot / 65 Qty)  
**Standard Lot Size:** 65 Qty  
**Capital Deployed Per Trade:** Max ₹15,000 – ₹22,000 (~15%–20%)  
**Risk Per Trade:** Max 12–15 points on option premium (Max loss: ₹1,125 – ₹1,500)  
**Daily Loss Limit (Circuit Breaker):** -₹3,000 (2 consecutive losses = Terminal Closed)  
**Chart Setup:**
- NIFTY Spot: 5-Minute Candlestick Chart + VWAP (`VWAP hlc3 Session`)
- Option Premium: 3-Minute Chart for pullback entry & trailing

---

## 📈 DAILY TRADE JOURNAL & PERFORMANCE LOG

| Date | Trade # | Strike / Instrument | Setup (1, 2, or 3) | Entry Price | Exit Price | P&L Points | P&L Amount (₹) | Key Takeaway / Lesson |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nov 13** | **1** | **NIFTY 25,150 PE** | Setup 1 (VWAP Rejection) | **₹171.00** | **₹162.00** | **-9.00 pts** | **-₹585.00** | *Cut on invalidation >25,160. Saved ₹1,755 capital. Lesson: Wait for 5m close.* |
| **Nov 13** | **2** | **NIFTY 25,200 CE** | Setup 3 (Ceiling Breakout) | **₹173.00** | **₹159.00** | **-14.00 pts** | **-₹910.00** | *SL hit. Stiff 25,250 hurdle caused premium decay. Loss strictly capped.* |

---

## 🧠 STRATEGY MEMORY & ARCHIVED RULES
1. **Never Chase**: Only buy on the 3-min pullback retest after 5-min candle confirmation.
2. **Never Buy OTM**: Only Delta 0.50–0.60 (ATM or Slight ITM).
3. **Midday Freeze**: 11:30 AM to 01:00 PM is strictly NO-TRADE / CHOP zone.
4. **Target 1 Rule**: At +20 to +25 points, book profit and immediately trail Stop-Loss to Cost.
5. **Zero-Tolerance Precision (The 25,146 vs 25,163 Lesson)**: Never read background Y-axis grid lines. The only acceptable source of truth is the candle's explicit OHLC tooltip or the trader's confirmed spot input.
6. **Strict 09:15 - 09:30 AM Freeze**: The opening 15 minutes is strictly for discovery. Never trade inside this window, no matter how big the candle looks.
7. **The "Futures vs Spot" Alignment Law**: Options derive fair value strictly from NIFTY 50 Spot, not Futures. Breakout signals must be confirmed on Spot index, not just Futures premium basis.
8. **Index Structural SL vs Arbitrary Premium Points**: Avoid rigid tight point SLs on option premiums that get hunted during normal index range noise. Stop-loss triggers must be tied to Index structural levels (e.g., 5-min close below VWAP).
9. **The 2-Loss Daily Circuit Breaker**: Today's session closed after 2 paper trades with only -1.49% drawdown (-₹1,495.00), leaving ₹98,505.00 (98.5%) capital 100% safe. Session officially ended at 11:04 AM.
