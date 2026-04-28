# Phase 6 — Backtest Results

**Data:** NQ=F daily bars from Yahoo Finance, 2005-01-03 → 2026-04-24 (5369 bars).

**Strategies:** NR7 Expansion Breakout (primary) + Top-Q Extension Breakout (secondary), stacked per `analysis/05_strategy_spec.md`.

**Friction baseline:** $4 RT commission + 1 tick slippage per side on full NQ ($20/pt). Sensitivity sweep stresses friction up to 2× baseline.

**Sizing:** 0.5% risk per trade, 15% annual vol target overlay, $100k starting equity.

**No look-ahead:** every signal is computed from end-of-day-`t` data only and executed on day `t+1`. Daily-bar fill ambiguity (both stop and target inside the next bar) is resolved conservatively as **stop-out**.

## 1. Headline (full sample)

- n=1299, win-rate=42.65%, expectancy=-0.176R, PF=0.577, CAGR=-8.18%, Sharpe=-1.767, MaxDD=-84.34%, MAR=0.097
- Total P&L (full sample): **$-83,735** on $100k start.
- Longest losing streak: **11** trades.

## 2. In-sample / Out-of-sample (chronological 70/30)

| | n | win-rate | exp R | PF | CAGR | Sharpe | MaxDD | MAR |
|---|---|---|---|---|---|---|---|---|
| **In-sample** | 1292 | 42.49% | -0.180 | 0.574 | -11.71% | -2.174 | -84.31% | 0.139 |
| **Out-of-sample** | 502 | 40.44% | -0.178 | 0.623 | -10.20% | -1.854 | -51.96% | 0.196 |

IS→OOS expectancy drift: **-0.002R**. Negative = OOS held up (better than IS); positive = OOS degraded.

## 3. Per-strategy decomposition

| | n | win-rate | exp R | PF | CAGR | Sharpe |
|---|---|---|---|---|---|---|
| **NR7 only (1.68× target)** | 608 | 48.19% | +0.008 | 0.956 | -0.32% | -0.082 |
| **NR7 only — diagnostic, no target, exit at close** | 614 | 48.37% | +0.017 | 0.986 | -0.11% | -0.013 |
| **TOPQ only** | 1035 | 39.71% | -0.262 | 0.464 | -9.52% | -2.304 |
| **Combined (spec'd)** | 1299 | 42.65% | -0.176 | 0.577 | -8.18% | -1.767 |

## 4. Walk-forward (annual)

| year | n | win-rate | exp R | PF | year P&L ($) | MaxDD |
|---|---|---|---|---|---|---|
| 2009 | 90 | 47.78% | -0.097 | 0.72 | -7,689 | -10.17% |
| 2010 | 83 | 44.58% | -0.151 | 0.612 | -10,306 | -11.31% |
| 2011 | 122 | 47.54% | -0.088 | 0.759 | -9,143 | -9.57% |
| 2012 | 118 | 40.68% | -0.238 | 0.521 | -19,933 | -21.15% |
| 2013 | 79 | 37.97% | -0.259 | 0.478 | -14,599 | -14.60% |
| 2014 | 106 | 47.17% | -0.101 | 0.691 | -9,556 | -12.96% |
| 2015 | 141 | 46.10% | -0.115 | 0.711 | -11,062 | -12.27% |
| 2016 | 126 | 40.48% | -0.226 | 0.475 | -20,560 | -21.69% |
| 2017 | 120 | 40.83% | -0.155 | 0.58 | -14,855 | -16.21% |
| 2018 | 142 | 44.37% | -0.096 | 0.763 | -8,133 | -9.69% |
| 2019 | 131 | 51.15% | -0.008 | 0.925 | -2,509 | -10.10% |
| 2020 | 127 | 40.94% | -0.181 | 0.645 | -12,456 | -13.55% |
| 2021 | 137 | 47.45% | -0.073 | 0.815 | -6,047 | -11.55% |
| 2022 | 100 | 40.00% | -0.217 | 0.554 | -15,217 | -16.46% |
| 2023 | 145 | 41.38% | -0.127 | 0.688 | -11,180 | -12.23% |
| 2024 | 104 | 38.46% | -0.168 | 0.631 | -11,241 | -12.08% |
| 2025 | 80 | 45.00% | -0.084 | 0.773 | -5,357 | -7.36% |
| 2026 | 11 | 45.45% | -0.157 | 0.608 | -1,490 | -2.31% |

## 5. Benchmarks

| Benchmark | CAGR | Sharpe | MaxDD | Notes |
|---|---|---|---|---|
| **Buy-and-hold (1 contract NQ)** | 1.97% | 0.719 | -9.00% | Naive long, no sizing |
| **Random entry (mean of 5 seeds)** | — | — | — | PF≈0.489, expectancy≈-0.185R — beats our strategy |

Random-entry uses the same NR7-style stop/target/sizing structure but picks direction at random with the same fire rate. If the strategy expectancy doesn't exceed the random benchmark by a clear margin, the apparent edge is a structural artifact (target/stop asymmetry, vol clustering, etc.) rather than a real signal.

## 6. Sensitivity sweep

Variations of target multiple (×0.75, ×1.0, ×1.25), stop distance (×0.75, ×1.0, ×1.25), and friction (×0.5, ×1.0, ×1.5, ×2.0) — 36 combinations.

- Profit factor: min=0.31, median=0.52, max=0.72.
- Sharpe: min=-3.11, median=-2.09, max=-1.13.
- Expectancy R: min=-0.427, median=-0.196, max=-0.091.
- **% of parameter combos with PF ≥ 1.1: 0%**.

Friction stress (target & stop fixed at nominal):

| friction × | n | win-rate | exp R | PF | CAGR | Sharpe | MaxDD |
|---|---|---|---|---|---|---|---|
| 0.5× | 1372 | 42.86% | -0.160 | 0.626 | -7.38% | -1.564 | -80.92% |
| 1.0× | 1299 | 42.65% | -0.176 | 0.577 | -8.18% | -1.767 | -84.34% |
| 1.5× | 1216 | 42.11% | -0.197 | 0.523 | -9.26% | -2.052 | -87.54% |
| 2.0× | 1136 | 41.29% | -0.222 | 0.481 | -10.23% | -2.304 | -89.94% |

## 7. Plots

- [Equity curve vs buy-and-hold](../results/equity_curve.png)
- [R-multiple distribution](../results/r_distribution.png)
- [Monthly returns](../results/monthly_returns.png)

## 8. Honest assessment

**Caveats and known weaknesses:**

- Daily-bar fill modeling cannot disambiguate whether the stop or target was hit first within `t+1`. We resolve conservatively as a stop-out, which biases the results downward when both are in range. Real-world fills (with intraday data) should be ≥ as good as reported.
- The 1.68 × NR7-range target was inherited from the source's *next-day full-range* stat, not the *excursion past the trigger*. The sensitivity sweep covers ±25% on either side; any conclusion that holds across the grid is robust to this misframing.
- Yahoo Finance NQ=F is a continuous front-month series with quarterly contract splice noise (~1.5% per AUDIT.md). Effect is small but real.
- TOPQ pre-commits a single direction on day `t`. Days with a 'doji-ish' mid-quartile close emit no signal, which is correct.
- We used a 70/30 chronological split, not k-fold. For daily strategies on 21 years this is acceptable; a stricter purged k-fold + Deflated Sharpe (Phase 3 K) would be appropriate before committing real capital.
- No regime filter applied to E1c or E1b (both are regime-stable per source v2).
- N_trials in the multiple-testing context is 17 (Phase 2) — even with BH, the best-of-17 Sharpe is modestly inflated. Treat the headline Sharpe as an upper bound; the bottom of the IQR of the sensitivity sweep is a more honest read.

## 9. Verdict for Phase 7

**Not live-deployable.** Edge does not survive realistic friction.
