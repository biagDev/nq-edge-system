# O. Session structure for index futures (IB, day types, profile evolution)

## Summary
Beyond AMT (topic A), there is a body of practitioner work on how the NQ/ES session evolves through the day in predictable phases. The dominant taxonomy is **Dalton's six day types** (Mind Over Markets):

1. **Normal Day** — wide IB (first hour) contains most of the day's range; rest of session rotates inside IB. ~10-15% of days.
2. **Normal Variation** — IB extension on one side, but contained move; the most common day type, ~35-40%.
3. **Trend Day** — IB extension dominates; close near extreme; IB extreme NOT retested. ~10-15%; the day type that *kills* retest edges.
4. **Double-Distribution Trend Day** — early balance, midday breakout, new balance. ~5-10%.
5. **Neutral Day** — extension on both sides of IB, close inside (centered).
6. **Neutral-Extreme Day** — extension on both sides, close at one extreme.

The 80/20 practical rule: ~70-80% of days are rotational (Normal, Normal-Variation, Neutral) — these are the days where IB-retest, prior-H/L-retest, and 9:30-candle-color edges work. ~20-30% are trending — these are the days where extension edges work and retest edges fail. **A regime gate that estimates "trend probability" early in the session would materially improve risk-adjusted returns** by suppressing retest entries on trend days.

Practitioner extensions: the **Initial Balance extension rule** (if price extends 1× IB beyond the IB high/low, probability of trend day rises sharply; if it extends 2× IB, the day is almost certainly a trend day with the close near the extreme); the **value-area open relationship** (open-above-VAH vs open-below-VAL vs open-inside-VA — Dalton claims open-inside-VA produces ~70% rotational days; open-outside-VA splits more evenly).

## What's evidence vs marketing
- **Evidence-grade**: The day-type frequencies are stable across decades of CME data and have been re-verified by practitioners many times; the IB-extension-magnitude → trend-day mapping is empirically robust.
- **Softer**: The exact percentages move with regime; numbers above are ballpark — re-verify on our specific 2014-2026 NQ window.
- **Marketing**: A lot of "day-type prediction" content sells deterministic-looking systems that are really just statistics-of-base-rates with extra steps.

## Sources
- Dalton, James F. — *Mind Over Markets* (Updated Edition, Wiley, 2013), Ch. 4 (six day types) and Ch. 6 (IB extension and trend-day characteristics).
- Dalton, James F. — *Mind Over Markets Continued: Integration of Market Profile with Momentum Trading*, Jim Dalton Trading. https://jimdaltontrading.com/product/mind-over-markets-continued-a-deep-dive/
- Time-Price-Research — "Six Types of Market Days: Mind Over Markets". https://time-price-research-astrofin.blogspot.com/2023/03/six-types-of-market-days-mind-over.html
- NinjaTrader — "The Statistical Analysis of Trading Patterns" (NQ-specific IB and break-then-continuation stats over recent windows). https://ninjatrader.com/futures/blogs/the-statistical-analysis-of-trading-patterns/
- TradingStats — "Opening Range Breakout Strategy: 6,142 Days of ES & NQ" (modern empirical day-type frequencies). https://tradingstats.net/orb-breakout-strategy-guide/

## Verdict
Build a **trend-day classifier** as a first-class regime gate. Inputs: (1) IB extension magnitude by 11:00, (2) gap size and direction, (3) prior-day type. Output: trend probability. Use this to mute D1/D2/B1 retest entries on high-trend-probability days, and to boost E1b/E1c/E1d extension entries.
