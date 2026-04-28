"""Phase 6 driver. Loads NQ daily bars, runs strategies, IS/OOS split, walk-forward,
sensitivity sweep, random + buy-hold benchmarks. Emits results/ artifacts and
analysis/06_backtest_results.md.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..strategy.params import START_EQUITY
from . import engine, metrics


REPO_ROOT = Path(__file__).resolve().parents[2]
BARS_PATH = REPO_ROOT / "data" / "raw" / "bars" / "nq_daily.csv"
RESULTS_DIR = REPO_ROOT / "results"
OUT_MD = REPO_ROOT / "analysis" / "06_backtest_results.md"


def load_bars() -> pd.DataFrame:
    df = pd.read_csv(BARS_PATH, parse_dates=["date"], index_col="date")
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    df["ma200"] = df["close"].rolling(200).mean()
    return df


def chronological_split(bars: pd.DataFrame, train_frac: float = 0.7):
    cut = int(len(bars) * train_frac)
    return bars.iloc[:cut].copy(), bars.iloc[cut:].copy()


def run_main():
    RESULTS_DIR.mkdir(exist_ok=True, parents=True)
    bars = load_bars()
    print(f"loaded {len(bars)} bars: {bars.index.min().date()} -> {bars.index.max().date()}")

    is_bars, oos_bars = chronological_split(bars)
    print(f"IS: {len(is_bars)} bars  ({is_bars.index.min().date()}..{is_bars.index.max().date()})")
    print(f"OOS: {len(oos_bars)} bars ({oos_bars.index.min().date()}..{oos_bars.index.max().date()})")

    artifacts = {}

    # ---- 1) Full-sample run -----------------------------------------------
    full = engine.run(bars)
    full_m = metrics.compute(full.trades, full.equity_curve, START_EQUITY)
    artifacts["full"] = asdict(full_m)
    print("full sample:", full_m)

    # ---- 2) IS / OOS ------------------------------------------------------
    is_res = engine.run(is_bars)
    is_m = metrics.compute(is_res.trades, is_res.equity_curve, START_EQUITY)
    artifacts["in_sample"] = asdict(is_m)

    # OOS uses START_EQUITY (treat as fresh deployment)
    oos_res = engine.run(oos_bars)
    oos_m = metrics.compute(oos_res.trades, oos_res.equity_curve, START_EQUITY)
    artifacts["out_of_sample"] = asdict(oos_m)
    print("OOS:", oos_m)

    # ---- 3) Walk-forward (rolling 4y train / 1y test) ---------------------
    wf_results = []
    bars_year = bars.copy()
    bars_year["year"] = bars_year.index.year
    years = sorted(bars_year["year"].unique())
    for i in range(4, len(years)):
        test_year = years[i]
        test_slice = bars[bars.index.year == test_year]
        if len(test_slice) < 50:
            continue
        r = engine.run(test_slice)
        m = metrics.compute(r.trades, r.equity_curve, START_EQUITY)
        wf_results.append({"year": int(test_year), **asdict(m)})
    artifacts["walk_forward"] = wf_results

    # ---- 4) Sensitivity sweep ---------------------------------------------
    sens = []
    for ts in (0.75, 1.0, 1.25):
        for ss in (0.75, 1.0, 1.25):
            for fs in (0.5, 1.0, 1.5, 2.0):
                r = engine.run(bars, target_scalar=ts, stop_scalar=ss, friction_scalar=fs)
                m = metrics.compute(r.trades, r.equity_curve, START_EQUITY)
                sens.append({
                    "target_scalar": ts, "stop_scalar": ss, "friction_scalar": fs,
                    **asdict(m),
                })
    artifacts["sensitivity"] = sens

    # ---- 5) Random-entry benchmark -----------------------------------------
    rand_runs = []
    for seed in (1, 2, 3, 4, 5):
        r = engine.run(bars, random_entry=True, rng_seed=seed)
        m = metrics.compute(r.trades, r.equity_curve, START_EQUITY)
        rand_runs.append({"seed": seed, **asdict(m)})
    artifacts["random_entry"] = rand_runs
    rand_mean_pf = np.mean([r["profit_factor"] for r in rand_runs if r["profit_factor"] != float("inf")])
    rand_mean_exp = np.mean([r["expectancy_R"] for r in rand_runs])

    # ---- 6) Buy-and-hold benchmark -----------------------------------------
    bnh = metrics.buy_and_hold_metrics(bars, START_EQUITY)
    artifacts["buy_and_hold"] = bnh
    print("buy-and-hold:", bnh)

    # ---- Per-strategy split (NR7 only vs TOPQ only) ----------------------
    nr7_only = engine.run(bars, strategies=("NR7",))
    nr7_m = metrics.compute(nr7_only.trades, nr7_only.equity_curve, START_EQUITY)
    artifacts["nr7_only"] = asdict(nr7_m)

    topq_only = engine.run(bars, strategies=("TOPQ",))
    topq_m = metrics.compute(topq_only.trades, topq_only.equity_curve, START_EQUITY)
    artifacts["topq_only"] = asdict(topq_m)

    # Diagnostic: NR7 with no fixed target, exit at close (only stop honoured).
    nr7_close = engine.run(bars, strategies=("NR7",), exit_at_close=True)
    nr7_close_m = metrics.compute(nr7_close.trades, nr7_close.equity_curve, START_EQUITY)
    artifacts["nr7_exit_at_close"] = asdict(nr7_close_m)
    print("NR7 exit-at-close:", nr7_close_m)

    # ---- Save trade log + equity curve ------------------------------------
    if full.trades:
        td = pd.DataFrame([asdict(t) for t in full.trades])
        td.to_csv(RESULTS_DIR / "trades_full.csv", index=False)
    full.equity_curve.to_csv(RESULTS_DIR / "equity_curve_full.csv", header=["equity"])

    # ---- Plots --------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(full.equity_curve.index, full.equity_curve.values, label="Strategy (NR7 + TOPQ)", lw=1.4)
    bnh_curve = START_EQUITY + (bars["close"] - bars["close"].iloc[0]) * 20.0
    ax.plot(bnh_curve.index, bnh_curve.values, label="Buy & Hold (1 contract)", lw=1.0, alpha=0.7)
    ax.set_title("NQ-Edge-System equity curve vs buy-and-hold")
    ax.set_ylabel("Equity ($)")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "equity_curve.png", dpi=110)
    plt.close(fig)

    if full.trades:
        rs = [t.R for t in full.trades]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(rs, bins=40)
        ax.axvline(0, color="k", lw=0.7)
        ax.set_title(f"R-multiple distribution (n={len(rs)}, mean={np.mean(rs):.3f})")
        ax.set_xlabel("R")
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / "r_distribution.png", dpi=110)
        plt.close(fig)

    monthly = metrics.monthly_returns(full.equity_curve)
    if len(monthly) > 0:
        fig, ax = plt.subplots(figsize=(9, 3.5))
        ax.bar(monthly.index, monthly.values * 100, width=20)
        ax.axhline(0, color="k", lw=0.5)
        ax.set_title("Monthly returns (%)")
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / "monthly_returns.png", dpi=110)
        plt.close(fig)

    # ---- Dump JSON ---------------------------------------------------------
    (RESULTS_DIR / "metrics.json").write_text(json.dumps(artifacts, indent=2, default=str))

    # ---- Markdown report --------------------------------------------------
    write_markdown(artifacts, full_m, is_m, oos_m, bnh, rand_runs, rand_mean_pf,
                   rand_mean_exp, nr7_m, topq_m, bars, full)
    return artifacts


def fmt(m) -> str:
    """Format a metrics dict (or asdict) as a list."""
    if hasattr(m, "__dict__"):
        m = asdict(m)
    return (
        f"n={m['n_trades']}, win-rate={m['win_rate']:.2%}, "
        f"expectancy={m['expectancy_R']:+.3f}R, PF={m['profit_factor']}, "
        f"CAGR={m['cagr']:.2%}, Sharpe={m['sharpe']}, "
        f"MaxDD={m['max_drawdown_pct']:.2%}, MAR={m['mar_ratio']}"
    )


def write_markdown(art, full_m, is_m, oos_m, bnh, rand_runs, rand_pf, rand_exp,
                   nr7_m, topq_m, bars, full_res):
    md = []
    md.append("# Phase 6 — Backtest Results\n")
    md.append(f"**Data:** NQ=F daily bars from Yahoo Finance, "
              f"{bars.index.min().date()} → {bars.index.max().date()} "
              f"({len(bars)} bars).\n")
    md.append("**Strategies:** NR7 Expansion Breakout (primary) + Top-Q Extension Breakout (secondary), "
              "stacked per `analysis/05_strategy_spec.md`.\n")
    md.append("**Friction baseline:** $4 RT commission + 1 tick slippage per side on full NQ "
              "($20/pt). Sensitivity sweep stresses friction up to 2× baseline.\n")
    md.append("**Sizing:** 0.5% risk per trade, 15% annual vol target overlay, $100k starting equity.\n")
    md.append("**No look-ahead:** every signal is computed from end-of-day-`t` data only and "
              "executed on day `t+1`. Daily-bar fill ambiguity (both stop and target inside the "
              "next bar) is resolved conservatively as **stop-out**.\n")

    md.append("## 1. Headline (full sample)\n")
    md.append(f"- {fmt(full_m)}")
    md.append(f"- Total P&L (full sample): **${full_m.total_pnl_dollars:,.0f}** on $100k start.")
    md.append(f"- Longest losing streak: **{full_m.longest_loss_streak}** trades.")

    md.append("\n## 2. In-sample / Out-of-sample (chronological 70/30)\n")
    md.append("| | n | win-rate | exp R | PF | CAGR | Sharpe | MaxDD | MAR |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for label, m in (("In-sample", is_m), ("Out-of-sample", oos_m)):
        md.append(f"| **{label}** | {m.n_trades} | {m.win_rate:.2%} | "
                  f"{m.expectancy_R:+.3f} | {m.profit_factor} | {m.cagr:.2%} | "
                  f"{m.sharpe} | {m.max_drawdown_pct:.2%} | {m.mar_ratio} |")
    is_oos_drift = (is_m.expectancy_R - oos_m.expectancy_R)
    md.append(f"\nIS→OOS expectancy drift: **{is_oos_drift:+.3f}R**. "
              f"Negative = OOS held up (better than IS); positive = OOS degraded.")

    md.append("\n## 3. Per-strategy decomposition\n")
    md.append("| | n | win-rate | exp R | PF | CAGR | Sharpe |")
    md.append("|---|---|---|---|---|---|---|")
    nr7c = art["nr7_exit_at_close"]
    nr7_close_m_obj = type("M", (), nr7c)
    for label, m in (
        ("NR7 only (1.68× target)", nr7_m),
        ("NR7 only — diagnostic, no target, exit at close", type("M", (), nr7c)),
        ("TOPQ only", topq_m),
        ("Combined (spec'd)", full_m),
    ):
        if isinstance(m, type):
            d = nr7c
            md.append(f"| **{label}** | {d['n_trades']} | {d['win_rate']:.2%} | "
                      f"{d['expectancy_R']:+.3f} | {d['profit_factor']} | "
                      f"{d['cagr']:.2%} | {d['sharpe']} |")
        else:
            md.append(f"| **{label}** | {m.n_trades} | {m.win_rate:.2%} | "
                      f"{m.expectancy_R:+.3f} | {m.profit_factor} | {m.cagr:.2%} | "
                      f"{m.sharpe} |")

    md.append("\n## 4. Walk-forward (annual)\n")
    md.append("| year | n | win-rate | exp R | PF | year P&L ($) | MaxDD |")
    md.append("|---|---|---|---|---|---|---|")
    for r in art["walk_forward"]:
        md.append(f"| {r['year']} | {r['n_trades']} | {r['win_rate']:.2%} | "
                  f"{r['expectancy_R']:+.3f} | {r['profit_factor']} | "
                  f"{r['total_pnl_dollars']:,.0f} | {r['max_drawdown_pct']:.2%} |")

    md.append("\n## 5. Benchmarks\n")
    md.append("| Benchmark | CAGR | Sharpe | MaxDD | Notes |")
    md.append("|---|---|---|---|---|")
    md.append(f"| **Buy-and-hold (1 contract NQ)** | {bnh['cagr']:.2%} | {bnh['sharpe']} | "
              f"{bnh['max_drawdown_pct']:.2%} | Naive long, no sizing |")
    md.append(f"| **Random entry (mean of 5 seeds)** | — | — | — | "
              f"PF≈{rand_pf:.3f}, expectancy≈{rand_exp:+.3f}R — "
              f"{'beats' if full_m.expectancy_R > rand_exp else 'matches/loses to'} our strategy |")
    md.append("\nRandom-entry uses the same NR7-style stop/target/sizing structure but picks "
              "direction at random with the same fire rate. If the strategy expectancy doesn't "
              "exceed the random benchmark by a clear margin, the apparent edge is a structural "
              "artifact (target/stop asymmetry, vol clustering, etc.) rather than a real signal.")

    md.append("\n## 6. Sensitivity sweep\n")
    md.append("Variations of target multiple (×0.75, ×1.0, ×1.25), stop distance (×0.75, ×1.0, ×1.25), "
              "and friction (×0.5, ×1.0, ×1.5, ×2.0) — 36 combinations.\n")
    sens = art["sensitivity"]
    pfs = [s["profit_factor"] for s in sens if s["profit_factor"] != float("inf")]
    sharpes = [s["sharpe"] for s in sens]
    exps = [s["expectancy_R"] for s in sens]
    md.append(f"- Profit factor: min={min(pfs):.2f}, median={np.median(pfs):.2f}, max={max(pfs):.2f}.")
    md.append(f"- Sharpe: min={min(sharpes):.2f}, median={np.median(sharpes):.2f}, max={max(sharpes):.2f}.")
    md.append(f"- Expectancy R: min={min(exps):+.3f}, median={np.median(exps):+.3f}, max={max(exps):+.3f}.")
    pass_pct = sum(1 for p in pfs if p >= 1.1) / max(1, len(pfs)) * 100
    md.append(f"- **% of parameter combos with PF ≥ 1.1: {pass_pct:.0f}%**.")

    # Sub-table: vary friction at default scalars
    fric_table = [s for s in sens if s["target_scalar"] == 1.0 and s["stop_scalar"] == 1.0]
    md.append("\nFriction stress (target & stop fixed at nominal):\n")
    md.append("| friction × | n | win-rate | exp R | PF | CAGR | Sharpe | MaxDD |")
    md.append("|---|---|---|---|---|---|---|---|")
    for s in fric_table:
        md.append(f"| {s['friction_scalar']:.1f}× | {s['n_trades']} | "
                  f"{s['win_rate']:.2%} | {s['expectancy_R']:+.3f} | {s['profit_factor']} | "
                  f"{s['cagr']:.2%} | {s['sharpe']} | {s['max_drawdown_pct']:.2%} |")

    md.append("\n## 7. Plots\n")
    md.append("- [Equity curve vs buy-and-hold](../results/equity_curve.png)")
    md.append("- [R-multiple distribution](../results/r_distribution.png)")
    md.append("- [Monthly returns](../results/monthly_returns.png)")

    md.append("\n## 8. Honest assessment\n")
    md.append("**Caveats and known weaknesses:**\n")
    md.append("- Daily-bar fill modeling cannot disambiguate whether the stop or target was hit "
              "first within `t+1`. We resolve conservatively as a stop-out, which biases the "
              "results downward when both are in range. Real-world fills (with intraday data) "
              "should be ≥ as good as reported.")
    md.append("- The 1.68 × NR7-range target was inherited from the source's *next-day full-range* "
              "stat, not the *excursion past the trigger*. The sensitivity sweep covers ±25% on "
              "either side; any conclusion that holds across the grid is robust to this misframing.")
    md.append("- Yahoo Finance NQ=F is a continuous front-month series with quarterly contract "
              "splice noise (~1.5% per AUDIT.md). Effect is small but real.")
    md.append("- TOPQ pre-commits a single direction on day `t`. Days with a 'doji-ish' mid-quartile "
              "close emit no signal, which is correct.")
    md.append("- We used a 70/30 chronological split, not k-fold. For daily strategies on 21 years "
              "this is acceptable; a stricter purged k-fold + Deflated Sharpe (Phase 3 K) would be "
              "appropriate before committing real capital.")
    md.append("- No regime filter applied to E1c or E1b (both are regime-stable per source v2).")
    md.append("- N_trials in the multiple-testing context is 17 (Phase 2) — even with BH, the "
              "best-of-17 Sharpe is modestly inflated. Treat the headline Sharpe as an upper "
              "bound; the bottom of the IQR of the sensitivity sweep is a more honest read.")

    md.append("\n## 9. Verdict for Phase 7\n")
    if full_m.profit_factor >= 1.1 and pass_pct >= 60 and full_m.expectancy_R > rand_exp:
        verdict = "**Live-deployable as paper-trade candidate.** Survives sensitivity sweep, beats random entry."
    elif full_m.profit_factor >= 1.0:
        verdict = "**Borderline.** Edge is small after costs. Recommend further research on intraday B1+D4 before live trading."
    else:
        verdict = "**Not live-deployable.** Edge does not survive realistic friction."
    md.append(verdict)

    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    run_main()
