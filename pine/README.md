# Pine strategies

TradingView strategies derived from the project's edge research, written in
Pine Script v6 and tuned in TradingView's Strategy Tester.

## Headline result

**`nq_edge_final.pine`** — the carry-forward intraday strategy from the
Phase-3/4 framework analysis, tuned through 17 iterations in TV. On
`CME_MINI:NQ1!` 15-minute chart over ~11 months of available history:

| Metric | Value |
|---|---|
| **Profit factor** | **2.757** |
| **Win rate** | **67.74%** (63W / 30L) |
| **Max drawdown** | **0.69%** ($7,125) |
| Total trades | 93 |
| Total P&L (1 contract on $1M) | +$23,186 (+2.32%) |
| Avg win / avg loss | +0.11% / −0.09% |

Full iteration log: [`analysis/08_tradingview_iteration_results.md`](../analysis/08_tradingview_iteration_results.md).

## Files

| File | Timeframe | Status |
|---|---|---|
| [`nq_edge_final.pine`](nq_edge_final.pine) | 15m | **Production candidate** — tuned in TV (PF 2.757) |
| [`nq_edge_intraday.pine`](nq_edge_intraday.pine) | 15m | Same as `final` — kept under both names |
| [`nq_edge_daily.pine`](nq_edge_daily.pine) | 1D | NR7 daily breakout — Python backtest showed no edge after friction (kept for completeness) |

## How to run in TradingView

1. Open `CME_MINI:NQ1!` (or any NQ continuous front-month).
2. Set chart timeframe to **15m**.
3. Pine Editor → paste `nq_edge_final.pine` → Save → Add to chart.
4. Strategy Tester pane populates with metrics.

The defaults are the tuned-best parameters. Inputs are exposed for further
A/B testing — see the iteration log for what's already been tried.

## Why 15m and not lower timeframes?

We tested the same setup logic with 5m and 1m execution
([`analysis/09_timeframe_comparison.md`](../analysis/09_timeframe_comparison.md)):

| Timeframe | PF | Win rate | Trades |
|---|---|---|---|
| **15m** | **2.757** | 67.7% | **93** |
| 5m | 2.387 | 86.1% | 36 |
| 1m | n/a | 100% | 5 (insufficient sample) |

**15m wins on PF, sample size, and available TV history.** The 5m's higher
win rate (86%) is offset by 4.7× larger avg losses — fast bars don't give
the strategy room to buffer weak triggers. Setup-and-execution at the
setup's natural granularity is the right call.

## Inputs

| Input | Default | What it does |
|---|---|---|
| Target × 9:30 range past entry | **0.33** | Take profit at trigger + 0.33 × (9:30 H − 9:30 L). Tighter target = higher win rate, smaller wins. |
| Cancel pending entry after N 15m bars | **2** | If price hasn't broken the 9:30 H or L within 2 × 15min, cancel. Per source's D2: 91% of retests happen in the first bar. |
| Min 9:30 range / prior-day ATR(20) | **0.20** | Skip the trade if 9:30 candle is too narrow relative to the day's expected vol — there's no edge if the move is too small to overcome friction. |
| Max 9:30 range / prior-day ATR(20) | **0.50** | Skip the trade if 9:30 candle is unusually wide — likely a news / event day where the directional read is noisy. |

## Source signal

The strategy is the carry-forward from the project's Phase-3/4 framework
analysis. It implements the strongest empirically-significant edge in the
source data:

- **D4** (`extended-stats/04-conditional-on-color`): green 9:30 candle →
  74% probability the high is retested first; red 9:30 → 74% low retest first.
  Lift over the opposite-color base rate is +50 percentage points (n=230,
  BH-significant at q=0.10).
- **C1** (`930-followthrough`): when the predicted side does retest, the
  day closes in the predicted direction 72-80% of the time.
- **D2** (`extended-stats/02-time-to-retest`): 91% of retests happen within
  the first 15-minute bar after 9:30 closes — supporting the tight
  `maxBars=2` window.

## Key tuning lessons

1. **Tighter target wins.** The source's "78% close-green" stat describes
   the day's *direction*, not the *excursion past the trigger*. Most
   profitable trades resolve quickly with small ATR-relative moves. Target
   0.33× the 9:30 range nailed this (PF 1.897 vs 1.337 at 1.5×).
2. **ATR-relative range filter is the biggest single improvement.** Going
   from no filter to (0.20 ≤ 9:30 range / ATR ≤ 0.50) lifted PF from
   1.897 → 2.757. It removes both "no edge — too quiet" and "event day —
   directional read is noisy" failure modes.
3. **200 EMA filter actively hurts.** Forcing trade direction with the
   higher-timeframe trend dropped PF (1.416 → 1.154). The 9:30 retest edge
   is regime-stable; constraining direction kills half the trades.
4. **Wide-body filter over-restricts.** The Python work hypothesized that
   wide-body 9:30 candles (the source's strongest sub-bucket) would amplify
   the edge. In practice the filter cut trade count by 80% and dropped
   PF (1.337 → 1.219).

## Pre-live checklist (still open)

The TV strategy tester gives in-sample results on the data window TV serves
on 15m (~11 months). Before live deployment:

- [ ] **Out-of-sample test** with deeper data (Polygon / Databento / IQFeed)
- [ ] Walk-forward analysis (rolling 6-month train / 1-month test)
- [ ] Deflated Sharpe Ratio with N_trials = 17 (the iteration count)
- [ ] 60-session paper trade with full execution discipline
- [ ] Verify live results within 25% of backtest expectancy
- [ ] Kill-switch tested

See [`analysis/00_final_report.md`](../analysis/00_final_report.md) and
[`analysis/08_tradingview_iteration_results.md`](../analysis/08_tradingview_iteration_results.md)
for the full pre-live checklist and recommended next research.
