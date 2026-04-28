# Pine strategies

Two TradingView strategies derived from the project's edge research, written
in Pine Script v6.

| File | Timeframe | Source signal | Status |
|---|---|---|---|
| [`nq_edge_intraday.pine`](nq_edge_intraday.pine) | 15m | D4 + C1 + D2 (9:30 color → retest → followthrough) | **Carry-forward primary** — best framework fit, strongest empirical lift (+50pp), unbacktested in Python (no 15m bars) |
| [`nq_edge_daily.pine`](nq_edge_daily.pine) | 1D | E1c (NR7 → next-day expansion) | Backtested in Python — fails after friction; included to mirror the Phase-5 spec |

## How to run in TradingView

1. Open `CME_MINI:NQ1!` (or any NQ continuous front-month) on the chart.
2. Set the chart timeframe to **15m** for the intraday strategy, **1D** for the
   daily one.
3. Open Pine Editor, paste the file's contents, click "Save", then "Add to chart".
4. Open the Strategy Tester pane to see metrics.

## Inputs cheat-sheet

### `nq_edge_intraday.pine`
- **Wide-body 9:30 only** — restrict to candles where body ≥ 50% of range
  (highest-conviction sub-bucket per source's C1 wide-body table).
- **Target multiple** — 1.5 default. Try 1.0–2.0; the Python sensitivity sweep
  hit local maxima around 1.0 for daily, but the intraday move past the
  trigger is meaningfully larger.
- **Max bars after 9:30** — entry-window length. 4 = 1 hour. Past 4 bars the
  D2 retest probability has plateaued (91% within first bar already).

### `nq_edge_daily.pine`
- **Use 1.68× target** — toggle off to exit at session close (the variant the
  Python diagnostic found marginally positive; PF 0.99 vs 0.96 with target).
- **200 SMA regime filter** — toggle on to only take longs above 200-day
  and shorts below. Per source's E2 the NR7 signal is regime-stable so this
  is informational, not edge-adding.

## Why these and not the others

The shortlist had 10 BH-significant edges (see
[`analysis/02_edge_ranking.md`](../analysis/02_edge_ranking.md)). We coded:

1. **NR7** because Python could backtest it with public daily data and we
   wanted a baseline for honesty (it failed → see [final report](../analysis/00_final_report.md)).
2. **9:30 color breakout** because Phase-3 framework research identified it
   as the highest-leverage edge under Auction Market Theory + Mark Fisher
   ACD frameworks, and the Python work could not test it without 15m bars.

The other shortlist edges (B1 1h-candle retest, D1 PDH/PDL retest, E1d gap
fills, etc.) are specified in [`analysis/04_edge_to_framework_mapping.md`](../analysis/04_edge_to_framework_mapping.md)
and can be coded as additional strategies when time permits.
