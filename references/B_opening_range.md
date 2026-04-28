# B. Opening Range theory — Crabel, Fisher's ACD, Raschke

## Summary
The opening range (OR) — typically the first 5, 15, 30, or 60 minutes of cash-session trading — is the most-studied intraday reference in the literature. Toby Crabel's 1990 *Day Trading with Short Term Price Patterns and Opening Range Breakout* is the foundational empirical work: he tabulated breakout success rates conditional on prior-day patterns (NR4, NR7, ID, ID/NR4) and introduced the "Stretch" — a small-volatility offset added to the open to define entry triggers. Mark Fisher (*The Logical Trader*, 2002) repackaged the same OR backbone as ACD: A = breakout above the OR by a noise-tuned increment, C = failed A (false breakout), B/D = the symmetric reciprocals. Linda Raschke (*Street Smarts*, 1996, with Connors) productionized OR work for index futures and added the "Holy Grail" pullback (ADX>30 + retest of 20-EMA in trend) as a continuation pattern. Quantified backtests on NQ specifically (TradingStats.net, 6,142 days, 2014-2026) report a 39.4% double-break rate at 30-min and a 67% continuation-given-break rate — i.e. NQ is a *cleaner* breakout instrument than ES. NinjaTrader and others find that on NQ over 6 months the single-break IB has held ~82% of the time. This pattern is exactly what feeds D4 (open-candle color predicts which side gets retested) and B1 (9-10am candle gets retested by 11:00 90.5%).

## What's evidence vs marketing
- **Evidence-grade**: Crabel's original tables (volatility contraction → next-day expansion); the IB-retest statistic on index futures; Fisher's ACD core that "extension beyond OR + close beyond" is meaningfully different from "wick beyond OR" (this is the C vs A distinction, supported by all subsequent OR research).
- **Softer**: Raschke herself has stated publicly (recent webinars) that several Street Smarts setups have decayed due to widespread adoption — the Holy Grail still works, naive ORB does not. So treat naked ORB as low-edge and prefer conditional ORB (with an NR-day or gap context).
- **Marketing fluff**: "5-minute ORB will make you rich" content. The raw wick-touch breakout is ~random with poor R/R per the TradingStats study.

## Sources
- Crabel, Toby — *Day Trading with Short Term Price Patterns and Opening Range Breakout*, Traders Press, 1990. NR4/NR7/ID chapters and Stretch calculation. https://www.amazon.com/Trading-Short-Patterns-Opening-Breakout/dp/0934380171
- Fisher, Mark B. — *The Logical Trader: Applying a Method to the Madness*, Wiley, 2002. Ch. 1-4 on ACD points and pivot ranges. https://www.amazon.com/Logical-Trader-Mark-B-Fisher/dp/0471215511
- Raschke & Connors — *Street Smarts: High Probability Short-Term Trading Strategies*, M. Gordon Pub., 1996. Holy Grail chapter. Supplemental: Raschke's "Trading the Open" lecture, https://www.youtube.com/watch?v=Gze_mwL4-Z4
- TradingStats.net — "Opening Range Breakout (ORB) Strategy: 6,142 Days of ES & NQ" (2014-2026). https://tradingstats.net/orb-breakout-strategy-guide/
- NinjaTrader — "The Statistical Analysis of Trading Patterns" (initial-balance retest rates on NQ). https://ninjatrader.com/futures/blogs/the-statistical-analysis-of-trading-patterns/
