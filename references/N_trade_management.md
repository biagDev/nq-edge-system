# N. Trade management — scaling, breakeven, partials

## Summary
The empirical literature on trade-management overlays (scaling out, moving stop to breakeven, taking partial profits) is much thinner than retail trading culture suggests. The honest finding across the few rigorous studies and credible practitioner write-ups (Acar & Toffel 2000 on stop-losses; Dave Mabe 2018 partials simulation; the broader trend-following backtest literature) is:

1. **Stops** — stop-losses systematically underperform on assets with positive autocorrelation (trends) and modestly help on assets with negative autocorrelation (mean-reverting). For NQ intraday, where short-horizon autocorrelation flips sign by regime, stops are essentially neutral on average and exist primarily for *risk control*, not for *expectancy*.
2. **Move-to-breakeven** — moving the stop to entry after some favorable excursion **reduces win rate without proportionally increasing R per win**, because price often retests the entry level before resuming. Empirically negative-EV unless the breakeven move happens after structural confirmation (e.g., a higher-low forms above entry), not after a fixed dollar move.
3. **Scaling out / partials** — also empirically weak in pure-expectancy terms. Mabe's simulation (and several others) shows that taking partials at 1R while letting "runners" go to target *underperforms* a single full-size exit at target on positive-skew systems (where the runners drive the edge), and is approximately neutral on symmetric systems. The reason: the partial at 1R steals from your right-tail wins, which is precisely where positive-skew systems make their money.
4. **The legitimate use case for partials** is **psychological / drawdown smoothing**, not expectancy. If taking partials lets you actually hold the runner instead of stopping out emotionally, then the partial is +EV in the *behavioral* sense.

## What's evidence vs marketing
- **Evidence-grade**: Acar/Toffel on stops; the trend-following literature on letting winners run; Mabe's clean partial-vs-full simulation.
- **Marketing fluff**: "Always take partials at 1R" is rule-of-thumb mythology; "always move to breakeven after X ticks" likewise. Both have negative expected EV in straightforward simulations.
- **Reasonable defaults for our system**: single fixed-target exit per edge (computed from edge-specific structural targets — opposite IB extreme for B1, prior-day high for D1, etc.), no scaling out, hard stop at edge invalidation level, no breakeven moves.

## Sources
- Acar, E., Toffel, R. — "Stop-loss and Investment Returns", 2000. https://www.actuaries.org.uk/system/files/documents/pdf/stop-loss-and-investment-returns.pdf
- Mabe, D. — "Should you EVER take Partial Profits?". https://davemabe.com/should-you-ever-take-partials
- Hurst/Ooi/Pedersen — *A Century of Evidence on Trend-Following Investing* (indirect: shows winners-run logic is essential for trend-style edges).
- JournalPlus — "Trade Management: Entries, Exits & Scaling" (practitioner-grade walkthrough). https://journalplus.co/learn/guides/trade-management-guide/
- Forex.com Academy — "Scaling In and Out of Trade Positions" (representative retail pro framing). https://www.forex.com/en-us/trading-academy/courses/advanced-risk-management/scaling-of-trades/

## Verdict
**Default: single hard stop, single structural target, no scaling, no breakeven moves.** Optionally A/B test breakeven-after-structural-confirmation for trend-following edges (E1b/E1d). Resist partials unless you find clear evidence in our backtest that they improve expectancy *and* not just Sharpe-via-vol-reduction.
