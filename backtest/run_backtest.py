"""
Quantitative 1-Minute Backtester for the 10 NIFTY Option Selling Strategies (MP-TH Framework).

Data:
  - 1-minute NIFTY options OHLCV + OI (2026-01-01 to 2026-07-21, 135 sessions)
  - Daily India VIX (rolling IVR) + Global Cues (SP500, NASDAQ, NIKKEI, HSI)

Rules Enforced (Zero Look-Ahead Bias):
  - Entry strictly >= 10:00 IST
  - Global Cues alignment (t-1 US close + t Asia)
  - Synthetic 1-min Spot (Put-Call Parity) + cumulative Session VWAP
  - Live 1-min Option Chain OI walls (Max PE OI Floor, Max CE OI Ceiling, PCR)
  - IVR > 35 (rolling VIX rank) mandatory for Strategy #1 Iron Condor
  - Position size: 1 Lot (65 Qty) [max 1-2 lots]
  - Strict 20% Stop-Loss per short leg
  - Costs: Groww brokerage (Rs 20/order) + STT (0.10% sell) + NSE/SEBI/Stamp/GST + 1.0 pt slippage/fill
"""
import os
import math
import time
import numpy as np
import pandas as pd

LOT_SIZE = 65
SLIPPAGE_PTS = float(os.getenv("SLIPPAGE_PTS", "1.0"))  # 1 point per fill (entry & exit)
LEG_SL_PCT = float(os.getenv("LEG_SL_PCT", "0.20"))      # Per-short-leg SL


def calc_groww_charges(sell_turnover: float, buy_turnover: float, n_orders: int) -> float:
    """Exact Groww + NSE F&O Options statutory charges (INR)."""
    brokerage = 20.0 * n_orders
    stt = sell_turnover * 0.001          # 0.10% on sell premium
    txn = (sell_turnover + buy_turnover) * 0.0003503  # NSE option txn
    sebi = (sell_turnover + buy_turnover) * 0.000001
    stamp = buy_turnover * 0.00003       # 0.003% on buy side
    gst = (brokerage + txn + sebi) * 0.18
    return brokerage + stt + txn + sebi + stamp + gst


def load_macro_signals(macro_path: str) -> pd.DataFrame:
    """Compute zero-lookahead daily VIX IVR and Global Cues alignment."""
    m = pd.read_parquet(macro_path).sort_index()
    # Rolling 126-day (6-month) VIX IVR using t-1 close
    vix = m["VIX_Close"].ffill()
    vix_min = vix.rolling(126, min_periods=30).min()
    vix_max = vix.rolling(126, min_periods=30).max()
    m["vix_prev"] = vix.shift(1)
    m["ivr_prev"] = ((vix - vix_min) / (vix_max - vix_min).replace(0, np.nan) * 100.0).shift(1)

    # Prior US session returns (known by 08:50 IST)
    sp_ret = m["SP500_Close"].ffill().pct_change().shift(1) * 100.0
    nq_ret = m["NASDAQ_Close"].ffill().pct_change().shift(1) * 100.0
    # Asian session intraday/close cues (Nikkei/HSI same day)
    nk_ret = m["NIKKEI_Close"].ffill().pct_change() * 100.0
    hs_ret = m["HSI_Close"].ffill().pct_change() * 100.0

    m["us_ret"] = (sp_ret + nq_ret) / 2.0
    m["asia_ret"] = (nk_ret + hs_ret) / 2.0
    m["global_bull"] = (m["us_ret"] > -0.3) & (m["asia_ret"] > -0.3) & ((m["us_ret"] > 0.15) | (m["asia_ret"] > 0.15))
    m["global_bear"] = (m["us_ret"] < 0.3) & (m["asia_ret"] < 0.3) & ((m["us_ret"] < -0.15) | (m["asia_ret"] < -0.15))
    m["global_quiet"] = (m["us_ret"].abs() < 1.0) & (m["asia_ret"].abs() < 1.0)
    return m


def build_day_context(day_df: pd.DataFrame, target_expiry: str) -> pd.DataFrame | None:
    """Build 1-minute Spot, Session VWAP, and Live OI walls for a single day."""
    sub = day_df[day_df["expiry"] == target_expiry]
    if sub.empty:
        return None

    # Pivot close & oi by (timestamp, strike, option_type)
    # Estimate spot via Put-Call Parity on highest-volume strikes
    ce = sub[sub["option_type"] == "CE"]
    pe = sub[sub["option_type"] == "PE"]
    merged = pd.merge(
        ce[["timestamp", "strike", "close", "volume", "oi"]],
        pe[["timestamp", "strike", "close", "volume", "oi"]],
        on=["timestamp", "strike"],
        suffixes=("_ce", "_pe"),
    )
    if merged.empty:
        return None

    # Pick strike closest to parity (min |ce - pe|) at each timestamp
    merged["diff"] = (merged["close_ce"] - merged["close_pe"]).abs()
    idx = merged.groupby("timestamp")["diff"].idxmin()
    atm = merged.loc[idx].sort_values("timestamp").copy()
    atm["spot"] = atm["strike"] + atm["close_ce"] - atm["close_pe"]
    atm["tot_vol"] = (atm["volume_ce"].fillna(0) + atm["volume_pe"].fillna(0)).clip(lower=1.0)
    atm["vwap"] = (atm["spot"] * atm["tot_vol"]).cumsum() / atm["tot_vol"].cumsum()

    # Live OI walls per timestamp across all strikes of target_expiry
    ce_oi = ce.groupby(["timestamp", "strike"])["oi"].sum().unstack(fill_value=0)
    pe_oi = pe.groupby(["timestamp", "strike"])["oi"].sum().unstack(fill_value=0)
    atm["max_ce_oi_strike"] = atm["timestamp"].map(ce_oi.idxmax(axis=1))
    atm["max_pe_oi_strike"] = atm["timestamp"].map(pe_oi.idxmax(axis=1))
    tot_ce_oi = ce.groupby("timestamp")["oi"].sum()
    tot_pe_oi = pe.groupby("timestamp")["oi"].sum()
    pcr_series = tot_pe_oi / tot_ce_oi.replace(0, np.nan)
    atm["pcr"] = atm["timestamp"].map(pcr_series)
    return atm.set_index("timestamp")


def pick_strike_by_delta_proxy(day_sub: pd.DataFrame, ts, spot: float, opt_type: str, target_delta: float) -> float | None:
    """
    Pick strike matching target Delta using approximate moneyness / premium ratio
    when exact Greeks are absent in 1-min OHLCV.
    Delta ~0.50 -> ATM; ~0.25 -> ~0.7% OTM; ~0.20 -> ~1.0% OTM; ~0.13 -> ~1.6% OTM; <=0.08 -> ~2.3% OTM.
    """
    if target_delta >= 0.45:
        dist_pct = 0.0
    elif target_delta >= 0.24:
        dist_pct = 0.007
    elif target_delta >= 0.18:
        dist_pct = 0.010
    elif target_delta >= 0.11:
        dist_pct = 0.016
    else:
        dist_pct = 0.023

    raw_strike = spot * (1.0 + dist_pct) if opt_type == "CE" else spot * (1.0 - dist_pct)
    target_k = round(raw_strike / 50.0) * 50.0
    avail = day_sub[(day_sub["timestamp"] == ts) & (day_sub["option_type"] == opt_type) & (day_sub["close"] > 1.0)]
    if avail.empty:
        return None
    strikes = avail["strike"].values
    return float(strikes[np.argmin(np.abs(strikes - target_k))])


def simulate_legs(
    bars_by_leg: list[tuple[str, pd.DataFrame]],
    qty: int,
    target_decay_pct: float | None = None,
    leg_sl_pct: float | None = None,
    golden_exit_px: float | None = None,
    cutoff_ts=None,
) -> dict | None:
    """
    Simulate multi-leg position over synchronized 1-minute bars.
    bars_by_leg: list of (direction 'SELL'|'BUY', df indexed by timestamp with open/high/low/close)
    Enforces strict per-short-leg SL + optional combined target decay + cutoff.
    """
    if leg_sl_pct is None:
        leg_sl_pct = LEG_SL_PCT
    # Align timestamps
    common_idx = bars_by_leg[0][1].index
    for _, df in bars_by_leg[1:]:
        common_idx = common_idx.intersection(df.index)
    if cutoff_ts is not None:
        common_idx = common_idx[common_idx <= cutoff_ts]
    if len(common_idx) < 2:
        return None

    entry_ts = common_idx[0]
    legs = []
    net_credit_raw = 0.0
    for direction, df in bars_by_leg:
        px = float(df.loc[entry_ts, "close"])
        if px <= 0.5:
            return None
        fill_entry = max(0.05, px - SLIPPAGE_PTS) if direction == "SELL" else (px + SLIPPAGE_PTS)
        legs.append({
            "dir": direction,
            "df": df,
            "entry_raw": px,
            "entry_fill": fill_entry,
            "sl_trigger": px * (1.0 + leg_sl_pct) if direction == "SELL" else None,
            "closed": False,
            "exit_fill": None,
        })
        net_credit_raw += px if direction == "SELL" else -px

    if net_credit_raw <= 2.0:
        return None  # Reject negative/tiny credit structures

    # Walk forward minute by minute
    exit_ts = common_idx[-1]
    for ts in common_idx[1:]:
        # 1. Check per-short-leg 20% SL
        any_sl = False
        for leg in legs:
            if leg["dir"] == "SELL" and not leg["closed"]:
                bar_high = float(leg["df"].loc[ts, "high"])
                if bar_high >= leg["sl_trigger"]:
                    # Stopped out at sl_trigger + slippage (or bar close if gapped)
                    exit_px = max(leg["sl_trigger"], float(leg["df"].loc[ts, "open"])) + SLIPPAGE_PTS
                    leg["exit_fill"] = exit_px
                    leg["closed"] = True
                    any_sl = True

        # If any short leg hit 20% SL, close all legs on spreads/condors/flies;
        # for straddles/strangles (#7, #9), if 1 leg stops, trail survivor to breakeven (entry_raw)
        if any_sl:
            if len(legs) >= 3 or any(l["dir"] == "BUY" for l in legs):
                # Defined-risk or 3+ leg: close entire structure cleanly
                for leg in legs:
                    if not leg["closed"]:
                        c = float(leg["df"].loc[ts, "close"])
                        leg["exit_fill"] = (c + SLIPPAGE_PTS) if leg["dir"] == "SELL" else max(0.05, c - SLIPPAGE_PTS)
                        leg["closed"] = True
                exit_ts = ts
                break
            else:
                # 2-leg Straddle/Strangle: trail surviving leg SL to entry_raw (breakeven)
                for leg in legs:
                    if not leg["closed"]:
                        leg["sl_trigger"] = min(leg["sl_trigger"], leg["entry_raw"])
                if all(l["closed"] for l in legs):
                    exit_ts = ts
                    break

        # 2. Check combined target decay or golden exit
        cur_spread = 0.0
        for leg in legs:
            if not leg["closed"]:
                c = float(leg["df"].loc[ts, "close"])
                cur_spread += c if leg["dir"] == "SELL" else -c
        if target_decay_pct is not None and cur_spread <= net_credit_raw * (1.0 - target_decay_pct):
            for leg in legs:
                if not leg["closed"]:
                    c = float(leg["df"].loc[ts, "close"])
                    leg["exit_fill"] = (c + SLIPPAGE_PTS) if leg["dir"] == "SELL" else max(0.05, c - SLIPPAGE_PTS)
                    leg["closed"] = True
            exit_ts = ts
            break
        if golden_exit_px is not None and all(l["dir"] == "SELL" for l in legs):
            if all(float(l["df"].loc[ts, "close"]) <= golden_exit_px for l in legs if not l["closed"]):
                for leg in legs:
                    if not leg["closed"]:
                        c = float(leg["df"].loc[ts, "close"])
                        leg["exit_fill"] = c + SLIPPAGE_PTS
                        leg["closed"] = True
                exit_ts = ts
                break

    # Square off any open legs at final bar (15:15 cutoff)
    for leg in legs:
        if not leg["closed"]:
            c = float(leg["df"].loc[exit_ts, "close"])
            leg["exit_fill"] = (c + SLIPPAGE_PTS) if leg["dir"] == "SELL" else max(0.05, c - SLIPPAGE_PTS)
            leg["closed"] = True

    gross_pnl = 0.0
    sell_turnover = 0.0
    buy_turnover = 0.0
    for leg in legs:
        if leg["dir"] == "SELL":
            gross_pnl += (leg["entry_fill"] - leg["exit_fill"]) * qty
            sell_turnover += leg["entry_fill"] * qty
            buy_turnover += leg["exit_fill"] * qty
        else:
            gross_pnl += (leg["exit_fill"] - leg["entry_fill"]) * qty
            buy_turnover += leg["entry_fill"] * qty
            sell_turnover += leg["exit_fill"] * qty

    charges = calc_groww_charges(sell_turnover, buy_turnover, n_orders=len(legs) * 2)
    net_pnl = gross_pnl - charges
    return {
        "entry_ts": entry_ts,
        "exit_ts": exit_ts,
        "gross_pnl": gross_pnl,
        "charges": charges,
        "net_pnl": net_pnl,
        "credit_pts": net_credit_raw,
    }


def get_leg_df(exp_df: pd.DataFrame, strike: float, opt_type: str, start_ts) -> pd.DataFrame | None:
    sub = exp_df[(exp_df["strike"] == strike) & (exp_df["option_type"] == opt_type) & (exp_df["timestamp"] >= start_ts)]
    if sub.empty:
        return None
    return sub.sort_values("timestamp").set_index("timestamp")[["open", "high", "low", "close"]]


def main():
    t0 = time.time()
    macro = load_macro_signals("backtest/data/macro_daily.parquet")
    print("Loading NIFTY_2026_intraday.parquet...")
    df = pd.read_parquet(
        "backtest/data/NIFTY_2026_intraday.parquet",
        columns=["date", "timestamp", "expiry", "strike", "option_type", "open", "high", "low", "close", "volume", "oi"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
    df["time_str"] = df["timestamp"].dt.strftime("%H:%M")

    dates = sorted(df["date"].unique())
    print(f"Loaded {len(dates)} sessions ({dates[0]} to {dates[-1]}). Running 10-strategy backtest...")

    # Pre-index by expiry for multi-day positional holds (#1, #2, #3, #5, #6)
    by_expiry = {exp: grp for exp, grp in df.groupby("expiry")}
    by_date = {d: grp for d, grp in df.groupby("date")}

    results = {f"S{i}": [] for i in range(1, 11)}

    for d in dates:
        day_df = by_date[d]
        exps = sorted([e for e in day_df["expiry"].unique() if e >= d])
        if not exps:
            continue
        nearest_exp = exps[0]
        dte = (pd.to_datetime(nearest_exp) - pd.to_datetime(d)).days
        # Positional strategies use nearest expiry with >= 1 DTE
        pos_exp = exps[0] if dte >= 1 else (exps[1] if len(exps) > 1 else None)

        if d not in macro.index:
            continue
        mrow = macro.loc[d]
        vix_prev = float(mrow["vix_prev"]) if pd.notna(mrow["vix_prev"]) else 14.0
        ivr_prev = float(mrow["ivr_prev"]) if pd.notna(mrow["ivr_prev"]) else 30.0
        g_bull = bool(mrow["global_bull"])
        g_bear = bool(mrow["global_bear"])
        g_quiet = bool(mrow["global_quiet"])

        ctx = build_day_context(day_df, nearest_exp)
        if ctx is None:
            continue

        # Filter timestamps >= 10:00 and <= 14:30 for entries
        entry_cands = ctx[(ctx.index.strftime("%H:%M") >= "10:00") & (ctx.index.strftime("%H:%M") <= "14:30")]
        if entry_cands.empty:
            continue

        exp_df_near = by_expiry[nearest_exp]
        eod_cutoff = pd.to_datetime(f"{d} 15:15:00")

        # --- Helper to pick first bar meeting condition ---
        def first_bar(cond_series):
            hits = entry_cands[cond_series]
            return hits.index[0] if not hits.empty else None

        # Common regime conditions on live 1-min bar
        bull_hold = (entry_cands["spot"] > entry_cands["vwap"]) & (entry_cands["spot"] > entry_cands["max_pe_oi_strike"]) & (entry_cands["pcr"] >= 1.0)
        bear_hold = (entry_cands["spot"] < entry_cands["vwap"]) & (entry_cands["spot"] < entry_cands["max_ce_oi_strike"]) & (entry_cands["pcr"] <= 1.0)
        neutral_hold = (
            (entry_cands["spot"] >= entry_cands["max_pe_oi_strike"])
            & (entry_cands["spot"] <= entry_cands["max_ce_oi_strike"])
            & (entry_cands["pcr"].between(0.85, 1.20))
        )

        # ------------------------------------------------------------------
        # S1: Iron Condor (Positional, IVR > 35, Global Quiet, OI/PCR neutral)
        # ------------------------------------------------------------------
        if pos_exp and ivr_prev > 35.0 and g_quiet:
            ts = first_bar(neutral_hold)
            if ts is not None:
                spot = float(ctx.loc[ts, "spot"])
                ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "CE", 0.13)
                pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "PE", 0.13)
                if ce_s and pe_s:
                    edf = by_expiry[pos_exp]
                    legs = [
                        ("SELL", get_leg_df(edf, ce_s, "CE", ts)),
                        ("BUY", get_leg_df(edf, ce_s + 200, "CE", ts)),
                        ("SELL", get_leg_df(edf, pe_s, "PE", ts)),
                        ("BUY", get_leg_df(edf, pe_s - 200, "PE", ts)),
                    ]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.80, cutoff_ts=pd.to_datetime(f"{pos_exp} 15:15:00"))
                        if res:
                            results["S1"].append(res)

        # ------------------------------------------------------------------
        # S2: Bull Put Credit Spread (Global Bull + Spot > VWAP + OI Floor)
        # ------------------------------------------------------------------
        if pos_exp and g_bull:
            ts = first_bar(bull_hold)
            if ts is not None:
                spot = float(ctx.loc[ts, "spot"])
                pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "PE", 0.27)
                if pe_s:
                    edf = by_expiry[pos_exp]
                    legs = [("SELL", get_leg_df(edf, pe_s, "PE", ts)), ("BUY", get_leg_df(edf, pe_s - 200, "PE", ts))]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.60, cutoff_ts=pd.to_datetime(f"{pos_exp} 15:15:00"))
                        if res:
                            results["S2"].append(res)

        # ------------------------------------------------------------------
        # S3: Bear Call Credit Spread (Global Bear + Spot < VWAP + OI Ceiling)
        # ------------------------------------------------------------------
        if pos_exp and g_bear:
            ts = first_bar(bear_hold)
            if ts is not None:
                spot = float(ctx.loc[ts, "spot"])
                ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "CE", 0.27)
                if ce_s:
                    edf = by_expiry[pos_exp]
                    legs = [("SELL", get_leg_df(edf, ce_s, "CE", ts)), ("BUY", get_leg_df(edf, ce_s + 200, "CE", ts))]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.60, cutoff_ts=pd.to_datetime(f"{pos_exp} 15:15:00"))
                        if res:
                            results["S3"].append(res)

        # ------------------------------------------------------------------
        # S4: 0DTE Expiry Theta Harvest (DTE == 0, >= 12:30 PM, Delta <= 0.08)
        # ------------------------------------------------------------------
        if dte == 0 and g_quiet:
            cands_0dte = entry_cands[(entry_cands.index.strftime("%H:%M") >= "12:30") & neutral_hold]
            if not cands_0dte.empty:
                ts = cands_0dte.index[0]
                spot = float(ctx.loc[ts, "spot"])
                ce_s = pick_strike_by_delta_proxy(exp_df_near[exp_df_near["date"] == d], ts, spot, "CE", 0.07)
                pe_s = pick_strike_by_delta_proxy(exp_df_near[exp_df_near["date"] == d], ts, spot, "PE", 0.07)
                if ce_s and pe_s:
                    legs = [("SELL", get_leg_df(exp_df_near, ce_s, "CE", ts)), ("SELL", get_leg_df(exp_df_near, pe_s, "PE", ts))]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, golden_exit_px=3.5, cutoff_ts=eod_cutoff)
                        if res:
                            results["S4"].append(res)

        # ------------------------------------------------------------------
        # S5: Positional Iron Fly (VIX 11-14.5, Global Quiet, Neutral OI/VWAP)
        # ------------------------------------------------------------------
        if pos_exp and 11.0 <= vix_prev <= 14.5 and g_quiet:
            ts = first_bar(neutral_hold)
            if ts is not None:
                spot = float(ctx.loc[ts, "spot"])
                atm_k = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "CE", 0.50)
                if atm_k:
                    edf = by_expiry[pos_exp]
                    legs = [
                        ("SELL", get_leg_df(edf, atm_k, "CE", ts)),
                        ("SELL", get_leg_df(edf, atm_k, "PE", ts)),
                        ("BUY", get_leg_df(edf, atm_k + 200, "CE", ts)),
                        ("BUY", get_leg_df(edf, atm_k - 200, "PE", ts)),
                    ]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.35, cutoff_ts=pd.to_datetime(f"{pos_exp} 13:30:00"))
                        if res:
                            results["S5"].append(res)

        # ------------------------------------------------------------------
        # S6: Jade Lizard (Global Bull + Spot > VWAP + OI Floor)
        # ------------------------------------------------------------------
        if pos_exp and g_bull:
            ts = first_bar(bull_hold)
            if ts is not None:
                spot = float(ctx.loc[ts, "spot"])
                pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "PE", 0.20)
                ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "CE", 0.20)
                if pe_s and ce_s:
                    edf = by_expiry[pos_exp]
                    legs = [
                        ("SELL", get_leg_df(edf, pe_s, "PE", ts)),
                        ("SELL", get_leg_df(edf, ce_s, "CE", ts)),
                        ("BUY", get_leg_df(edf, ce_s + 150, "CE", ts)),
                    ]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.60, cutoff_ts=pd.to_datetime(f"{pos_exp} 15:15:00"))
                        if res:
                            results["S6"].append(res)

        # ------------------------------------------------------------------
        # S7: Intraday Regime-Gated Straddle (10:15-12:30, Neutral, 20% SL)
        # ------------------------------------------------------------------
        if g_quiet:
            cands_s7 = entry_cands[
                (entry_cands.index.strftime("%H:%M") >= "10:15")
                & (entry_cands.index.strftime("%H:%M") <= "12:30")
                & neutral_hold
                & ((entry_cands["spot"] - entry_cands["vwap"]).abs() / entry_cands["spot"] < 0.0025)
            ]
            if not cands_s7.empty:
                ts = cands_s7.index[0]
                spot = float(ctx.loc[ts, "spot"])
                atm_k = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts, spot, "CE", 0.50)
                if atm_k:
                    legs = [("SELL", get_leg_df(exp_df_near, atm_k, "CE", ts)), ("SELL", get_leg_df(exp_df_near, atm_k, "PE", ts))]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, cutoff_ts=eod_cutoff)
                        if res:
                            results["S7"].append(res)

        # ------------------------------------------------------------------
        # S8: Intraday Hedged Iron Fly (VIX < 15, Neutral, 200-pt wings)
        # ------------------------------------------------------------------
        if vix_prev < 15.0 and g_quiet:
            ts = first_bar(neutral_hold)
            if ts is not None:
                spot = float(ctx.loc[ts, "spot"])
                atm_k = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts, spot, "CE", 0.50)
                if atm_k:
                    legs = [
                        ("SELL", get_leg_df(exp_df_near, atm_k, "CE", ts)),
                        ("SELL", get_leg_df(exp_df_near, atm_k, "PE", ts)),
                        ("BUY", get_leg_df(exp_df_near, atm_k + 200, "CE", ts)),
                        ("BUY", get_leg_df(exp_df_near, atm_k - 200, "PE", ts)),
                    ]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.35, cutoff_ts=eod_cutoff)
                        if res:
                            results["S8"].append(res)

        # ------------------------------------------------------------------
        # S9: Intraday 20-Delta OTM Strangle (VIX > 16, Neutral, 20% SL)
        # ------------------------------------------------------------------
        if vix_prev > 16.0 and g_quiet:
            ts = first_bar(neutral_hold)
            if ts is not None:
                spot = float(ctx.loc[ts, "spot"])
                ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts, spot, "CE", 0.20)
                pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts, spot, "PE", 0.20)
                if ce_s and pe_s:
                    legs = [("SELL", get_leg_df(exp_df_near, ce_s, "CE", ts)), ("SELL", get_leg_df(exp_df_near, pe_s, "PE", ts))]
                    if all(l[1] is not None for l in legs):
                        res = simulate_legs(legs, LOT_SIZE, cutoff_ts=eod_cutoff)
                        if res:
                            results["S9"].append(res)

        # ------------------------------------------------------------------
        # S10: VWAP-Confirmed Intraday Credit Spread (Global + VWAP + OI)
        # ------------------------------------------------------------------
        ts_bull = first_bar(bull_hold) if g_bull else None
        ts_bear = first_bar(bear_hold) if g_bear else None
        if ts_bull is not None and (ts_bear is None or ts_bull <= ts_bear):
            spot = float(ctx.loc[ts_bull, "spot"])
            pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts_bull, spot, "PE", 0.27)
            if pe_s:
                legs = [("SELL", get_leg_df(exp_df_near, pe_s, "PE", ts_bull)), ("BUY", get_leg_df(exp_df_near, pe_s - 200, "PE", ts_bull))]
                if all(l[1] is not None for l in legs):
                    res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.55, cutoff_ts=eod_cutoff)
                    if res:
                        results["S10"].append(res)
        elif ts_bear is not None:
            spot = float(ctx.loc[ts_bear, "spot"])
            ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts_bear, spot, "CE", 0.27)
            if ce_s:
                legs = [("SELL", get_leg_df(exp_df_near, ce_s, "CE", ts_bear)), ("BUY", get_leg_df(exp_df_near, ce_s + 200, "CE", ts_bear))]
                if all(l[1] is not None for l in legs):
                    res = simulate_legs(legs, LOT_SIZE, target_decay_pct=0.55, cutoff_ts=eod_cutoff)
                    if res:
                        results["S10"].append(res)

    # Print summary table
    names = {
        "S1": "Iron Condor (IVR>35)",
        "S2": "Bull Put Spread",
        "S3": "Bear Call Spread",
        "S4": "0DTE Theta Harvest",
        "S5": "Positional Iron Fly",
        "S6": "Jade Lizard",
        "S7": "Regime-Gated Straddle",
        "S8": "Intraday Hedged Iron Fly",
        "S9": "20-Delta OTM Strangle",
        "S10": "VWAP Credit Spread",
    }
    print("\n" + "=" * 105)
    print(f"BACKTEST RESULTS (1 Lot = 65 Qty | {int(LEG_SL_PCT*100)}% Leg SL | >=10:00 IST | Global+VWAP+OI Filters | Groww Fees + {SLIPPAGE_PTS}pt Slippage)")
    print("=" * 105)
    print(f"{'Strategy':<28} {'Trades':>6} {'Win%':>7} {'Gross(Rs)':>11} {'Costs(Rs)':>10} {'Net(Rs)':>11} {'Expectancy':>11} {'MaxDD(Rs)':>10}")
    print("-" * 105)
    rows_out = []
    for k in [f"S{i}" for i in range(1, 11)]:
        trades = results[k]
        if not trades:
            print(f"{k + ' ' + names[k]:<28} {0:>6} {'-':>7} {'0':>11} {'0':>10} {'0':>11} {'0':>11} {'0':>10}")
            continue
        tdf = pd.DataFrame(trades)
        n = len(tdf)
        win_pct = (tdf["net_pnl"] > 0).mean() * 100.0
        gross = tdf["gross_pnl"].sum()
        costs = tdf["charges"].sum()
        net = tdf["net_pnl"].sum()
        exp_per_trade = net / n
        eq = tdf["net_pnl"].cumsum()
        dd = (eq - eq.cummax()).min()
        print(f"{k + ' ' + names[k]:<28} {n:>6} {win_pct:>6.1f}% {gross:>11,.0f} {costs:>10,.0f} {net:>11,.0f} {exp_per_trade:>11,.0f} {dd:>10,.0f}")
        rows_out.append({"strategy": k, "name": names[k], "trades": n, "win_pct": win_pct, "gross": gross, "costs": costs, "net": net, "expectancy": exp_per_trade, "max_dd": dd})
    pd.DataFrame(rows_out).to_csv("backtest/backtest_summary.csv", index=False)
    print(f"\nCompleted in {time.time() - t0:.1f}s. Saved backtest/backtest_summary.csv")


if __name__ == "__main__":
    main()
