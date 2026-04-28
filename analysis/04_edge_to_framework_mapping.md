# Phase 4 — Edge → Framework Mapping

For each Phase-2 shortlist edge, this file specifies (a) which Phase-3 framework
provides the causal story and trading vocabulary, (b) the precise trigger that
converts the statistical tendency into an executable signal, (c) what
invalidates the setup, (d) a natural target implied by the data, and (e) how
the edge could combine with others into a stack with lower correlation than
any single signal.

This is **not yet** a strategy spec — it's the bridge between "the data says
this happens 80% of the time" and "here is exactly when I click buy." The
strategy spec (Phase 5) picks 1–3 of these and freezes them into code.

## Selection lens

We exclude:

- **C1 directional setups** — n=85 / 80 base bucket, sub-buckets 31–49. Wide
  CIs. The repo itself notes wide-body green narrowly fails BH at q=0.10 once
  multiple-testing is applied. Carry forward as *future research*, not Phase-5
  candidate.
- **E1d large-gap fills (50–100pt)** — n=77, smaller. Useful as a regime modifier
  not a primary edge.

We carry forward, in priority order:

1. **E1c** NR7 → next-day expansion (n=1044, regime-stable, lift +33.5pp)
2. **E1b** top-Q close → higher high (n=2419, regime-stable, lift +35.6pp)
3. **D4** 9:30 color → retest side (n≈115/color, lift +50pp)
4. **B1** 9-10am 1h candle either-side retest (n=232, 90.5%)
5. **D1** prior-day H/L retest in first hour (n=222, 77.5%)
6. **D2** 9:30 retest within first 15m bar (n=223, 91%)
7. **E1d** medium gap (25-50pt) fills (n=176, 67.6%) — regime modifier

Plus the cross-cutting **200MA regime filter** from E2.

---

## E1c — NR7 → next-day range expansion

**Framework fit (primary):** Crabel "Day Trading with Short Term Price Patterns",
Chapter on NR7 / volatility contraction. Direct match. The setup name is
literally Crabel's term.

**Mechanism:** Range contracts → coiled-spring effect → next-day expansion
~84%. Crabel pairs this with an ORB trigger on the expansion day. Predicts
*magnitude*, not *direction*.

**Trigger (executable signal):**
- *Setup* fires on the close of an NR7 day: today's range == min(last 7 daily ranges).
- *Trigger* fires on the next session: NQ takes out either the prior day's H or L
  (we use this as a directional read rather than guessing).
- *Optional confirmation:* the breakout side aligns with the daily 200MA-regime
  bias from E2 (above MA → favor longs).

**Entry:** stop-buy 1 tick above prior-day H, or stop-sell 1 tick below prior-day L.
First trigger wins; no second entry if first stops out.

**Invalidation (stop):** opposite side of the *NR7 day's* H/L (i.e. stop at
the NR7 low for a long, NR7 high for a short). This is structural, not arbitrary.
Risk per trade ≈ NR7 range ≈ today's range × 1 (by definition the smallest of
last 7).

**Target:** 1.68× NR7 range (the *empirical* mean expansion ratio from
`daily-patterns-v1`). Final-bar exit if not hit.

**Why this works:** Volatility clusters — empirical fact (Engle 1982, GARCH lit).
NR7 is a clean low-vol regime classifier. Expansion is regime-mean-reversion.

**How it combines:** Daily timeframe → near-zero correlation with intraday
retest edges (D1/D2/D4/B1). Can be stacked simultaneously without exposure
overlap.

---

## E1b — Top-Q close → next-day higher high

**Framework fit (primary):** AQR-style time-series momentum, but applied at
1-day lookback. Source's largest-n signal (n=2419, 85.6%). Predicts *extension*
(higher high), not *direction* (close green).

**Mechanism:** Strong close near the top of the day's range = persistent buying
imbalance — one form of short-horizon momentum. The "predicts higher high but
not green close" finding is consistent with Asness/Moskowitz: momentum is a
dispersion / continuation signal, not a sign of P&L.

**Trigger:**
- *Setup* fires at today's close if today's close ≥ today's high − 0.25 × range
  (top-quartile of today's range).
- *Trigger* fires next session: the previous day's high gets traded.

**Entry:** stop-buy 1 tick above prior-day H *only if* triggered before 12:00 ET
(structural — most HOD's are set 9:30-11:00 per D7).

**Invalidation:** prior-day H minus 0.5 × prior-day range (a 50% retracement of
prior day) — structural rather than monetary.

**Target:** prior-day H + 0.5 × prior-day range, or session close, whichever first.
The stat is "higher high happens" so we collect 0.5 R worth of "higher" before
the day mean-reverts.

**Why this works:** Same coiled-spring reasoning as NR7 but in *direction* form.
Asness "Value & Momentum Everywhere" gives the broad theoretical justification.

**Combines with:** Pairs naturally with **NR7 + above-200MA** as a "directionally
preferred breakout" setup. When NR7 + top-Q close + above MA all align (rare),
the stacked signal has the highest support of any combination.

**Caveat:** the bare top-Q signal does not predict direction (53.8% green). The
85.6% number applies to *extension* (higher high). The trigger above
operationalizes extension, not direction.

---

## D4 — 9:30 color predicts retest side

**Framework fit (primary):** Mark Fisher ACD method. The 9:30 candle = the OR.
"Color = direction of the day's first push". The 73.95% high-retest after green
9:30 *is exactly* an "A-up failure → C-down" pattern in ACD vocabulary.

**Mechanism:** First push sets the direction; the *opposite* extreme of the
opening candle becomes the magnet on rotational days (Auction Market Theory).
Color encodes which side was extended last → which side has remaining liquidity
to attract price.

**Trigger:**
- *Setup* fires at the close of the 9:30-9:45 candle: classify color (green/red),
  body size (wide ≥ 50% of range, narrow < 50%).
- *Side selected:* on green 9:30 we are "looking for high to be retested" =
  long bias. On red 9:30 we are looking for low retest = short bias.

But D4 says **the high is the side that gets retested**, not "price ends green
because high gets retested." Pure D4 alone is not directional. C1 layered on
top makes it directional but with smaller n.

**Phase-5 decision:** Treat D4 as a **filter / structural prior**, not a primary
entry trigger. D4 selects the *expected retest side*; D1/B1 supply the
executable retest setup; D7/E2 supply the regime filter; C1 supplies the optional
followthrough overlay.

**Combines with:** D4 is a building block for D1/B1/D2 (it tells those edges
which side to favor). It is the ACD-style "directional read" layer of the stack.

---

## B1 — 9-10am 1h candle either-side retest by 11:00

**Framework fit (primary):** Auction Market Theory — "Initial Balance retest
on rotational days." Direct match. Steidlmayer/Dalton's IB rotation is exactly
this measurement at 1h granularity.

**Mechanism:** ~70-80% of NQ days are rotational. On rotational days the IB
extremes act as magnets. 90.5% retest by 11:00 implies *both* sides get touched
on most days (since 5.4% are "both same bar"). The edge isn't "which side";
it's "any side gets revisited" → fade-the-extension trade.

**Trigger:**
- *Setup* fires at 10:00 ET: 9-10am candle is closed; H1 and L1 are known.
- Wait for price to extend beyond H1 or L1 *after* 10:00.
- *Trigger:* on extension above H1, look to short back through H1 (and mirror
  for L1).

**Entry:** limit sell at H1 (or limit buy at L1) on the first touch after extension.
Or stop-sell 1 tick below H1 after a failed re-test from above.

**Invalidation:** 0.5 × (H1 − L1) above H1 (mirror for L1). Structural — half
the IB above extension. If price holds that level, we're on a trend day and the
retest fails.

**Target:** opposite extreme of the 1h candle (L1 from a short above H1).
Empirically expected to be hit by 11:00 — exit at 11:30 if not reached.

**Why this works:** Auction theory. "Outside extensions seek opposite extreme"
on rotational days; the 91% rate quantifies it.

**Failure modes:** Trend days. **Critical:** B1 must be gated by the trend-day
classifier (Phase 3 topic O) or it will systematically lose on the ~10-15% of
days when extensions don't return.

**Combines with:** D4 selects which extension is *expected* to extend further
(green 9:30 → high more likely to be retested = lower-quality short of H1).
Use D4 to size up the L1 long (concordant) and size down the H1 short (against).

---

## D1 — Prior-day H/L retested in first hour

**Framework fit (primary):** Auction Market Theory — value-area / prior-session
balance. Same family as B1. Different timeframe reference (yesterday's RTH H/L
vs today's 1h IB).

**Mechanism:** Yesterday's auction H/L = remembered liquidity. 77.5% touch rate
in the first hour means at least one side gets revisited on most days.

**Trigger / entry / stop / target:** structurally identical to B1 with substituted
levels (PDH/PDL instead of 1H1/L1).

**Combines with:** Stacks with B1 on overlap — when 1H extension breaks PDH,
that is a *higher-conviction* short-extension trade (two reference levels
breached). When PDH ≈ B1 H1 ≈ overnight high, sizing should reflect the
correlation (use min, not sum, of edge weights — see signal stacking note below).

---

## D2 — 9:30 retest within first 15m bar

**Framework fit (primary):** Auction Market Theory + ACD. 91% retest within
first bar means on most days, an immediate ACD "A-failure" or open-rotation
happens.

**Tradeability:** Useful as a **timing modifier**, not a standalone edge. 91%
within 15m means if no retest by 10:00, we are in a *trend / momentum day* — a
trend-day classifier flag.

**Combines with:** Lights up the "no-retest = trend day" signal that disables
B1 / D1 / D4 retest-fade trades for the rest of the session.

**Spec role:** trend-day classifier input. Not its own entry.

---

## E1d — Medium gap (25-50pt) fills same day

**Framework fit:** Auction Market Theory — gap = price opens outside prior
value area; 67.6% same-day fill = mean-reversion to value. Robust above/below
200MA per E2.

**Trigger:**
- *Setup* fires at 9:30 open: prior_close = yesterday's RTH close;
  gap = today's open − prior_close. If 25 ≤ |gap| ≤ 50, setup is live.
- *Trigger:* enter on first 15m bar that does not extend beyond opening 5m H/L
  in the gap-direction (i.e. gap-up + first 15m doesn't break above the open
  range high → fade the gap).

**Entry:** market on confirmation, or limit at midpoint of the 9:30 candle.

**Invalidation (stop):** 25% beyond the gap extreme (open + 0.25 × gap-size for
gap-up). Structural.

**Target:** prior_close. Time-stop at 13:00 ET (most fills happen earlier per
D7 timing).

**Caveats:** 67.6% is the lowest hit rate in our shortlist. After-cost expectancy
needs the avg-fill-distance vs avg-loss-distance, which is not in the source.
Treat as a **secondary/optional strategy** until backtest confirms expectancy.

**Combines with:** When gap-fill setup fires *and* day is rotational (D2 retest
confirmed by 10:00), fill probability should rise. When gap-fill setup fires
on a no-retest day (trend-day flag), suppress.

---

## Cross-cutting layer: 200MA regime filter (from E2)

**Framework fit:** CTA / managed-futures regime gate (Phase 3 J/O).

**Spec role:** Above 200MA → bullish regime, sizes up long-bias setups, sizes
down short-bias setups (and vice versa). E2 confirmed:

- Streak/range-position drift signals — only work above MA.
- NR7 expansion / top-Q higher-high — robust both regimes (no filter needed).
- Bear-streak bounce — works both regimes (no filter needed).

For our shortlist: applies as a *direction modifier* to E1b and to D4's
followthrough version (C1 family). Doesn't apply to symmetric retest edges
(B1 / D1 are direction-agnostic).

---

## Cross-cutting layer: Trend-day classifier

**Framework fit:** Dalton six-day-types (Phase 3 O), AMT.

**Spec role:** Disable retest edges (B1, D1, E1d) on suspected trend days.

**Inputs (computable in real time):**

1. **D2 status by 10:00.** If 9:30 candle has *not* been retested by 10:00, +1
   trend-flag.
2. **IB extension by 11:00.** If price > IB-high + 0.5 × IB-range or < IB-low −
   0.5 × IB-range, +1 trend-flag.
3. **Daily 200MA gap.** If today's open is > 0.5σ from 200MA in the trend
   direction, +1 trend-flag.

Simple sum. ≥2 flags → "likely trend day" → suppress fade trades for the
remainder of the session, allow only the prevailing-direction extension trade
(E1b style).

**This classifier is *not* in the source data.** It is a Phase-3-derived overlay
that we'll have to validate ourselves in Phase 6.

---

## Stacking model (how the edges combine)

We have three families of edges with low expected pairwise correlation:

1. **Daily timeframe** — E1c (NR7 expansion), E1b (top-Q higher-high). Decisions
   made at daily close, executed next session.
2. **Open-driven** — D4-modulated B1, D1, D2 retest fades. Decisions made
   9:45-10:30 ET.
3. **Gap-driven** — E1d gap fill. Decision made at 9:30 ET.

Within a session, multiple edges can fire concurrently. Sizing rule (Phase 5):

- Each edge has a fixed risk allocation of **0.5% of equity** per trade
  (fractional-Kelly-implied).
- **Aggregate session risk cap = 1.5%** (sum of concurrent at-risk).
- When two edges target the *same direction in the same level cluster* (e.g.
  PDH and 1H-high at the same price), use the *higher-conviction* edge only
  rather than double-sizing (this is the AQR equal-risk-contribution trick: don't
  let correlated signals masquerade as independent).
- When two edges target *opposite* directions in the same window (e.g. E1b
  long-bias breakout vs B1 short-bias H1 fade), the older signal (E1b's
  next-session breakout, set yesterday) takes precedence; the newer signal is
  suppressed for the day.

---

## Validation overlay (carries into Phase 6)

Per Phase-3 K (López de Prado):

- **Purged k-fold** with embargo on the daily timeframe (E1c, E1b) since features
  span multi-day windows.
- **Walk-forward** on the intraday edges (B1, D1, D4) since the source's 232-day
  sample is too thin for k-fold; use rolling 6-month train / 1-month test.
- **Deflated Sharpe Ratio** computed on the final stacked equity curve, with
  N_trials = 17 (the count of edges in our Phase-2 ranking).
- **Sensitivity:** vary stop and target by ±25% per Phase-6 spec.

---

## Carry into Phase 5

Primary strategy candidates (in order of priority — Phase 5 will pick):

1. **E1c NR7 expansion ORB** — daily setup, most direct framework match,
   regime-stable, large n.
2. **B1 + D4 stacked** — IB-retest fade, gated by D4 directional read and the
   trend-day classifier. Most directly profitable on rotational NQ days.
3. **E1b top-Q higher-high** — daily extension, large n, complements (1).

The Phase-5 spec will pick **(1)** as the primary (it has the best framework fit,
largest regime-stable n, and is the simplest to backtest first), and **(2)** as
the optional secondary if available data allows. **(3)** will appear as a
"future addition" with spec but not initial code.
