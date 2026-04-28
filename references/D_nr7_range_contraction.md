# D. NR7 / range contraction → expansion (Crabel)

## Summary
Toby Crabel (*Day Trading with Short Term Price Patterns and Opening Range Breakout*, 1990) coined NR4 (today's range narrowest of last 4) and NR7 (narrowest of last 7), and showed empirically that low-volatility days are followed by above-average-range days at significantly higher than baseline rates. The mechanism Crabel proposed is structural: a narrow-range day reflects compressed disagreement among participants — pent-up positioning — which resolves on the next session. The pattern is regime-stable across markets and decades; replications by Connors/Raschke (*Street Smarts*), StockCharts ChartSchool, Oxfordstrat, QuantifiedStrategies, and more all reproduce the qualitative result that NR7 next-day range > average. Crabel's strongest setup is the **NR7-Inside-Day** (today is NR7 *and* range fits inside yesterday's range) — "double compression" — which historically shows the cleanest expansion stats. The famous extension is to combine NR7 with an opening-range breakout next day: enter on the OR break in the direction of the break, target ATR. This is exactly the home of E1c (NR7 → 83.5% next-day expansion in our data).

## What's evidence vs marketing
- **Evidence-grade**: The NR7-then-expansion phenomenon is one of the most-replicated intraday patterns in the literature — multiple independent backtests across decades, instruments, and exchanges. Our 83.5% on NQ is consistent.
- **Important caveat**: NR7 predicts *range expansion*, **not direction**. Crabel was explicit about this; many secondary writeups conflate the two. So E1c needs a directional layer (e.g. ORB-on-NR7-day, gap direction, etc.), not a coin-flip entry.
- **Marketing fluff**: "NR7 strategy 90% win rate" content typically cherry-picks. The honest finding is "expected next-day range substantially > unconditional expected range," which compounds into edge only when paired with a reasonable directional trigger.

## Sources
- Crabel, Toby — *Day Trading with Short Term Price Patterns and Opening Range Breakout*, Traders Press, 1990. Especially the NR4 and NR7 tables (Ch. 4-5) and the discussion of expansion conditional on prior-day pattern.
- StockCharts ChartSchool — "Narrow Range Day NR7" (clean primary-source-style writeup with formulas). https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/narrow-range-day-nr7
- Time-Price-Research — "Narrow Range 4, Narrow Range 7, and Inside Days | Toby Crabel" (replicated stats, notes original sample sizes from Crabel's book). https://time-price-research-astrofin.blogspot.com/2023/09/nr4-nr7-narrow-range-4-7-id-inside-days.html
- TradingStrategiesDaily — "The NR7ID: Toby Crabel's Powerful Double-Compression Trading Setup". https://tradingstrategiesdaily.com/p/nr7id-toby-crabel
- Oxfordstrat — "Price Breakout with NR7" (entry/exit specification). https://oxfordstrat.com/trading-strategies/price-breakout-nr7/

## Verdict
Best-supported framework in the entire literature for E1c. Pair with an OR break or gap-direction filter to get directional edge.
