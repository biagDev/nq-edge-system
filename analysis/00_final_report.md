# NQ Statistical Edge → Day Trading System — Final Report

**Project:** `nq-edge-system`
**Source repo:** [biagDev/data-collection](https://github.com/biagDev/data-collection) at SHA `92e5f9c`.
**Date:** 2026-04-27.

## TL;DR

We took 14 statistical studies on NQ futures from a research repo, applied
formal multiple-testing correction to 17 candidate edges, mapped the survivors
to the professional literature on auction theory, opening-range trading, and
short-horizon momentum, specified a daily-timeframe trading system from the
two strongest regime-stable signals (NR7 expansion + top-quartile extension),
and backtested it on 21 years of NQ daily bars.

**The system as specified is not live-deployable.** The combined backtest
produces a profit factor of 0.58, expectancy of −0.18R, and a 21-year CAGR of
−8.2%. The negative result is robust: 0 of 36 sensitivity-sweep parameter
combinations hit PF ≥ 1.1; both in-sample and out-of-sample agree
(IS-OOS expectancy drift = −0.002R); the random-entry benchmark performs
nearly identically.

The result is also **diagnostic, not nihilistic**. Three findings carry
forward:

1. The **NR7 signal is real but tiny** — when the 1.68× target is removed and
   trades exit at session close (only stop honoured), expectancy is +0.017R
   with PF 0.986 over 614 trades. The signal exists; daily friction eats it.
2. The 1.68× target was a **misframing of the source statistic**. The source's
   "next-day expands 1.68×" describes the full next-day range vs the NR7 day's
   range — *not* the excursion past the prior-day high. Anyone reading the
   source's stat as "1.68R reachable from a stop-buy at prior_H" is wrong;
   we now know that empirically.
3. The **most-framework-aligned edge (B1 + D4 intraday IB-retest fade) was not
   backtestable** because the source repo did not persist 15-minute bars and
   no free vendor offers deep 15m NQ history. This is the single most
   important next research step.

## What we did, in five lines

1. Cataloged every study in the source repo (Phase 1).
2. Computed Wilson CIs, two-proportion z-tests, BH-corrected p-values, and a
   tradeability score for 17 candidate edges; shortlisted 10 (Phase 2).
3. Researched professional frameworks (Auction Market Theory, Crabel, Fisher
   ACD, AQR, López de Prado, Tharp) and mapped each shortlist edge to its
   best-fitting framework (Phases 3-4).
4. Specified a two-strategy daily system (NR7 + Top-Q) with structural stops,
   targets, sizing, vol overlay, and stacking rules (Phase 5).
5. Backtested over 21 years of NQ=F daily bars with realistic friction,
   IS/OOS split, walk-forward, sensitivity sweep, and benchmarks (Phase 6).

## Edges that survived rigorous filtering

After Wilson CI and Benjamini-Hochberg FDR correction at q=0.10 on 17 tests,
ten edges survive. The headlines (sorted by Phase-2 tradeability score):

| Rank | Edge | k/n | Rate | Lift over null | BH-p |
|---|---|---|---|---|---|
| 1 | D4: red 9:30 → low retest first by 10:00 | 82/111 | 73.9% | +52.9pp vs green-day base | 0.000 |
| 2 | D4: green 9:30 → high retest first by 10:00 | 88/119 | 74.0% | +49.6pp | 0.000 |
| 3 | B1: 9-10am 1h candle either-side retest by 11:00 | 210/232 | 90.5% | +40.5pp vs 50% null | 0.000 |
| 4 | E1b: top-Q close → next-day higher high | 2071/2419 | 85.6% | +35.6pp | 0.000 |
| 5 | E1c: NR7 → next-day range expansion | 872/1044 | 83.5% | +33.5pp | 0.000 |
| 6 | E1b: bottom-Q close → next-day lower low | 1318/1598 | 82.5% | +32.5pp | 0.000 |
| 7 | B2: 6-10am 4h candle retest by 11:00 | 188/232 | 81.0% | +31.0pp | 0.000 |
| 8 | D1: prior-day H/L retested in first hour | 172/222 | 77.5% | +27.5pp | 0.000 |
| 9 | E1d: medium gap (25-50pt) fills same day | 119/176 | 67.6% | +17.6pp | 0.001 |
| 10 | D2: 9:30 retest within first 15m bar | 203/223 | 91.0% | +13.0pp vs first-30m null | 0.000 |

The full ranking, including the seven non-survivors and the 200MA
regime-condition test, is in [`analysis/02_edge_ranking.md`](02_edge_ranking.md).

## Edges that did NOT survive (and why)

- **C1 wide-body green 9:30 + high retest → green close** — score 1, BH-p 0.33, n=39.
  Lift +9.5pp not strong enough to clear FDR with that small n.
- **E2 top-Q + above-200MA → higher high** — BH-p 0.23. Counterintuitive
  result but consistent: top-Q already works regardless of regime (the
  "above-MA gives 85.9% vs below-MA 83.8%" lift is +2.1pp with n=1808/536,
  not significant). Good — top-Q doesn't need an MA filter.
- **E1a 4-green streak** — BH-significant but score 2 because v2 showed it's
  regime-dependent (only works above 200MA).
- Various small-n sub-buckets in C1.

## The strategy and its theoretical basis

We built two daily-timeframe strategies (full spec in
[`analysis/05_strategy_spec.md`](05_strategy_spec.md)):

**Primary — NR7 Expansion Breakout** (E1c, Crabel "Day Trading with Short
Term Price Patterns"). Day `t` qualifies as NR7 iff its range is the smallest
of the last 7 days. On day `t+1` we place stop orders 1 tick beyond the NR7
day's high (long) and low (short); first to fill wins. Stop = opposite NR7
extreme. Target = 1.68 × NR7 range past the trigger (the source's empirical
mean expansion ratio). Time-stop = session close.

**Secondary — Top-Q Extension Breakout** (E1b, AQR-style short-horizon
momentum). When today's close lands in the top quartile of today's range, we
pre-commit to long bias for tomorrow; stop-buy at today's high + 1 tick;
stop = today's high − 0.5 × today's range; target = today's high + 0.5 ×
today's range. Mirror logic for bottom-quartile closes.

**Stacking:** when both fire same direction, primary only (no double-sizing).
When opposite directions, both skipped. Sizing: 0.5% per-trade risk, 1.5%
concurrent cap, 15% annual vol-target overlay. Friction: $1.50 RT commission
+ 1 tick slippage per side on MNQ (the right product for a $100k account).

The theoretical basis (Phase 3): NR7 maps directly to Crabel's volatility-
contraction-expansion thesis. Top-Q maps to time-series momentum (Asness,
Moskowitz). Both are regime-stable per the source's 200MA split (E2), which
is why the spec doesn't gate them on regime.

## Backtest performance — full disclosure

**21 years of NQ=F daily bars (2005-01-03 → 2026-04-24, 5369 bars):**

| Metric | Combined | NR7 only | NR7 (no target) | TOPQ only | Buy & Hold | Random |
|---|---|---|---|---|---|---|
| n trades | 1,299 | 608 | 614 | 1,035 | — | ~1,250 |
| Win rate | 42.7% | 48.2% | 48.4% | 39.7% | — | 41% |
| Expectancy | −0.176R | +0.008R | +0.017R | −0.262R | — | −0.185R |
| Profit factor | 0.58 | 0.96 | 0.99 | 0.46 | — | 0.49 |
| CAGR | −8.2% | −0.3% | −0.1% | −9.5% | +2.0% | — |
| Sharpe | −1.77 | −0.08 | −0.01 | −2.30 | 0.72 | — |
| Max DD | −84.3% | — | −17.9% | — | −9.0% | — |

Full table, walk-forward years, sensitivity grid, and benchmarks:
[`analysis/06_backtest_results.md`](06_backtest_results.md).

**Sensitivity sweep:** 36 parameter combinations (target ±25%, stop ±25%,
friction 0.5×–2×). Min PF 0.31, median 0.52, max 0.72. **Zero combinations**
reach PF ≥ 1.1. The system isn't parameter-rescuable — the issue isn't tuning,
it's the underlying trade construction.

**IS/OOS:** in-sample expectancy −0.18R (n=1292), out-of-sample expectancy
−0.18R (n=502). Drift = −0.002R. The OOS performance is essentially identical
to in-sample, meaning the *negative* result is reliable and not a regime
artifact.

**Benchmarks:** the strategy's −0.18R expectancy is essentially indistinguishable
from random-entry benchmark of −0.19R. Buy-and-hold the underlying produced
+2% CAGR and a 0.72 Sharpe over the same window. The strategy underperforms
both the active alternative and passive ownership.

## Honest discussion of weaknesses

1. **Daily-bar fill ambiguity.** When both the stop and target lie inside
   day `t+1`'s range, we resolve as a stop-out. This biases results downward.
   With 15m intraday data the resolution would be exact.
2. **Source-stat misframing on target.** As discussed, "1.68× expansion" is
   the next-day full range, not excursion past the trigger. Our diagnostic
   (NR7 with no target, exit at close) confirms even the corrected exit only
   yields +0.017R — i.e. the issue is *also* signal weakness, not just exit
   choice.
3. **Daily-only operationalization.** The strongest *framework-fit* edges
   (B1, D1, D4 — auction-rotation retests) are intraday by construction.
   Without 15m bars they cannot be tested. The two daily edges that *were*
   tested (NR7, TOPQ) are the source's strongest *daily* edges but not the
   strongest in the whole catalog.
4. **N_trials = 17 in Phase 2, but model-selection N is bigger.** We picked
   2 of 10 shortlist edges as the spec, then ran 36 sensitivity combinations.
   The Deflated-Sharpe penalty (Phase 3 K) for that selection is real and
   would lower any apparent positive Sharpe — but our raw Sharpe is already
   negative, so DSR cannot rescue it.
5. **Vendor data integrity.** Yahoo `NQ=F` is a continuous front-month with
   contract-roll splice noise (~1.5% per source AUDIT.md). Effect is small
   but real. A Polygon/Databento pull would be cleaner for live deployment.
6. **No regime gate tested.** Both NR7 and TOPQ are regime-stable per E2, so
   we deliberately omitted a 200MA filter. Adding one might *narrow* the
   trade count without changing the per-trade expectancy. We did not test it.

## Pre-live checklist

This system is **NOT cleared for live trading**. The pre-live checklist is
written assuming a future iteration (likely B1+D4 intraday) does pass:

- [ ] Edge survives realistic friction in backtest (PF ≥ 1.1, expectancy ≥ +0.10R)
- [ ] Sensitivity sweep: ≥ 60% of param combos hit PF ≥ 1.1
- [ ] OOS performance within 25% of IS expectancy
- [ ] Walk-forward: positive expectancy in ≥ 60% of test years
- [ ] Beats random-entry benchmark by ≥ +0.10R per trade
- [ ] Beats buy-and-hold on Sharpe AND on max drawdown
- [ ] Deflated Sharpe Ratio computed and ≥ 0.5
- [ ] **Paper trade for 60 sessions** with full execution discipline; live
      results within 25% of backtest expectancy
- [ ] Kill-switch tested: 30-trade rolling win rate < 35% AND mean-R < −0.5R
      → halt; 20% account drawdown → halt
- [ ] Quarterly re-validation: re-fetch data, re-run all source stats, alert
      if any deviates by > 5pp from original sample
- [ ] Position sizing audit: no single trade > 1% of equity, aggregate
      concurrent risk ≤ 1.5%

## Recommended next research (priority order)

1. **Acquire 15-minute NQ RTH bar data**, ideally 5+ years deep. Vendors:
   Databento (paid, clean), Polygon (paid, clean), Firstrate (paid, OK),
   IQFeed (paid, real-time-quality historical). TradingView Desktop export
   is the source repo's path; the cap is ~11 months.

2. **Implement and backtest B1 + D4 intraday IB-retest fade.** This is the
   carry-forward strategy in Phase 5. Spec is already written; the stub at
   `src/strategy/intraday_b1_d4.py` is the entry point. Expected to be the
   most promising candidate based on Auction Market Theory framework fit and
   the +50pp lift in D4.

3. **Test directional follow-through (C1 wide-body)** with the larger
   intraday sample. The source's n=39 was the binding constraint; deeper data
   should produce a clean test.

4. **Re-test all source intraday stats** on the deeper sample, then re-run
   Phase 2 with much tighter Wilson CIs. Several "borderline" edges in our
   ranking will either consolidate or fall apart.

5. **Add a formal trend-day classifier** (D2 + IB-extension + 200MA
   composite) and re-test retest edges with the trend-day filter. This is
   specified in Phase 4 cross-cutting layer but uncoded.

6. **Investigate whether the daily NR7+TOPQ signal can be combined with an
   intraday execution layer** — e.g. NR7 setup, but only enter when the 9:30
   candle confirms direction. This converts a daily setup into a hybrid
   intraday trigger and may extract the +0.017R diagnostic signal we found.

7. **Apply purged k-fold CV + Deflated Sharpe** before any live deployment of
   any iteration. Phase 3 K is the methodology source.

## What this project produced

Independent of the trading verdict, the project produced:

- A **rigorous edge-ranking pipeline** (`src/stats/`) with Wilson CI, BH FDR,
  tradeability scoring — reusable for any future statistical research.
- A **complete framework-mapping document** (Phase 4) that links each edge
  to the academic and practitioner literature, with citations.
- A **daily-bar backtest engine** (`src/backtest/`) with no look-ahead,
  realistic friction, IS/OOS split, walk-forward, sensitivity sweep, and
  random/buy-hold benchmarks.
- A **strategy spec format** (Phase 5) faithful to the Tharp Setup-Trigger-
  Entry-Stop-Target-Sizing convention, mirrored in code.
- A **definitive empirical answer**: daily-timeframe operationalization of
  the source's daily NR7 / top-Q edges does not produce a tradeable system
  after realistic friction, even with corrected exit logic. The signal is
  ~+0.02R per trade — real but too small.

## Closing

The most important deliverable of this project is the *negative* result and
the *diagnostic* underneath it. The source repo's daily statistics are real
and replicable; what they do not directly imply is a profitable stop-and-
target strategy. The edge that matters most — D4 (color predicts retest side,
+50pp lift) — lives at the 15-minute timeframe and has not yet been put
through this same rigorous pipeline. That is the next thing to do.
