# 03 — Research Synthesis: Frameworks for Converting Edges into a Robust Day-Trading System

**Date:** 2026-04-27
**Status:** Phase 3 (research only). No changes to strategy spec, ranking, or backtest.
**Inputs:** Phase 2 shortlist of 8 BH-significant NQ edges (D4, B1, E1b, E1c, D1, D2, E1d, C1).
**Output:** Per-topic synthesis (cites reference notes in `/references/`) + verdict table + skeptical appendix.

---

## Executive summary

The professional literature converges on a clear hierarchy: **statistical edges (the inputs we already have) → R-multiple bookkeeping → multi-signal stacking with low correlation → vol-targeted fractional-Kelly sizing → strict purged-CV / Deflated-Sharpe validation.** Auction Market Theory and Mark Fisher's ACD provide the most directly applicable conceptual scaffolding for our shortlist (retest-of-extreme, opening-range-as-reference). Crabel's NR7 work is the strongest match for E1c. Order flow, ICT/SMC, and Al Brooks are best treated as *execution refinements*, not signal sources — and ICT in particular should be cherry-picked at most for its liquidity-sweep concept (which is just classical breakout-failure under new branding). The single highest-leverage piece of professional methodology we can adopt is López de Prado's purged k-fold CV plus the Deflated Sharpe Ratio: with 14 studies tested and 10 BH-survivors, our exposure to selection-bias-inflated Sharpe is non-trivial and *must* be quantified before live deployment.

---

## A. Auction Market Theory / Market Profile

**What it is** (see `references/A_auction_market_theory.md`). Steidlmayer/Dalton framework: market = continuous two-way auction. Day taxonomy (Initial Balance, Value Area, POC; rotational vs trending day types). On the ~70-80% of days that are rotational, the IB extremes act as magnets/retest targets — exactly the mechanism behind B1, D1, D2.

**Pairs with:** B1 (9-10am candle retest 90.5% by 11:00), D1 (prior H/L retest 77.5%), D2 (9:30 candle retest 91% within first 15m). The framework supplies the *causal story* for why these edges exist, plus the day-type taxonomy for when they fail.

**Failure modes:** On trend days (~10-15%), IB extremes break and don't retest. Without a regime filter, retest edges drag in those days as systematic losers. *Action:* couple every retest edge with a trend-day suppressor (see topic O).

## B. Opening Range theory (Crabel, Fisher, Raschke)

**What it is** (see `references/B_opening_range.md`). The OR — typically 9:30-9:45 or 9:30-10:30 — is the most-studied intraday reference. NQ-specific quantified data (TradingStats, 6,142 days): single-break IB held ~82%; double-break rate at 30m ORB only 39.4%; 67% continuation given break. Naive ORB has decayed; *conditional* ORB (with NR7 context, or A-vs-C confirmation) still works.

**Pairs with:** D4 (9:30 color predicts retested side), C1 (9:30 wide-body followthrough), B1 directly. E1c works specifically as NR7 → next-day ORB.

**Failure modes:** Treating wick-touch breakouts as signals. Modern statistics (TradingStats, NinjaTrader) show wick breakouts are ~random; **close-beyond + retest-and-hold** is the empirically supported variant.

## C. Mark Fisher's ACD method

**What it is** (see `references/C_acd_method.md`). OR + A/C breakout/failure points + Pivot Range bias filter. The A-vs-C distinction is the conceptual ancestor of the modern "double-break filter" and ICT's "sweep then reclaim."

**Pairs with:** D4 most directly — D4's mechanism (open-color predicts retest side) is the "C-on-the-other-side" pattern in ACD vocabulary. Also B1, since A/C levels formalize "extension followed by retest."

**Failure modes:** Fisher's published A/C offsets are calibrated to early-2000s vol; need re-tuning for NQ post-2018. Fisher himself (per Elite Trader threads) said the levels alone don't make traders profitable — execution skill matters.

## D. NR7 / range contraction → expansion (Crabel)

**What it is** (see `references/D_nr7_range_contraction.md`). Today's range narrowest of last 7 → next-day expanded range at significantly above-baseline rates. Most-replicated intraday pattern in the literature. NR7-Inside-Day ("double compression") is the strongest variant.

**Pairs with:** E1c **directly and uniquely**. Our 83.5% next-day expansion stat is consistent with Crabel's tables.

**Failure modes:** **Predicts expansion, not direction.** E1c needs a directional layer (gap direction, ORB on the NR7+1 day, or the prior-day-close-position bias from E1b).

## E. Order flow / footprint / delta / absorption

**What it is** (see `references/E_order_flow.md`). Bar-internal microstructure: aggressor delta, cumulative delta, bid/ask absorption, footprint imbalances. Real academic foundations exist (OFI in Cont/Kukanov/Stoikov 2014, VPIN in Easley/de Prado 2011) but operate at ms-to-second horizons that retail can't capture.

**Pairs with:** Optional execution refinement on any retest entry (D1/D2/B1). E.g., absorption at the prior-day-high during a D1 retest is a reasonable confirmation; CVD-divergence is a reasonable invalidation.

**Failure modes:** Treating footprint patterns as signals. Most retail orderflow content has no published statistical validation. **Do not make order-flow a precondition for any shortlist edge.**

## F. ICT / Smart Money Concepts — critical evaluation

**What it is** (see `references/F_ict_smc.md`). Huddleston's repackaging of supply/demand (Order Block), breakaway gap (FVG), stop-hunt (Liquidity Sweep), upper/lower-half-of-range (Premium/Discount). Underlying phenomena are real; the ICT-specific framing adds unfalsifiable narrative on top. Huddleston blew his 2024 Robbins Cup account live — material counter-evidence.

**Pairs with:** Maybe — *narrowly* — extract the liquidity-sweep concept and apply it to D1/D2 (sweep of prior H/L then reverse). This is just classical breakout-failure with better branding. Skip OBs, FVGs, kill zones, Power-of-Three.

**Failure modes:** Adopting ICT wholesale imports unfalsifiable narratives that immunize the strategy from honest evaluation. **Reject the ICT framework; cherry-pick at most the sweep-and-reclaim pattern.**

## G. Al Brooks price action

**What it is** (see `references/G_al_brooks.md`). Most exhaustive published taxonomy of bar-by-bar action: signal bars, MM bars, two-legged pullbacks (M2B/M2S), failed breakouts. Brooks himself reports realistic 40-60% win rates on his core setups — unusually honest for the price-action industry.

**Pairs with:** **Entry-trigger refinement** on every shortlisted edge. E.g., for D1/D2 retest, require the retest bar to be a strong-close reversal signal bar; for B1, require an ii or M2B before re-entry to retest level.

**Failure modes:** Brooks' vocabulary describes structure, doesn't manufacture edge. Insisting on two-legged pullbacks systematically misses single-leg pullbacks in the strongest trends — Brooks acknowledges this trade-off.

## H. AQR-style multi-signal stacking

**What it is** (see `references/H_aqr_signal_stacking.md`). Combining N weakly-correlated signals scales Sharpe with √N. AQR's *Value and Momentum Everywhere* (2013): two signals with mildly negative correlation roughly double Sharpe.

**Pairs with:** **The portfolio-level architecture for the entire shortlist.** Our 8 edges have heterogeneous conditioning (open color, gap, NR, prior range) so we can reasonably expect low pairwise correlation among the signal-conditional return streams.

**Failure modes:** Naïve summation overweights edges that fire on overlapping windows (most of ours fire in the open + first hour). Must measure conditional-on-fire correlation, not unconditional. Combine via inverse-vol or equal-risk-contribution; cap aggregate concurrent risk.

## I. Renaissance / Two Sigma / D.E. Shaw — "many small edges"

**What it is** (see `references/I_renaissance_two_sigma_des.md`). Mercer's "50.75% but 100% right 50.75% of the time" quote is the philosophy: tiny per-trade edge × enormous N × strict cost control × ruthless validation = Medallion. Simons' lectures: patterns exist but are close-to-random; extraction requires industrialized research.

**Pairs with:** Philosophical posture, not method. Implication for us: our 70-90% conditional hit rates are *suspiciously high* by Renaissance standards, which means either (a) we're benefiting from a small-scale arena Renaissance can't trade, (b) our R:R is unfavorable enough to neutralize the apparent advantage, or (c) we have selection / look-ahead bias somewhere. Almost certainly some mix of (b) and (c).

**Failure modes:** Believing that any single edge is "the edge." Combine, validate, never bet the farm.

## J. CTA / managed-futures intraday models

**What it is** (see `references/J_cta_managed_futures.md`). Public CTA literature is overwhelmingly long-horizon trend-following (20d-500d, AQR Trends Everywhere 2024). Intraday CTA models exist at large shops but are not disclosed. Recent academic work (arXiv 2507.15876) shows short-horizon (20d) trend modestly improves CTA Sharpe at higher turnover cost.

**Pairs with:** **Daily trend filter as a regime gate**, not as a signal. On trend days, retest edges (D1, D2, B1) decay; extension edges (E1b, E1c, E1d) work. A simple sign-of-20d-return or close-vs-50d-SMA gate is sufficient.

**Failure modes:** Treating CTA-style trend signals as intraday entry signals — they're calibrated to weeks/months and don't time intraday entries.

## K. Walk-forward, purged k-fold, Deflated Sharpe (López de Prado)

**What it is** (see `references/K_validation_dsr.md`). AFML Ch. 7 (Purged K-Fold CV with embargo) and Ch. 12 (Combinatorial Purged CV); Bailey & López de Prado 2014 (Deflated Sharpe). Standard k-fold leaks via overlapping labels; CPCV resolves it. DSR corrects observed Sharpe for selection bias under multiple testing (False Strategy Theorem).

**Pairs with:** **Mandatory adoption** before live deployment. With 14 studies tested and 10 BH-survivors, our multiple-testing exposure is real. BH controls FDR but not Sharpe magnitude inflation.

**Failure modes:** Skipping this step is the single most common failure mode in retail/prop systematic trading — it's why backtest Sharpe ≠ live Sharpe.

## L. Position sizing — Kelly, fractional Kelly, vol targeting

**What it is** (see `references/L_position_sizing.md`). Full Kelly is mathematically optimal but practically catastrophic for fat-tailed assets. Half-Kelly captures ~75% of growth at ~50% vol (MacLean/Ziemba/Blazenko 1992); professionals run 10-25% of Kelly. Vol targeting (Harvey et al. 2018) consistently improves Sharpe by 0.08-0.10 on risk assets.

**Pairs with:** Sizing layer for the entire stack. Recommended: fractional-fixed-R per edge, vol-target at the equity-curve level, hard cap on aggregate concurrent risk (~2-3%).

**Failure modes:** Full Kelly under estimated parameters can produce negative growth. "Kelly will make you rich" content ignores tail risk.

## M. Van Tharp R-multiples / expectancy

**What it is** (see `references/M_van_tharp_r_multiples.md`). Standardized bookkeeping: Setup → Trigger → Entry → Stop → Target → Sizing. Every trade reported as multiple of R. Expectancy = mean R-multiple. SQN = Sharpe-analog at trade level.

**Pairs with:** **The canonical strategy-spec format for Phase 4.** Every shortlisted edge gets converted into this skeleton.

**Failure modes:** Tharp's psychology/personality-typing material is weaker than his bookkeeping. Adopt the bookkeeping; ignore the personality marketing.

## N. Trade management — scaling, breakeven, partials

**What it is** (see `references/N_trade_management.md`). Empirical literature is much thinner than retail culture suggests. Stops are roughly neutral on expectancy for index futures (helpful for risk control, not edge). Move-to-breakeven typically *reduces* expectancy. Partial profits at fixed R are approximately neutral on symmetric systems and *negative* on positive-skew systems (steal from the right tail).

**Pairs with:** Default for our system: single hard stop, single structural target, no scaling, no breakeven moves.

**Failure modes:** Importing retail trade-management folklore (always partials at 1R, always BE at 1R) without measuring its EV impact. Most of these rules are behavioral crutches with negative or neutral expectancy.

## O. Session structure for index futures

**What it is** (see `references/O_session_structure.md`). Dalton's six day types: ~70-80% rotational (where retest edges live), ~10-15% trend (where retest edges fail and extension edges win). IB-extension-magnitude predicts trend-day probability.

**Pairs with:** **Trend-day classifier as first-class regime gate.** Inputs: IB extension magnitude by 11:00, gap, prior-day type. Output: trend probability used to mute retest edges and boost extension edges.

**Failure modes:** Day-type frequencies are ballparks; verify on our specific 2014-2026 NQ window. Avoid deterministic "today is X day type" claims.

---

## Verdict table — best fit per shortlist edge

| Edge | Mechanism family | Primary framework fit | Secondary frameworks | Validation/sizing layer |
|---|---|---|---|---|
| **D4** — 9:30 color predicts retest side | Open + retest | **Mark Fisher ACD (C)** — A-then-C pattern | Auction Market Theory (A), Brooks signal-bar trigger (G) | DSR + purged-CV (K), fractional Kelly (L) |
| **B1** — 9-10am candle retests by 11:00 | IB retest | **Auction Market Theory (A)** — IB retest on rotational days | Mark Fisher ACD pivot range (C), trend-day gate (J/O) | DSR (K), fractional Kelly (L) |
| **E1b** — top-quartile close → next-day higher high | Extension / momentum | **CTA short-horizon trend (J)** — close-vs-prior-range bias | AQR multi-signal stacking (H) | DSR (K), vol-targeted sizing (L) |
| **E1c** — NR7 → next-day expansion | Vol contraction → expansion | **Crabel NR7 (D)** — direct match | OR breakout next day (B), Brooks signal bar (G) | DSR (K), fractional Kelly (L) |
| **D1** — prior H/L retest in next session H1 | Auction retest | **Auction Market Theory (A)** | ICT *liquidity sweep* (narrow extract from F), Brooks reversal signal bar (G) | Trend-day gate (J/O), DSR (K) |
| **D2** — 9:30 candle retested in H1 | Open retest | **Auction Market Theory (A)** + ACD (C) | Brooks two-legged pullback if retest is structured (G) | DSR (K), fractional Kelly (L) |
| **E1d** — 25-50pt gap fills same day | Gap reversion | **Auction Market Theory (A)** — open-outside-VA mean-reversion | Trend-day gate (J/O) — suppress on trend-day setups | DSR (K), fractional Kelly (L) |
| **C1** — 9:30 followthrough wide body | Open + extension | **ACD (C)** — A signal | Crabel ORB (B), CTA daily trend (J) | More data first; DSR especially important given small n |
| **All combined** | Portfolio | **AQR multi-signal stacking (H)** — equal-risk-contrib | Renaissance philosophy (I) — many small edges | Vol targeting (L), Tharp R-bookkeeping (M), Purged-CV + DSR (K) |

**Cross-cutting layers (apply to every edge):**
- **Spec format:** Tharp Setup→Trigger→Entry→Stop→Target→Sizing (M).
- **Trade management default:** single hard stop, single structural target, no scaling, no breakeven moves (N).
- **Regime gate:** trend-day classifier from IB extension + daily-trend sign (J + O).
- **Validation:** purged k-fold or CPCV + DSR before any live deployment (K).
- **Sizing:** fractional Kelly inside vol-target envelope, ~2% aggregate concurrent risk cap (L).

---

## Appendix — Marketing red flags encountered

Things popular in the retail / prop-firm trading content but **evidence-thin or actively misleading**, encountered in this research:

1. **ICT "kill zones," Power-of-Three, OBs and FVGs as deterministic signals.** Underlying phenomena (stop-hunts, breakaway gaps, supply/demand) are real and predate ICT. The ICT-specific framing adds unfalsifiable narrative; Huddleston's own live-trading record (2016 $10k→$1M challenge, 2024 Robbins Cup) is materially negative.
2. **"5-min ORB will make you rich."** Modern NQ-specific data (TradingStats 6,142 days) shows raw wick-touch ORB is ~random. Conditional ORB (with NR-day or close-confirmation) still works.
3. **"Always take partials at 1R / always move stop to BE at 1R."** Empirically these rules either reduce expectancy (move-to-BE) or steal from the right tail (partials on positive-skew systems). They're behavioral crutches, not edge.
4. **Full Kelly position sizing.** Mathematically optimal under known μ, σ², Gaussian; practically catastrophic on real, fat-tailed, parameter-uncertain markets. Anyone selling full Kelly is ignoring tail risk.
5. **"Read the tape and beat the algos."** Retail orderflow vendors. You cannot out-tape institutional algos at retail latency. Order flow is legitimate as *contextual confirmation*, not as a signal source.
6. **"Renaissance secret algorithm revealed."** The actual algorithms are not public. The *philosophy* (many small edges, ruthless validation) is — and that's what's transferable.
7. **Backtest Sharpe with naive train/test splits and no DSR.** Almost universal in retail content. With multiple testing of 10+ candidate edges, observed best-of-N Sharpe is materially inflated. **This is the single most pervasive failure mode.**
8. **"NR7 has 90% win rate."** NR7 predicts *range expansion*, not *direction*. Cherry-picked direction stats are misleading.
9. **Van Tharp's personality-typing courses.** The R-multiple bookkeeping is excellent. The "trader personality" material is weak.
10. **Paid ACD / Market Profile indicator packages.** The math is in the original books (Fisher 2002, Dalton 2013). Indicator packages are reskins.

---

## Topics where evidence was thin enough to flag

- **(E) Retail-specific footprint patterns** — we found no peer-reviewed support for the specific footprint pattern recipes sold by orderflow vendors. The academic order-flow literature (OFI, VPIN) is real but operates at ms-to-second horizons we can't trade. **Recommendation: skip retail orderflow vocabulary; consider a single CVD-sign confirmation gate as an A/B variant only.**
- **(F) ICT-specific concepts (OBs, FVGs, kill zones, P3)** — empirical support is limited to a handful of un-replicated preprints; the framework's main proponent has a documented record of public trading failures. **Recommendation: skip; possibly extract liquidity-sweep concept (which is just classical breakout-failure).**
- **(J) Public intraday CTA models** — the literature is overwhelmingly long-horizon. Specific intraday CTA techniques are not disclosed. **Recommendation: use only the daily-trend regime gate; do not attempt to replicate intraday CTA signal generation.**
- **(N) Empirical trade-management studies** — surprisingly few rigorous studies exist. The honest answer is "default to simple: hard stop, structural target, no overlays" until/unless we measure each overlay's EV in our own backtest. **Recommendation: simple defaults; treat overlays as A/B test candidates not built-in features.**

---

## Phase 4 implementation directives (carried forward, no spec changes)

1. Convert each shortlist edge to Tharp Setup-Trigger-Entry-Stop-Target-Sizing format (M).
2. Build trend-day classifier (J + O) as a regime gate, applied to retest edges.
3. Add purged k-fold or CPCV validation harness (K).
4. Compute Deflated Sharpe Ratio for combined system (K).
5. Estimate conditional-on-fire correlation matrix across edges; combine via equal-risk-contribution (H).
6. Implement fractional Kelly + vol-target sizing with 2% aggregate concurrent risk cap (L).
7. Default trade-management: single hard stop, single structural target, no overlays (N).
