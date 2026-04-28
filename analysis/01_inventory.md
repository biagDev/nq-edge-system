# Phase 1 — Source Repo Inventory

**Source:** `https://github.com/biagDev/data-collection`
**Pinned commit:** `92e5f9c29b53f49b400f07aadef6d13a3107dc69` (HEAD at clone, 2026-04-27)
**Local read-only checkout:** `/Users/biag/Claude/_source`

The source repo is a research scratchpad of NQ statistical studies, not a backtest framework. Every
study computes aggregated counts/percentages via Pine Script over TradingView's `CME_MINI:NQ1!`
continuous front-month feed; the **raw OHLCV bars are never persisted**. What ships in `_source` is
a tree of `data/results.json` + `data/*.csv` summary tables and the `pine/*.pine` scripts that
produced them. To backtest anything we have to pull our own NQ bars.

The repo's own `AUDIT.md` is the most important meta-document — it documents bugs found and fixed,
plus residual caveats. Anything below that flags a number as "audited" means the AUDIT.md cleared it.

## Tree (top 3 levels)

```
_source/
├── README.md
├── AUDIT.md
├── analyses/
│   ├── 930-candle-hit-stats/         {pine/, data/{aggregate.csv, by_dow.csv, results.json}, README.md, EASY_READ.md}
│   ├── 945-candle-hit-stats/         (corrected; off-by-one bug fixed pre-audit)
│   ├── 1000-candle-hit-stats/
│   ├── 1015-candle-hit-stats/
│   ├── 1030-candle-hit-stats/
│   ├── 1045-candle-hit-stats/
│   ├── 9am-1h-candle-hit-stats/
│   ├── 6am-4h-candle-hit-stats/
│   ├── 930-followthrough/            {body_split.csv, dayclose_table.csv, excursion_past_high.csv, results.json}
│   ├── extended-stats/
│   │   ├── 01-prior-day-hl-retest/
│   │   ├── 02-time-to-retest/        (v2, audit fix B)
│   │   ├── 03-max-excursion/         (v2, audit fix C)
│   │   ├── 04-conditional-on-color/
│   │   ├── 05-first-touch-direction/
│   │   ├── 06-midpoint-mean-reversion/
│   │   ├── 07-hod-lod-timing/
│   │   ├── 08-range-stats/
│   │   └── 09-volume-profile/
│   ├── daily-patterns-v1/            {gap_fill.csv, streaks.csv, results.json} — ~6,700 daily bars
│   └── daily-patterns-v2/            {combined_streak_quartile.csv, regime_split.csv, results.json}
└── tradingview-mcp/                  vendored MCP bridge — tooling only, no analyses
```

## Catalog

All studies are on `CME_MINI:NQ1!` (NQ continuous front-month). "as_of" dates are 2026-04-25/26.
"232-day series" = the `15m` opening-range studies (TradingView's intraday cap ≈ 11 months).
"223-day series" = same window but tally gated at 15:45 RTH close (audit Issue 2).
Daily series = ~6,700 bars (~27 years, 1999-onwards).

### A. Opening-range 15m candle hit-rate series — RTH

The signature dataset. For each of the first six 15m RTH candles, report the probability that a
later candle's wick "retests" (`>= H` or `<= L`) within 1, 2, or 3 forward bars, split into
`high_only / low_only / both / either / neither`. Ships an aggregate row plus a day-of-week split.

| Study | Path | Subject | Forward windows | n | Headline (either-side, last window) | Audit tier |
|---|---|---|---|---|---|---|
| A1 | `analyses/930-candle-hit-stats` | 9:30-9:45 | by 10:00, by 10:15 | 232 | ~78%/~88% retest | High |
| A2 | `analyses/945-candle-hit-stats` | 9:45-10:00 | by 10:15, 10:30, 10:45 | 232 | ~85% by 10:45 | High (post-fix A) |
| A3 | `analyses/1000-candle-hit-stats` | 10:00-10:15 | by 10:30, 10:45, 11:00 | 232 | 84.91% by 10:30 | High |
| A4 | `analyses/1015-candle-hit-stats` | 10:15-10:30 | by 10:45, 11:00, 11:15 | 232 | 86.21% by 10:45 | High |
| A5 | `analyses/1030-candle-hit-stats` | 10:30-10:45 | by 11:00, 11:15, 11:30 | 232 | 89.22% by 11:00 | High |
| A6 | `analyses/1045-candle-hit-stats` | 10:45-11:00 | by 11:15, 11:30, 11:45 | 232 | 82.76% by 11:15 | High |

### B. Multi-timeframe candle hit-rate

| Study | Path | Subject | Forward | n | Headline | Audit tier |
|---|---|---|---|---|---|---|
| B1 | `analyses/9am-1h-candle-hit-stats` | 9:00-10:00 1h (built from 4×15m) | 10:15 / 10:30 / 10:45 / 11:00 | 232 | 66 / 78 / 88 / **91**% retest | High |
| B2 | `analyses/6am-4h-candle-hit-stats` | 6:00-10:00 4h (built from 16×15m) | 10:30 / 11:00 | 232 | 67 / 81% retest | Medium-high (Issue 1: ±1 DOW swap) |

### C. 9:30 follow-through — does the directional setup actually pay?

| Study | Path | n | Headline | Notes |
|---|---|---|---|---|
| C1 | `analyses/930-followthrough` | 232 (sub-buckets 25-49) | Green 9:30 + high retest → 71.8% green close (n=85). **Wide-body** version: 76.9%. Red+low retest **wide body** = 79.6%. Mean follow-through past the 9:30 high = **1.21× the 9:30 range**, with 17.6% of days extending >2× | The single most strategy-actionable file in the repo. Sub-buckets have ~±10pp CIs |

### D. Extended stats — 9-theme decomposition of the 9:30 candle (and prior-day HL)

| # | Path | Theme | n | Headline | Audit |
|---|---|---|---|---|---|
| D1 | `extended-stats/01-prior-day-hl-retest` | Prior-day RTH H/L retest in next session | 222 | First hour: 77.5% either-side; PDH 47.3% / PDL 28.4% | Med-high |
| D2 | `extended-stats/02-time-to-retest` | Bars-to-retest distribution for 9:30 | 223 | 91.0% within first 15m bar; mean 16.82 min | High (v2 fix) |
| D3 | `extended-stats/03-max-excursion` | Max travel past 9:30 H/L before first retest | 223 | 0-25% of OR bucket: 44.84%; mean excursion 37.5% | High (v2 fix) |
| D4 | `extended-stats/04-conditional-on-color` | 9:30 retest by candle color | 119 grn / 111 red / 2 doji | **Green: 73.95% high-any vs 21.01% low-any (3.5×). Red: mirror.** | High |
| D5 | `extended-stats/05-first-touch-direction` | Which side gets wicked first | 223 | High first 47.98%, low first 46.64%, both same bar 5.38%, never 0% | High |
| D6 | `extended-stats/06-midpoint-mean-reversion` | Touch of (H+L)/2 of 9:30 | 223 | 64.6% by 10:15, 71.3% by 11:00, 78.9% by EOD | Med-high |
| D7 | `extended-stats/07-hod-lod-timing` | Hourly bucket of HOD/LOD | 223 | 9:30-10:00 prints HOD 31.4% / LOD 35.0% | Med-high |
| D8 | `extended-stats/08-range-stats` | OR vs full RTH range | 223 | OR mean 109.35 pts, day mean 309.03 pts (OR ≈ 38.7% of day) | Med-high |
| D9 | `extended-stats/09-volume-profile` | Avg 15m volume per RTH bucket | 232 | 9:30 peak ≈36,924 contracts; ≈3.5× midday trough | High |

### E. Daily patterns — ~6,700-bar (~27y) daily series

| # | Path | n | Headline | Notes |
|---|---|---|---|---|
| E1a | `daily-patterns-v1` stat 1 (streaks) | 1690 / 888 / 488 / 259 / 351 (green); mirror red | After-3-green: 53.7% continue. After-4-green: 59.85%. Bear-streak bounce edge ≈ 56% | Real but small lift over 50% |
| E1b | stat 2 (close quartile follow-through) | 2419 top-Q / 1598 bot-Q | **Top-Q close → 85.6% higher high next day; bot-Q → 82.5% lower low.** P(green next) only 53.8% — extension ≠ direction | Strong range-extension signal |
| E1c | stat 3 (NR7 expansion) | 1044 | **NR7 day → 83.5% next-day expansion, ratio 1.68×.** Slight green bias 55.9% | One of the most usable edges; n large; regime-stable per v2 |
| E1d | stat 4 (gap fill) | 5884 / 176 / 77 / 17 / 17 | <25pt: 95% fill (roll noise inflates this); 25-50pt: 67.6%; 50-100pt: 67.5%; 100-200pt: 47.1% (n=17!); 200+pt: 52.9% (n=17!) | Big-gap buckets are anecdotal; <25pt bucket polluted by roll |
| E1e | stat 5 (range-position 20d) | 1632 top-10% / 517 bot-10% | After top-10% close: 56.3% green; bot-10%: 55.5% green | Slight continuation top, slight bounce bottom |
| E2 | `daily-patterns-v2` combined + regime | as v1, split by 200MA | **200MA is the dominant regime filter.** Above MA: 3+ green continues 57.2%; below: 49.2% (no edge). NR7 + top-Q higher-high = regime-independent | Combined streak+quartile **adds nothing** over streak alone (verdict in file) |

## tradingview-mcp directory

Vendored clone of `tradesdontlie/tradingview-mcp`: an MCP server that drives TradingView Desktop
via remote-debug. Contains `src/` (TS server), `agents/`, `skills/`, `scripts/`, `tests/`. **Tooling
only.** No analyses or data live here. We do not need any of it to backtest — we only need NQ OHLCV
bars and the Pine logic to translate into Python.

## Raw data available for backtesting

**There are no raw OHLCV bars in `_source`.** Every `data/*.csv` is an aggregate (counts, hit
rates, distributions). The atomic data we have:

| File pattern | What it is | Useful for |
|---|---|---|
| `analyses/*/data/aggregate.csv` | One-row aggregate counts/percentages | Verifying our re-implementation matches |
| `analyses/*/data/by_dow.csv` | Per-DOW breakdowns | DOW conditioning sanity checks |
| `analyses/930-followthrough/data/{body_split,dayclose_table,excursion_past_high}.csv` | Strategy-grade tables | The closest thing we have to a "tradeable spec" |
| `analyses/daily-patterns-v*/data/{streaks,gap_fill,combined_streak_quartile,regime_split}.csv` | Daily aggregates | Same |
| `analyses/extended-stats/*/data/*.{csv,json}` | Theme aggregates | Same |
| `analyses/*/pine/*.pine` | Pine reference | **Single source of truth for bar mapping logic** when we re-implement in Python |

**To run any backtest, we need to fetch our own bars.** Required pulls:

- **Daily NQ continuous front-month** — for E1/E2 replication. Public sources: Stooq (free), or
  Norgate / Databento / Polygon (paid). 27y deep is achievable.
- **15m NQ RTH bars** — for the A/B/C/D series. TradingView caps intraday history; vendor pulls
  (Polygon, Databento, Firstrate, IQFeed) reach further. Even 2-3y of clean 15m would multiply the
  source's 232-day sample by ~5×, which materially tightens CIs.

Until we pull data, every claim in the source is **directionally** known but not independently
verified.

## Overlaps / duplications

- A1 (9:30 candle 232 days) and D2/D3/D5/D6/D7/D8 (extended-stats with n=223) measure the **same
  9:30 candle** with different aggregations. Not duplicates but tightly coupled — a Python
  re-implementation should produce them all from one data pass.
- D4 (conditional-on-color) is the *raw input* to C1 (followthrough). C1 is downstream and richer.
- E1 vs E2: V2 reuses V1 stats, splitting them by 200MA regime. Treat E1 as the unconditional
  baseline and E2 as the regime-conditioned version of the same numbers.
- A1 (n=232) vs D2/D3 (n=223): same 9:30 universe, different denominator due to EOD-tally gate.
  AUDIT Issue 2 explains; not a bug.

## Data-quality concerns (compiled from AUDIT.md + my read)

- **Sample size — intraday studies are thin.** n=232 → ±3.9pp CI on aggregates, ±10pp per-DOW. Any
  sub-bucket below n≈100 should be treated as suggestive at best. The C1 wide-body × red-low
  buckets (n=31–49) fall in this zone.
- **Contract-roll noise** (~1.5% of intraday days, more impact on the daily `<25pt gap` bucket).
  Disclosed but not filtered.
- **TradingView feed not cross-validated** against Polygon/Databento. Likely fine for liquid NQ but
  unverified.
- **Pine bugs already caught and fixed:** off-by-one (945), `var` comma decl, denominator-gating
  bugs B/C in extended-stats themes 2 and 3. v2 numbers in repo are corrected.
- **Multiple-comparisons risk.** The repo computes dozens of conditional rates without correction.
  Phase 2 must apply Bonferroni / BH and rank what survives.
- **No look-ahead vulnerability in the *measurements* themselves** (each study only inspects bars
  *after* the subject candle closes), but a backtest will need to ensure the **decision time** is
  the close of the subject candle, not after.
- **Holidays / half-days not filtered** (small effect for 24h instrument).
- **No out-of-sample tracking.** Every number in `_source` is in-sample by construction.

## Cluster-level commentary — what looks promising vs weak

**Strongest:**
- **C1 (9:30 followthrough) + D4 (color)** — this *is* the only setup-grade analysis. Direction
  predicted by 9:30 color, action triggered by which side retests first, magnitude implied by D3
  (max-excursion) and the C1 mean-1.21× extension. The wide-body filter looks meaningful but
  the n is small.
- **B1 (9am 1h candle)** — 91% retest by 11:00 is the cleanest "auction-rotation" signal in the
  repo. Symmetric. Useful as a *fade* leg or a "don't chase past 11:00" rule.
- **E1c (NR7 expansion)** — 83.5% expansion with regime-stability (E2). Large n. Pairs with
  volatility-targeted sizing.
- **E1b (top-Q close → higher-high)** — 85.6% on n=2419 is the highest-confidence signal in the
  whole catalog by sample weight. Note: it predicts *range extension*, not direction.

**Mediocre:**
- E1a streak continuation. Lift is real but only ~3-7pp above coin flip; not enough on its own.
- D6 midpoint mean reversion. 65-79% rates are not impressive vs the unconditional fact that the
  midpoint sits inside most subsequent bars by construction (need a base-rate sanity check in
  Phase 2).
- D7 HOD/LOD timing. Useful as a session-structure prior, not a signal.

**Weak / discard candidates:**
- E1d gap fill big-gap buckets (n=17). Anecdote.
- D8 range stats. Descriptive, not predictive.
- E2 combined streak+quartile. The repo itself flags it as additive ≈ 0.

**Most fragile under Phase 2 rigor:** anything with n<100, the 6am-4h DOW row, all sub-buckets in
C1.

## What we'll copy into `nq-edge-system/data/raw/`

For Phase 2 we only need the *summary tables* the source already produced (so we can compute
Wilson CIs and lift), plus the Pine sources (so we can replicate any number we doubt). We do **not**
copy `tradingview-mcp/` (tooling) or any tree we won't read.

Concretely:

- `analyses/*/data/results.json` (every analysis)
- `analyses/*/data/*.csv` (every analysis)
- `analyses/*/pine/*.pine` (every analysis)
- `AUDIT.md` (verbatim, as `data/raw/SOURCE_AUDIT.md`)

A `PROVENANCE.md` will record source path, source SHA `92e5f9c`, and what each file represents.

## Items deferred to later phases

- Independent re-fetch of NQ daily + 15m bars (Phase 6 prerequisite).
- Wilson CIs, lift calc, BH correction for every reported rate (Phase 2).
- Mapping of survivors to ideologies / framework-fit (Phase 3-4).
- Strategy spec (Phase 5).
