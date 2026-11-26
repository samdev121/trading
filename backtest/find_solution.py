"""
Quantitative Solution Finder on NIFTY 2026 1-Minute Data (135 sessions).
Tests institutional SL/Target mechanics (Net Spread Credit SL + Profit Targets)
under BOTH 0.5pt (Limit-order) and 1.0pt (Aggressive) slippage + full Groww charges.
"""
import time
import numpy as np
import pandas as pd
from backtest.run_backtest import (
    LOT_SIZE,
    calc_groww_charges,
    load_macro_signals,
    build_day_context,
    pick_strike_by_delta_proxy,
    get_leg_df,
)


def sim_spread_or_condor(
    bars_by_leg: list[tuple[str, pd.DataFrame]],
    qty: int,
    slip_pts: float,
    target_decay_pct: float,
    sl_credit_mult: float,
    cutoff_ts,
) -> dict | None:
    """
    Defined-risk spread/condor simulation using NET SPREAD MTM SL (sl_credit_mult x initial credit)
    instead of fragile 20% single-leg wick stops.
    """
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
        fill_entry = max(0.05, px - slip_pts) if direction == "SELL" else (px + slip_pts)
        legs.append({"dir": direction, "df": df, "entry_raw": px, "entry_fill": fill_entry})
        net_credit_raw += px if direction == "SELL" else -px

    if net_credit_raw <= 5.0:
        return None

    target_val = net_credit_raw * (1.0 - target_decay_pct)
    stop_val = net_credit_raw * (1.0 + sl_credit_mult)
    exit_ts = common_idx[-1]

    for ts in common_idx[1:]:
        cur_spread = 0.0
        for leg in legs:
            c = float(leg["df"].loc[ts, "close"])
            cur_spread += c if leg["dir"] == "SELL" else -c
        if cur_spread <= target_val or cur_spread >= stop_val:
            exit_ts = ts
            break

    gross_pnl = 0.0
    sell_to = 0.0
    buy_to = 0.0
    for leg in legs:
        c = float(leg["df"].loc[exit_ts, "close"])
        exit_fill = (c + slip_pts) if leg["dir"] == "SELL" else max(0.05, c - slip_pts)
        if leg["dir"] == "SELL":
            gross_pnl += (leg["entry_fill"] - exit_fill) * qty
            sell_to += leg["entry_fill"] * qty
            buy_to += exit_fill * qty
        else:
            gross_pnl += (exit_fill - leg["entry_fill"]) * qty
            buy_to += leg["entry_fill"] * qty
            sell_to += exit_fill * qty

    charges = calc_groww_charges(sell_to, buy_to, n_orders=len(legs) * 2)
    return {"net_pnl": gross_pnl - charges, "gross_pnl": gross_pnl, "charges": charges}


def sim_straddle_with_target(
    bars_by_leg: list[tuple[str, pd.DataFrame]],
    qty: int,
    slip_pts: float,
    leg_sl_pct: float,
    combined_target_pct: float,
    cutoff_ts,
) -> dict | None:
    """2-leg straddle/strangle with per-leg SL + breakeven trail + combined profit target."""
    common_idx = bars_by_leg[0][1].index.intersection(bars_by_leg[1][1].index)
    if cutoff_ts is not None:
        common_idx = common_idx[common_idx <= cutoff_ts]
    if len(common_idx) < 2:
        return None

    entry_ts = common_idx[0]
    legs = []
    tot_credit = 0.0
    for direction, df in bars_by_leg:
        px = float(df.loc[entry_ts, "close"])
        if px <= 2.0:
            return None
        legs.append({
            "df": df,
            "entry_raw": px,
            "entry_fill": max(0.05, px - slip_pts),
            "sl": px * (1.0 + leg_sl_pct),
            "closed": False,
            "exit_fill": None,
        })
        tot_credit += px

    exit_ts = common_idx[-1]
    for ts in common_idx[1:]:
        any_sl = False
        for leg in legs:
            if not leg["closed"] and float(leg["df"].loc[ts, "high"]) >= leg["sl"]:
                leg["exit_fill"] = max(leg["sl"], float(leg["df"].loc[ts, "open"])) + slip_pts
                leg["closed"] = True
                any_sl = True
        if any_sl:
            for leg in legs:
                if not leg["closed"]:
                    leg["sl"] = min(leg["sl"], leg["entry_raw"])
            if all(l["closed"] for l in legs):
                exit_ts = ts
                break

        # Combined target check (only if both still open, or realized+open >= target)
        cur_open_cost = sum(float(l["df"].loc[ts, "close"]) for l in legs if not l["closed"])
        realized_pts = sum(l["entry_raw"] - l["exit_fill"] for l in legs if l["closed"])
        open_entry_pts = sum(l["entry_raw"] for l in legs if not l["closed"])
        if (realized_pts + (open_entry_pts - cur_open_cost)) >= tot_credit * combined_target_pct:
            for leg in legs:
                if not leg["closed"]:
                    leg["exit_fill"] = float(leg["df"].loc[ts, "close"]) + slip_pts
                    leg["closed"] = True
            exit_ts = ts
            break

    for leg in legs:
        if not leg["closed"]:
            leg["exit_fill"] = float(leg["df"].loc[exit_ts, "close"]) + slip_pts
            leg["closed"] = True

    gross_pnl = sum((l["entry_fill"] - l["exit_fill"]) * qty for l in legs)
    sell_to = sum(l["entry_fill"] * qty for l in legs)
    buy_to = sum(l["exit_fill"] * qty for l in legs)
    charges = calc_groww_charges(sell_to, buy_to, n_orders=4)
    return {"net_pnl": gross_pnl - charges, "gross_pnl": gross_pnl, "charges": charges}


def main():
    t0 = time.time()
    macro = load_macro_signals("backtest/data/macro_daily.parquet")
    df = pd.read_parquet(
        "backtest/data/NIFTY_2026_intraday.parquet",
        columns=["date", "timestamp", "expiry", "strike", "option_type", "open", "high", "low", "close", "volume", "oi"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
    dates = sorted(df["date"].unique())
    by_expiry = {exp: grp for exp, grp in df.groupby("expiry")}
    by_date = {d: grp for d, grp in df.groupby("date")}

    configs = [
        ("S1_IC_50tgt_1xSL", "S1", 0.50, 1.0),
        ("S1_IC_80tgt_1xSL", "S1", 0.80, 1.0),
        ("S2_BP_50tgt_1xSL", "S2", 0.50, 1.0),
        ("S3_BC_50tgt_1xSL", "S3", 0.50, 1.0),
        ("S10_VWAP_50tgt_1xSL", "S10", 0.50, 1.0),
        ("S7_Straddle_20SL_30tgt", "S7", 0.30, 0.20),
        ("S8_IronFly_30tgt_1xSL", "S8", 0.30, 1.0),
    ]

    for slip in [0.5, 1.0]:
        buckets = {c[0]: [] for c in configs}
        for d in dates:
            day_df = by_date[d]
            exps = sorted([e for e in day_df["expiry"].unique() if e >= d])
            if not exps or d not in macro.index:
                continue
            nearest_exp = exps[0]
            dte = (pd.to_datetime(nearest_exp) - pd.to_datetime(d)).days
            pos_exp = exps[0] if dte >= 1 else (exps[1] if len(exps) > 1 else None)
            mrow = macro.loc[d]
            vix_prev = float(mrow["vix_prev"]) if pd.notna(mrow["vix_prev"]) else 14.0
            ivr_prev = float(mrow["ivr_prev"]) if pd.notna(mrow["ivr_prev"]) else 30.0
            g_bull, g_bear, g_quiet = bool(mrow["global_bull"]), bool(mrow["global_bear"]), bool(mrow["global_quiet"])

            ctx = build_day_context(day_df, nearest_exp)
            if ctx is None:
                continue
            entry_cands = ctx[(ctx.index.strftime("%H:%M") >= "10:00") & (ctx.index.strftime("%H:%M") <= "14:30")]
            if entry_cands.empty:
                continue

            exp_df_near = by_expiry[nearest_exp]
            eod_cutoff = pd.to_datetime(f"{d} 15:15:00")
            bull_hold = (entry_cands["spot"] > entry_cands["vwap"]) & (entry_cands["spot"] > entry_cands["max_pe_oi_strike"]) & (entry_cands["pcr"] >= 1.0)
            bear_hold = (entry_cands["spot"] < entry_cands["vwap"]) & (entry_cands["spot"] < entry_cands["max_ce_oi_strike"]) & (entry_cands["pcr"] <= 1.0)
            neutral_hold = (entry_cands["spot"] >= entry_cands["max_pe_oi_strike"]) & (entry_cands["spot"] <= entry_cands["max_ce_oi_strike"]) & (entry_cands["pcr"].between(0.85, 1.20))

            def first_bar(s):
                h = entry_cands[s]
                return h.index[0] if not h.empty else None

            # S1
            if pos_exp and ivr_prev > 35.0 and g_quiet:
                ts = first_bar(neutral_hold)
                if ts is not None:
                    spot = float(ctx.loc[ts, "spot"])
                    ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "CE", 0.13)
                    pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "PE", 0.13)
                    if ce_s and pe_s:
                        edf = by_expiry[pos_exp]
                        legs = [("SELL", get_leg_df(edf, ce_s, "CE", ts)), ("BUY", get_leg_df(edf, ce_s + 200, "CE", ts)), ("SELL", get_leg_df(edf, pe_s, "PE", ts)), ("BUY", get_leg_df(edf, pe_s - 200, "PE", ts))]
                        if all(l[1] is not None for l in legs):
                            for tgt, key in [(0.50, "S1_IC_50tgt_1xSL"), (0.80, "S1_IC_80tgt_1xSL")]:
                                r = sim_spread_or_condor(legs, LOT_SIZE, slip, tgt, 1.0, pd.to_datetime(f"{pos_exp} 15:15:00"))
                                if r:
                                    buckets[key].append(r)

            # S2
            if pos_exp and g_bull:
                ts = first_bar(bull_hold)
                if ts is not None:
                    spot = float(ctx.loc[ts, "spot"])
                    pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "PE", 0.27)
                    if pe_s:
                        edf = by_expiry[pos_exp]
                        legs = [("SELL", get_leg_df(edf, pe_s, "PE", ts)), ("BUY", get_leg_df(edf, pe_s - 200, "PE", ts))]
                        if all(l[1] is not None for l in legs):
                            r = sim_spread_or_condor(legs, LOT_SIZE, slip, 0.50, 1.0, pd.to_datetime(f"{pos_exp} 15:15:00"))
                            if r:
                                buckets["S2_BP_50tgt_1xSL"].append(r)

            # S3
            if pos_exp and g_bear:
                ts = first_bar(bear_hold)
                if ts is not None:
                    spot = float(ctx.loc[ts, "spot"])
                    ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == pos_exp], ts, spot, "CE", 0.27)
                    if ce_s:
                        edf = by_expiry[pos_exp]
                        legs = [("SELL", get_leg_df(edf, ce_s, "CE", ts)), ("BUY", get_leg_df(edf, ce_s + 200, "CE", ts))]
                        if all(l[1] is not None for l in legs):
                            r = sim_spread_or_condor(legs, LOT_SIZE, slip, 0.50, 1.0, pd.to_datetime(f"{pos_exp} 15:15:00"))
                            if r:
                                buckets["S3_BC_50tgt_1xSL"].append(r)

            # S10
            ts_b = first_bar(bull_hold) if g_bull else None
            ts_r = first_bar(bear_hold) if g_bear else None
            if ts_b is not None and (ts_r is None or ts_b <= ts_r):
                spot = float(ctx.loc[ts_b, "spot"])
                pe_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts_b, spot, "PE", 0.27)
                if pe_s:
                    legs = [("SELL", get_leg_df(exp_df_near, pe_s, "PE", ts_b)), ("BUY", get_leg_df(exp_df_near, pe_s - 200, "PE", ts_b))]
                    if all(l[1] is not None for l in legs):
                        r = sim_spread_or_condor(legs, LOT_SIZE, slip, 0.50, 1.0, eod_cutoff)
                        if r:
                            buckets["S10_VWAP_50tgt_1xSL"].append(r)
            elif ts_r is not None:
                spot = float(ctx.loc[ts_r, "spot"])
                ce_s = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts_r, spot, "CE", 0.27)
                if ce_s:
                    legs = [("SELL", get_leg_df(exp_df_near, ce_s, "CE", ts_r)), ("BUY", get_leg_df(exp_df_near, ce_s + 200, "CE", ts_r))]
                    if all(l[1] is not None for l in legs):
                        r = sim_spread_or_condor(legs, LOT_SIZE, slip, 0.50, 1.0, eod_cutoff)
                        if r:
                            buckets["S10_VWAP_50tgt_1xSL"].append(r)

            # S7
            if g_quiet:
                c7 = entry_cands[(entry_cands.index.strftime("%H:%M") >= "10:15") & (entry_cands.index.strftime("%H:%M") <= "12:30") & neutral_hold & ((entry_cands["spot"] - entry_cands["vwap"]).abs() / entry_cands["spot"] < 0.0025)]
                if not c7.empty:
                    ts = c7.index[0]
                    spot = float(ctx.loc[ts, "spot"])
                    atm_k = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts, spot, "CE", 0.50)
                    if atm_k:
                        legs = [("SELL", get_leg_df(exp_df_near, atm_k, "CE", ts)), ("SELL", get_leg_df(exp_df_near, atm_k, "PE", ts))]
                        if all(l[1] is not None for l in legs):
                            r = sim_straddle_with_target(legs, LOT_SIZE, slip, 0.20, 0.30, eod_cutoff)
                            if r:
                                buckets["S7_Straddle_20SL_30tgt"].append(r)

            # S8
            if vix_prev < 15.0 and g_quiet:
                ts = first_bar(neutral_hold)
                if ts is not None:
                    spot = float(ctx.loc[ts, "spot"])
                    atm_k = pick_strike_by_delta_proxy(day_df[day_df["expiry"] == nearest_exp], ts, spot, "CE", 0.50)
                    if atm_k:
                        legs = [("SELL", get_leg_df(exp_df_near, atm_k, "CE", ts)), ("SELL", get_leg_df(exp_df_near, atm_k, "PE", ts)), ("BUY", get_leg_df(exp_df_near, atm_k + 200, "CE", ts)), ("BUY", get_leg_df(exp_df_near, atm_k - 200, "PE", ts))]
                        if all(l[1] is not None for l in legs):
                            r = sim_spread_or_condor(legs, LOT_SIZE, slip, 0.30, 1.0, eod_cutoff)
                            if r:
                                buckets["S8_IronFly_30tgt_1xSL"].append(r)

        print(f"\n=== INSTITUTIONAL SL/TARGET SOLUTION TEST (Slippage: {slip} pt/fill | 1 Lot = 65 Qty) ===")
        print(f"{'Config':<26} {'Trades':>6} {'Win%':>7} {'Gross':>10} {'Costs':>8} {'Net':>10} {'Exp/Trd':>9} {'MaxDD':>9}")
        print("-" * 92)
        for name, *_ in configs:
            tdf = pd.DataFrame(buckets[name])
            if tdf.empty:
                continue
            n = len(tdf)
            wp = (tdf["net_pnl"] > 0).mean() * 100
            g, c, net = tdf["gross_pnl"].sum(), tdf["charges"].sum(), tdf["net_pnl"].sum()
            eq = tdf["net_pnl"].cumsum()
            dd = (eq - eq.cummax()).min()
            print(f"{name:<26} {n:>6} {wp:>6.1f}% {g:>10,.0f} {c:>8,.0f} {net:>10,.0f} {net/n:>9,.0f} {dd:>9,.0f}")

    print(f"\nDone in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
