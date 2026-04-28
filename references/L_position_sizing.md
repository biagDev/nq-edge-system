# L. Position sizing — Kelly, fractional Kelly, vol targeting

## Summary
The Kelly criterion (Kelly 1956) gives the bet fraction f* = edge/odds that maximizes log-wealth growth. For a continuous return process with mean μ and variance σ², the analog is f* = μ/σ² — formally identical to Markowitz mean-variance with log utility. **Full Kelly is mathematically optimal but practically catastrophic** for fat-tailed financial assets because (a) μ and σ² are estimated, not known — even small estimation error pushes you above true-Kelly into a region where growth is *negative*; (b) returns are non-Gaussian with fat negative tails — the second-moment-only formula understates true ruin probability; (c) drawdowns under full Kelly can exceed 80%, beyond practical pain tolerance and often beyond margin / regulatory limits. **Fractional Kelly** (typically 0.25× to 0.5×) is the standard professional response: MacLean/Ziemba/Blazenko (1992) show Half-Kelly captures ~75% of full-Kelly growth at ~50% of volatility. Most professional CTAs run *much* smaller — 10-25% of Kelly equivalent.

**Volatility targeting** is the modern continuous-version analog: scale position size so realized portfolio vol stays at a target (e.g., 10% annualized). Empirically (Harvey/Hoyle/Korgaonkar/Rattray/Sargaison/Van Hemert 2018, "The Impact of Volatility Targeting"), vol targeting consistently improves Sharpe for risk assets (S&P from 0.40 to ~0.50) and reduces tail-loss probability across 60+ instruments, especially in regime shifts. The mechanism: vol clusters, so cutting size when realized vol is high reduces dollar-loss exposure during the regimes that produce most drawdowns.

For our system: **never run full Kelly.** Recommended path: (1) compute per-edge fixed-fractional risk (e.g., 0.5% of equity per trade as the R unit, à la Van Tharp), (2) scale that R by inverse-realized-vol of NQ (rolling 20-day) to target constant return-vol, (3) cap aggregate concurrent risk across edges at a fraction (e.g., 2-3%) of equity to handle correlated-fire scenarios.

## What's evidence vs marketing
- **Evidence-grade**: Kelly math; MacLean/Ziemba simulations; Harvey et al. vol-targeting paper.
- **Caveat**: Vol targeting helps most when vol is persistent (clusters); on instruments where vol is mean-reverting fast, the benefit shrinks. NQ vol clusters reasonably well.
- **Marketing**: "Kelly will make you rich" content. Anyone selling full-Kelly is ignoring tail risk.

## Sources
- Kelly, J. L. — "A New Interpretation of Information Rate", *Bell System Technical Journal*, 1956 (original).
- MacLean, L., Ziemba, W., Blazenko, G. — "Growth Versus Security in Dynamic Investment Analysis", *Management Science*, 1992. (Half-Kelly captures 75% growth, 50% vol.)
- Harvey, C., Hoyle, E., Korgaonkar, R., Rattray, S., Sargaison, M., Van Hemert, O. — "The Impact of Volatility Targeting", *Journal of Portfolio Management*, 2018. https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf
- Stat Berkeley — "Good and bad properties of the Kelly criterion" (Aldous lecture notes; clean fat-tail caveats). https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf
- AlphaArchitect — "Volatility Targeting Improves Risk-Adjusted Returns". https://alphaarchitect.com/volatility-targeting-improves-risk-adjusted-returns/

## Verdict
Use fractional Kelly (≤0.25×) inside a vol-targeting envelope. Never full Kelly. Aggregate cap at ~2% concurrent risk.
