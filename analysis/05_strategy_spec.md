# Phase 5 — Strategy Specification

This file is the source of truth for what the system trades. It must be
unambiguous enough to translate directly to code (and `src/strategy/` does
exactly that). Anything not specified here is **out of scope**.

## Decision rationale

We pick **two daily-timeframe strategies** that we can actually backtest
end-to-end with publicly available NQ daily bars:

1. **Primary — NR7 Expansion Breakout** (E1c). Crabel framework, regime-stable,
   n=1044. Daily setup, next-session trigger, structural stop, vol-implied target.
2. **Secondary — Top-Quartile Extension Breakout** (E1b). AQR-style short-horizon
   momentum, n=2419, regime-stable. Same trigger style, different setup.

Edges relegated to **future research** (specified but not coded for the initial
backtest):

- **NR7 + Top-Q stacked** (intersection set) — should appear as a separate
  trade only if both setups fire and direction agrees; lower n but very high
  conviction.
- **B1 (1h auction-rotation fade) + D4 directional read** — requires 15m intraday
  bars, which the source repo does not provide and we cannot fetch from a free
  vendor in arbitrary depth. Spec preserved here; code stub only.

## Universe and session

- **Instrument:** `CME_MINI:NQ1!` (Nasdaq-100 e-mini front-month continuous).
  Backtest uses Yahoo Finance `NQ=F` daily as the proxy data source. The
  underlying contract behaviour is identical at daily granularity; small
  differences from quarterly contract roll splicing are accepted (per source
  AUDIT.md Issue 3, ~1.5% noise).
- **Session:** Daily timeframe. Each "bar" is one CME settlement day (close
  ~17:00 ET, then Sunday-Friday session structure). We do not subset to RTH
  for the daily strategies — the daily bar is the unit of analysis.
- **Lookback for indicators:** 200 daily bars (200MA), 7 daily bars (NR7
  detection), 20 daily bars (range-position normalizer if needed).

## Cost model (applies to all strategies)

Per `src/stats/edge.py`:

- $4 round-trip commission per contract (full NQ).
- 1 tick (0.25 pts) slippage per side.
- Total round-trip friction ≈ **0.7 pts** ≈ **$14 per contract**.
- $20/pt for full NQ. Backtest equity assumes 1-contract sizing scaled by the
  position-sizing rule below.

For sensitivity, the backtest reruns with friction scaled to 0.5×, 1.0×, 1.5×, 2.0×
the default. Edge is "real" only if it survives 1.5× friction.

## Position sizing (applies to all strategies)

- **Account size assumption:** $100,000 starting equity.
- **Risk per trade:** **0.5% of current equity** = $500 at start.
- **Position size:** `floor(risk_$ / (stop_distance_pts × $20))`. Minimum 1
  contract. If 1 contract exceeds the risk budget (rare for NR7 days), trade is
  skipped.
- **Aggregate concurrent risk cap:** 1.5%. If primary and secondary both fire
  same direction same day, only the higher-conviction (= primary) position is
  taken; the secondary signal is logged but not traded.
- **Vol target overlay:** equity-curve vol target of 15% annualized — if the
  trailing-30-day realized vol of the equity curve exceeds 15%, scale all new
  positions by `(15% / realized_vol)`. Floor at 0.25× and cap at 1.5×.

## Filters (applies to all strategies)

- **News blackout:** none in v1 (we don't have a news calendar in the source
  data; Phase 7 carryforward).
- **Holiday blackout:** skip trade if next-session bar is missing or has
  range < 25 NQ points (likely a half-day; Phase 1 AUDIT.md Issue 4).
- **Regime gate (200MA):** *not used* on E1c or E1b — both are regime-stable
  per E2. (We will report results split by regime as a robustness check.)
- **Failure conditions / kill switch:**
  - 30-trade rolling win rate drops below 35% AND mean-R drops below −0.5R →
    pause new entries, alert.
  - Equity drawdown exceeds 20% from peak → pause new entries.

---

## Strategy 1 (PRIMARY) — NR7 Expansion Breakout

### Setup (fires at end-of-day t)

A day `t` is an **NR7** day iff:

```
range(t) == min(range(t-6 .. t))           # today's range is the smallest of last 7
range(t) > 0                               # sanity
```

where `range(t) = high(t) - low(t)` of the daily bar.

### Trigger (evaluated bar-by-bar on day t+1)

The setup goes live at session open of day `t+1`. We watch for a break of
either NR7-day extreme:

- **Long trigger:** during day `t+1`, price prints `high >= prior_high + 1 tick`
  where `prior_high = high(t)` (the NR7 day's high).
- **Short trigger:** during day `t+1`, price prints `low <= prior_low - 1 tick`.

In daily-bar backtest terms:
- Long fills if `high(t+1) > prior_high`. Fill price = `prior_high + 1 tick`
  (modelling a stop order).
- Short fills if `low(t+1) < prior_low`. Fill price = `prior_low - 1 tick`.
- **First trigger wins.** If both `high(t+1) > prior_high` and
  `low(t+1) < prior_low` (NR7-day-engulfing outside bar), use the **higher-conviction
  side**: the side aligned with the daily 200MA bias (above MA → long; below →
  short). If no 200MA bias (close == 200MA exactly), skip.

### Entry

Stop order at `prior_high + 1 tick` (long) or `prior_low - 1 tick` (short).
Daily-bar fill modelling assumes the stop is hit and we receive the fill at
the stop price + 1 tick of slippage (so net entry = `prior_high + 2 ticks` for
a long).

### Invalidation (stop loss)

Hard stop at the **opposite extreme of the NR7 day**:

- Long: stop at `low(t)` (the NR7-day low). Risk = `prior_high + 1 tick - low(t)`.
- Short: stop at `high(t)`. Risk = `high(t) - (prior_low - 1 tick)`.

This is structural — it's the level that, if breached, falsifies the NR7
expansion hypothesis (we'd be back inside the contraction range from the wrong
side).

In the daily-bar backtest, the stop is checked *after* the entry trigger:
if both extremes are hit on day `t+1`, the trade is assumed to enter then stop
out same day for a full risk loss (the backtest is intentionally conservative
on this ambiguity).

### Target

`1.68 × NR7_range` past the entry trigger (i.e. `prior_high + 1.68 × range(t)`
for a long). The 1.68 factor is the **empirical mean expansion ratio** from
`daily-patterns-v1`'s NR7 stat. This makes the target structurally tied to the
edge magnitude, not arbitrary.

### Time-based exit

If neither stop nor target hits by the close of day `t+1`, exit at session
close of `t+1` at the closing price.

### Cancellation rule

If the trigger does not fire on day `t+1` (neither stop is filled), the setup
is cancelled. It does **not** carry forward to day `t+2`.

### Expected statistics (backtest hypothesis)

- 83.5% of NR7 days expand → triggers fire on most (n weighted: ~84% of NR7s).
- Of triggered trades: ~50/50 long/short by symmetry, with possibly slight
  long bias (E1c says next-day green 55.9%).
- Average target reach: `1.68R` if hit, but most won't hit a 1.68R target — the
  expectancy depends on the distribution of expansion magnitudes, which we
  measure in Phase 6.
- Pre-cost expected R per trade: positive but uncertain (the stat says
  expansion happens, not that it reaches 1.68R *past entry*; the 1.68R is the
  next day's *full* range vs the NR7 range).

This last point is critical and is a known weakness of the spec: the **1.68 ×
NR7 range** is the next day's *full range*, not the *excursion past prior H/L*.
The actual MFE past the entry trigger is smaller. Phase 6 will measure this
and may need to retune the target. Sensitivity sweep covers ±25% of target.

---

## Strategy 2 (SECONDARY) — Top-Quartile Extension Breakout

### Setup (fires at end-of-day t)

Day `t` qualifies iff:

```
close(t) - low(t) >= 0.75 × (high(t) - low(t))    # close in top quartile of range
range(t) > 0
```

Mirror condition for short bias:

```
high(t) - close(t) >= 0.75 × (high(t) - low(t))   # close in bottom quartile
```

### Trigger (day t+1)

- Long trigger: `high(t+1) > high(t)` (a higher high prints).
- Short trigger: `low(t+1) < low(t)` (a lower low prints).

The setup pre-commits to the long or short side at `t` close based on
top-Q vs bottom-Q.

### Entry

Stop order at `high(t) + 1 tick` (long) or `low(t) - 1 tick` (short).

### Invalidation (stop)

`prior_high - 0.5 × prior_range` for longs (= `high(t) - 0.5 × range(t)`).
Mirror for shorts. Structural: half-retracement of the entire prior day.

### Target

`prior_high + 0.5 × prior_range` (long), mirror for shorts. Time-stop at session
close of `t+1`.

### Time-based exit

Close on `t+1` if neither stop nor target hits.

### Cancellation rule

Setup is one-shot — if not triggered on `t+1`, dead.

### Expected behaviour

E1b reports 85.6% next-day higher-high after top-Q close (n=2419). That's the
*trigger fire rate*, not the win rate. Once triggered, the trade resolves
between the +0.5R target and the −1.0R-ish stop (depending on prior-day range
size). The backtest will measure the full distribution.

---

## Strategy stacking rules

When primary and secondary both fire on the same day-`t` close:

- **Same direction (both long or both short):** trade the **primary only** with
  the primary's stop and target. Secondary is logged but not traded (avoids
  double-sizing on correlated signals — AQR ERC principle).
- **Opposite direction:** **both are skipped.** The setups disagree, so we
  defer to "no edge today."

When neither fires: no trade.

When only one fires: that one trades on its own rules.

## Failure / kill-switch behaviour

- 30-trade rolling: after 30 closed trades, if `win_rate < 0.35` AND
  `mean_R < -0.5`, halt new entries until the trader manually re-enables.
- 20% drawdown from equity peak: halt new entries until trader re-enables.
- Spec drift: if the source repo's NR7 stats deviate from a re-fetched 27-year
  sample by > 5pp on next quarterly review, the parameters are stale and the
  system pauses for re-spec.

## Carry-forward (specified, not coded for v1 backtest)

### B1 + D4 — Intraday IB-retest fade

(Specified here so the rules are recorded; code stub in
`src/strategy/intraday_b1_d4.py`. Activation requires 15m bars.)

- **Setup (10:00 ET):** classify 9:30 candle (color, body wide/narrow);
  identify 9:00-10:00 1h candle H1/L1.
- **D4 directional read:** green 9:30 → bias long (looking for L1 retest),
  red 9:30 → bias short (looking for H1 retest).
- **Trigger:** price extends beyond H1 or L1 between 10:00 and 11:30, then
  closes a 5-min bar back inside.
- **Entry:** market on confirmation, or limit at H1/L1 on first touch from
  outside.
- **Stop:** 0.5 × IB above H1 (mirror for L1).
- **Target:** opposite extreme of the 1h candle.
- **Time stop:** 12:00 ET.
- **Trend-day suppressor:** if 9:30 candle has not been retested by 10:00
  (D2 trend-day flag), do not take this trade.
- **Sizing:** 0.5% risk, same as primary.

### NR7 + Top-Q intersection (high-conviction)

If both fire same direction on same day, take primary's risk + half-size on
secondary's stop/target — net 0.75% risk, two distinct exits. Backtest will
revisit once the v1 results are in.

## Implementation map

| Spec section | Code module |
|---|---|
| NR7 setup detection | `src/strategy/nr7.py:is_nr7_day` |
| NR7 trade construction | `src/strategy/nr7.py:nr7_signal` |
| Top-Q setup detection | `src/strategy/topq.py:topq_class` |
| Top-Q trade construction | `src/strategy/topq.py:topq_signal` |
| Position sizing | `src/strategy/sizing.py:position_size` |
| Stacking rule | `src/strategy/stack.py:combine` |
| Cost model | `src/stats/edge.py:round_trip_cost_points` (re-used) |
| Backtest engine | `src/backtest/engine.py` |
| Metrics | `src/backtest/metrics.py` |

## Parameters (single point of edit)

```python
# src/strategy/params.py
NR7_LOOKBACK = 7
NR7_TARGET_MULTIPLE = 1.68      # mean expansion ratio
TOPQ_THRESHOLD = 0.75            # quartile cutoff
TOPQ_TARGET_FRAC = 0.5           # of prior-day range
TOPQ_STOP_FRAC = 0.5             # of prior-day range
RISK_PER_TRADE_FRAC = 0.005      # 0.5% of equity
AGGREGATE_RISK_CAP_FRAC = 0.015  # 1.5%
VOL_TARGET_ANNUAL = 0.15
TICK_SIZE = 0.25
DOLLAR_PER_POINT = 20.0
COMMISSION_RT = 4.0
SLIPPAGE_TICKS = 1.0             # per side
```

## Sensitivity grid (Phase 6 will sweep)

- Target multiple: `0.75 ×` to `1.25 ×` of nominal (1.26 → 2.10 for NR7).
- Stop distance: `0.75 ×` to `1.25 ×` of nominal (i.e. tighter or looser
  by 25% on each side of the structural level).
- Friction: `0.5 ×` to `2.0 ×` baseline.

If the strategy's profit factor drops below 1.0 anywhere in the grid, that's a
red flag for overfit. The robustness criterion is: PF ≥ 1.1 across the full
grid, Sharpe ≥ 0.5 across the full grid.
