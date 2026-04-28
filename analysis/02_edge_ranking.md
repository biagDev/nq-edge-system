# Phase 2 — Edge Ranking

Wilson 95% CIs, two-proportion z-test vs a stated base rate, Benjamini-Hochberg FDR correction at q=0.10. Tradeability score 1-5 combines sample size, BH-adjusted significance, lift magnitude, and regime stability (Phase 1 + source AUDIT.md).

Cost model used for the R-multiple sanity check: $4 RT commission + 1 tick slippage per side on full NQ ($20/pt). Round-trip cost ≈ 0.7 pts ≈ $14 per contract per round trip.

## Ranked table

| # | Edge | Family | k/n | rate | base | lift (pp) | Wilson 95% CI | p (z) | p-adj BH | BH rej | regime | trad. | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | D4: red 9:30 → low retest by 10:00 | intraday-15m | 82/111 | 0.739 | 0.210 | +52.87 | [0.650, 0.811] | 0.0 | 0.0 | ✓ | ? | 5 | Mirror of green case. |
| 2 | D4: green 9:30 → high retest by 10:00 | intraday-15m | 88/119 | 0.740 | 0.243 | +49.63 | [0.654, 0.810] | 0.0 | 0.0 | ✓ | ? | 5 | Color = side. Compared vs the high-retest rate on red-9:30 days. |
| 3 | B1: 9-10am 1h candle either-side retest by 11:00 | intraday-15m | 210/232 | 0.905 | 0.500 | +40.52 | [0.861, 0.936] | 0.0 | 0.0 | ✓ | ? | 5 | Auction rotation. Null = 50% (no informed prior). |
| 4 | E1b: top-Q close → higher high next day | daily | 2071/2419 | 0.856 | 0.500 | +35.63 | [0.842, 0.870] | 0.0 | 0.0 | ✓ | ✓ stable | 5 | Largest-n signal in repo. Predicts extension, not direction. |
| 5 | E1c: NR7 → next-day range expansion | daily | 872/1044 | 0.835 | 0.500 | +33.52 | [0.811, 0.857] | 0.0 | 0.0 | ✓ | ✓ stable | 5 | Regime-stable per E2. |
| 6 | E1b: bottom-Q close → lower low next day | daily | 1318/1598 | 0.825 | 0.500 | +32.48 | [0.805, 0.843] | 0.0 | 0.0 | ✓ | ✓ stable | 5 | Mirror. Robust per E2. |
| 7 | B2: 6-10am 4h candle either-side retest by 11:00 | intraday-15m | 188/232 | 0.810 | 0.500 | +31.03 | [0.755, 0.856] | 0.0 | 0.0 | ✓ | ? | 5 | Larger window. Null = 50%. |
| 8 | D1: PDH or PDL retested in first hour | intraday-15m | 172/222 | 0.775 | 0.500 | +27.48 | [0.715, 0.825] | 0.0 | 0.0 | ✓ | ? | 5 | Null = 50%. |
| 9 | E1d: medium gap (25-50pt) fills same day | daily | 119/176 | 0.676 | 0.500 | +17.61 | [0.604, 0.741] | 0.00079 | 0.00134 | ✓ | ✓ stable | 5 | Robust above/below MA per E2 (70.95 vs 69.41). |
| 10 | D2: 9:30 retest within first 15m bar (vs first 30m null) | intraday-15m | 203/223 | 0.910 | 0.780 | +13.00 | [0.866, 0.941] | 0.00015 | 0.00028 | ✓ | ? | 4 | Frames 'is the retest fast?' rather than 'does retest happen?' |
| 11 | C1: Red 9:30 + LO retest → red close | intraday-15m | 56/80 | 0.700 | 0.400 | +30.00 | [0.592, 0.789] | 0.00673 | 0.01041 | ✓ | ? | 3 | Mirror. |
| 12 | C1-wide: Red wide-body 9:30 + LO retest → red close | intraday-15m | 39/49 | 0.796 | 0.548 | +24.75 | [0.664, 0.885] | 0.01859 | 0.02633 | ✓ | ? | 3 | Strongest-looking bearish setup in repo. |
| 13 | C1: Green 9:30 + HI retest → green close | intraday-15m | 61/85 | 0.718 | 0.520 | +19.76 | [0.614, 0.802] | 0.06411 | 0.07266 | ✓ | ? | 2 | Counterfactual = same color, wrong-side retest (no edge per source). |
| 14 | E1d: large gap (50-100pt) fills same day | daily | 52/77 | 0.675 | 0.493 | +18.18 | [0.565, 0.769] | 0.02207 | 0.02886 | ✓ | ? | 2 | Smaller n. |
| 15 | E1a: 4-green streak → next day green | daily | 155/259 | 0.599 | 0.502 | +9.65 | [0.538, 0.656] | 0.02724 | 0.03308 | ✓ | ✗ fragile | 2 | Regime-DEPENDENT — only works above 200MA. |
| 16 | E2: top-Q close + above-200MA → higher high | daily | 1553/1808 | 0.859 | 0.838 | +2.13 | [0.842, 0.874] | 0.22045 | 0.23423 | ✗ | ✓ stable | 2 | Above-MA vs below-MA — regime test. |
| 17 | C1-wide: Green wide-body 9:30 + HI retest → green close | intraday-15m | 30/39 | 0.769 | 0.674 | +9.53 | [0.617, 0.874] | 0.33065 | 0.33065 | ✗ | ? | 1 | Wide vs narrow same-color same-side. n is small. |

## Shortlist (tradeability ≥ 4 and BH-significant)

- **D4: red 9:30 → low retest by 10:00** — k=82/n=111, rate 73.9%, lift +52.9pp, BH p=0.0. Mirror of green case.
- **D4: green 9:30 → high retest by 10:00** — k=88/n=119, rate 74.0%, lift +49.6pp, BH p=0.0. Color = side. Compared vs the high-retest rate on red-9:30 days.
- **B1: 9-10am 1h candle either-side retest by 11:00** — k=210/n=232, rate 90.5%, lift +40.5pp, BH p=0.0. Auction rotation. Null = 50% (no informed prior).
- **E1b: top-Q close → higher high next day** — k=2071/n=2419, rate 85.6%, lift +35.6pp, BH p=0.0. Largest-n signal in repo. Predicts extension, not direction.
- **E1c: NR7 → next-day range expansion** — k=872/n=1044, rate 83.5%, lift +33.5pp, BH p=0.0. Regime-stable per E2.
- **E1b: bottom-Q close → lower low next day** — k=1318/n=1598, rate 82.5%, lift +32.5pp, BH p=0.0. Mirror. Robust per E2.
- **B2: 6-10am 4h candle either-side retest by 11:00** — k=188/n=232, rate 81.0%, lift +31.0pp, BH p=0.0. Larger window. Null = 50%.
- **D1: PDH or PDL retested in first hour** — k=172/n=222, rate 77.5%, lift +27.5pp, BH p=0.0. Null = 50%.
- **E1d: medium gap (25-50pt) fills same day** — k=119/n=176, rate 67.6%, lift +17.6pp, BH p=0.00134. Robust above/below MA per E2 (70.95 vs 69.41).
- **D2: 9:30 retest within first 15m bar (vs first 30m null)** — k=203/n=223, rate 91.0%, lift +13.0pp, BH p=0.00028. Frames 'is the retest fast?' rather than 'does retest happen?'

## Discarded for Phase 5

- C1: Green 9:30 + HI retest → green close — score 2, BH-significant, n=85.
- E1d: large gap (50-100pt) fills same day — score 2, BH-significant, n=77.
- E1a: 4-green streak → next day green — score 2, BH-significant, n=259.
- E2: top-Q close + above-200MA → higher high — score 2, NOT BH-significant, n=1808.
- C1-wide: Green wide-body 9:30 + HI retest → green close — score 1, NOT BH-significant, n=39.

## Method notes

- **Base rates** are the natural counterfactual where one exists (e.g. opposite-color rows for D4 / C1). Where no clean counterfactual is available, we use the agnostic null of 50% — this is conservative for one-sided directional claims and biases p-values upward (i.e. we under-reject).
- **Multiple comparisons:** BH at q=0.10 on the full set of 17 tests. With this many tests, raw p<0.05 is insufficient.
- **Sample-size flag:** anything with n<100 is a yellow card. C1 wide-body sub-buckets (n≈31-49) survive only because their lift is large; the CIs are wide and we treat the magnitude as indicative, not precise.
- **Regime stability:** drawn from `daily-patterns-v2` 200MA split for daily edges. For intraday edges the source has not tested regime sensitivity — Phase 6 should add it as a robustness check.
- **R-multiple after costs:** computed in code (`src/stats/edge.py:expected_r_after_costs`) but not tabulated row-wise here because it depends on the trade construction (stop, target) which is a Phase-5 decision, not a Phase-2 one. We re-visit it in Phase 5/6.
