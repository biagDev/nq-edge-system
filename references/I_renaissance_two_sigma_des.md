# I. Renaissance / Two Sigma / D.E. Shaw — "many small edges"

## Summary
The defining philosophy of the systematic-quant elite is captured by Robert Mercer's Renaissance quote: "We're right 50.75% of the time, but we're 100% right 50.75% of the time." Translated: an edge of half a percentage point, repeated across 150,000-300,000 daily trades and many uncorrelated instruments, is the foundation of the Medallion Fund's ~66% gross annualized returns over decades. The supporting Simons quote (multiple lectures, *The Man Who Solved the Market*, Zuckerman 2019): "Patterns of price movement are not random. However, they're close enough to random so that getting some excess, some edge out of it, is not easy and not so obvious." D.E. Shaw and Two Sigma have published less but follow the same paradigm — David Shaw's early-1990s pitch decks emphasize portfolios of hundreds of micro-strategies rather than a few big bets; Two Sigma's public talks (e.g. Alfred Spector, John Overdeck interviews) describe the "factory model" — an industrialized research pipeline producing many small-decay alphas that are stitched together by a portfolio optimizer with strict cost models and risk constraints.

The implication for our project is direct and humbling: even at the absolute top of the sophistication ladder, the per-trade edge is fractions of a percent. Our shortlist has 70-90% conditional hit rates — that is *huge* by Renaissance standards, which strongly suggests either (a) we have selection / look-ahead bias somewhere, (b) the realized R:R is unfavorable enough to neutralize most of it, or (c) we are operating at a much smaller scale than they are and edges available at our scale haven't been arbitraged. Honest answer: probably some mixture of (b) and (c), with (a) requiring careful purged k-fold to rule out.

## What's evidence vs marketing
- **Evidence-grade**: Mercer's quote is on the public record; Medallion's audited returns are well documented; Zuckerman's book (2019) is the most reliable journalistic account.
- **Caveat**: Renaissance also has unique advantages we don't — lowest-cost execution, leverage, and a tightly-held internal employee-only fund. Don't read "0.5% edge per trade × N is enough" as instructions for retail; we need bigger per-trade edge because we have higher costs and lower turnover.
- **Marketing fluff**: Almost everything online claiming to "reveal Renaissance's secret algorithms". The actual algorithms are not public; the *philosophy* is.

## Sources
- Zuckerman, Gregory — *The Man Who Solved the Market: How Jim Simons Launched the Quant Revolution*, Penguin, 2019. Especially Ch. 9-12 on the assembly of the Medallion edge stack.
- Mercer's "50.75%" quote — multiple secondary sources but originally Sebastian Mallaby, *More Money Than God*, 2010.
- BuildAlpha — "Jim Simons - The Man Who Solved the Market" (book summary with traceable quotes). https://www.buildalpha.com/jim-simons-the-man-who-solved-the-market/
- QuantifiedStrategies — "How Jim Simons' Trading Strategies Achieved 66% Annual Returns". https://www.quantifiedstrategies.com/jim-simons/
- Edgeful — "Jim Simons trading strategy: systematic approach that made $100+ billion". https://www.edgeful.com/blog/posts/jim-simons-trading-strategy-systematic-approach

## Verdict
Adopt as **philosophy**, not as method. The lesson is: combine many small edges, control costs obsessively, never bet the farm on any one. We should be *suspicious* that our reported hit rates are so high, and the response should be aggressive purged-CV and DSR.
