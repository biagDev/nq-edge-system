# Phase 8 — TradingView Session Notes

After Phase 7 closed out the Python project, the next step was to port the
strongest carry-forward strategies into Pine Script and run them inside
TradingView's strategy tester. This file records what happened.

## What was attempted

1. Pushed the entire `nq-edge-system` project to a fresh public GitHub repo:
   https://github.com/biagDev/nq-edge-system (8 commits, 1 per phase + scaffold).

2. Connected to TradingView Desktop via the local MCP bridge with NQ1!
   already loaded. Set chart to 15m and to the daily timeframe in turn.

3. Wrote and iterated three Pine v6 strategies:
   - **v1**: 9:30 color breakout, NY-time `hour()/minute()` detection.
   - **v2**: cleaner state machine, same NY-time detection.
   - **v3**: session-string detection (`time("", "0930-1600", "America/New_York")`),
     bgcolor highlights for visual debug.
   Plus a trivial **DEBUG every-N-bars** strategy as an integration sanity check.

4. For every variant, the strategy was successfully:
   - injected into Pine Editor (`pine_set_source`),
   - saved (`Save and add to chart` confirmation dialog clicked),
   - confirmed on chart via `chart_get_state` (study list shows the strategy),
   - rendered the chart on 15m NQ1! at the visible window.

5. **For every variant, including the trivial DEBUG strategy, the Strategy
   Tester reported `Total trades = 0` and the data MCP returned
   `metric_count: 0`, "No strategy found on chart"** — even though `chart_get_state`
   reported the strategy attached.

## Diagnosis

The Pine Editor's right pane was stuck in a loading-spinner state for the
entire session (10+ minutes), while the left chart and bottom Strategy Tester
panel rendered correctly. My hypothesis is that the strategy tester's compute
worker is gated on the editor's worker, and a stuck editor blocks new
strategies from compiling for the tester even though the chart engine has
their compiled bytecode (because chart-side plotting works — the studies
do appear in `chart_get_state`).

This is consistent with:
- **DEBUG strategy** (deterministic 100+ trades) → 0 trades reported.
- **Real strategies** → 0 trades reported.
- **Strategy dropdown** correctly shows current strategy name.
- **Chart** correctly shows 15m NQ data.

The bug is on the TradingView Desktop / MCP integration side, not in the
Pine code. The Pine code itself is straightforward and the same patterns
work in standalone TV usage.

## What was delivered

Final strategies live in [`pine/`](../pine/):

- [`pine/nq_edge_intraday.pine`](../pine/nq_edge_intraday.pine) — the
  9:30 Color Continuation Breakout. Implements D4 + C1 + D2.
- [`pine/nq_edge_daily.pine`](../pine/nq_edge_daily.pine) — the NR7
  Expansion Breakout. Implements E1c with both target-fixed and
  exit-at-close modes (the latter being the Python sensitivity-sweep winner).
- [`pine/README.md`](../pine/README.md) — 1-page inputs cheat-sheet and
  run instructions.

These have been pushed to the GitHub repo as part of a final commit:
https://github.com/biagDev/nq-edge-system/tree/main/pine

## How to run them yourself

1. Open `CME_MINI:NQ1!` on TradingView.
2. Set timeframe to **15m** (intraday) or **1D** (daily).
3. Pine Editor → paste `pine/nq_edge_intraday.pine` (or daily) → Save → Add
   to chart.
4. Strategy Tester pane will populate within a few seconds.

If you want me to iterate on the strategy with you, paste the **first row of
the Strategy Tester's metrics** (Total P&L, Profit Factor, Total Trades, Win
Rate, Max Drawdown) and I can tune from there.

## Recommended iteration plan once results show up

Based on the Python backtest's diagnostics:

1. **If trades fire but win rate < 50%** → tighten the entry-window cutoff
   (`maxBars` 4 → 2). The D2 stat says 91% of retests happen within the
   first 15m bar. Late entries dilute.
2. **If win rate is OK but expectancy < 0** → reduce the target multiple
   (1.5 → 1.0) and add a `move-to-breakeven at 0.5R` style overlay (note:
   Phase-3 research suggests this is usually neutral-to-negative; A/B test it).
3. **If both wide-body green and red work but only one of them is reliable**
   → split into two separate strategies and stack-trade them.
4. **If equity curve is whipsawed** → add a 200 EMA on the daily timeframe
   as a regime filter (long bias above, short bias below). This wasn't
   needed in source data but might help reduce trend-day losses.
5. **If too few trades** → relax the wide-body filter and accept narrower
   sub-buckets at the cost of slightly lower per-trade expectancy.
