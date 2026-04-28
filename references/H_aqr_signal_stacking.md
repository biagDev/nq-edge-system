# H. AQR-style multi-signal stacking

## Summary
The AQR research canon (Asness, Moskowitz, Pedersen and co-authors) has, over 20+ years, formalized the idea that **combining weakly-correlated signals dominates picking the "best" one**. The math is elementary: portfolio Sharpe under independence scales with √N of similarly-Sharpe components. AQR's "Craftsmanship Alpha" (FAJ 2017) and "Alpha Beyond Expected Returns" papers articulate this for multi-factor equity selection (value × momentum × quality × low-vol), but the principle generalizes to any setting where you have multiple statistically positive signals with low pairwise correlation. Asness & Moskowitz & Pedersen's *Value and Momentum Everywhere* (JoF 2013) is the canonical empirical demonstration: value alone Sharpe ~0.4, momentum alone Sharpe ~0.5, **combined Sharpe ~0.8** because their correlation is mildly negative. The practical recipe: (1) test each signal in isolation; (2) measure pairwise return correlations of the *signal-conditional returns*, not the underlying instrument; (3) combine via inverse-vol weights or simple equal-risk; (4) gate at the portfolio level via vol-targeting rather than at the signal level.

For our shortlist of 8 BH-significant edges: their statistical conditioning is heterogeneous (open-candle color, gap size, prior-day range, NR7) so we can reasonably *expect* low pairwise correlation among the signal-conditional return streams. That is exactly the AQR setup. The expected uplift from combining is meaningful — going from a per-edge Sharpe of (say) 0.6 to a portfolio Sharpe of 1.0+ if correlations stay <0.3.

## What's evidence vs marketing
- **Evidence-grade**: The Sharpe-improves-with-diversified-uncorrelated-signals math is just statistics. AQR's specific factor results are heavily replicated and well-published.
- **Caveat**: Correlations rise in stress regimes. The "weakly correlated" assumption needs to be verified out-of-sample, not assumed. Use rolling windows.
- **Caveat 2**: Naïve summation overweights signals with overlapping conditioning. Many of our edges trigger on the same setup window (open + first hour), so they will not be truly independent — measure conditional-on-fire correlation, not unconditional.

## Sources
- Asness, C., Moskowitz, T., Pedersen, L. — "Value and Momentum Everywhere", *Journal of Finance*, 2013. Empirical workhorse for combining negatively-correlated signals. https://alphaarchitect.com/value-and-momentum-and-risk/
- Israel, R., Jiang, S., Ross, A. (AQR) — "Craftsmanship Alpha: An Application to Style Investing" (FAJ, 2017). https://www.aqr.com/-/media/AQR/Documents/Insights/Working-Papers/AQR--Craftsmanship-Alpha.pdf
- Ilmanen, A. (AQR) — "Alpha Beyond Expected Returns". https://images.aqr.com/-/media/AQR/Documents/Insights/White-Papers/Alpha-Beyond-Expected-Returns.pdf
- AQR — "Looking for the Intuition Underlying Multi-Factor Stock Selection". https://www.aqr.com/Insights/Perspectives/Looking-for-the-Intuition-Underlying-Multi-Factor-Stock-Selection
- Asness, C. — "Why Not 100% Equities" (1996), original portable-alpha intuition.

## Verdict
Adopt as the *combination layer*. Explicit recommendation for Phase 4: estimate the conditional return correlation matrix across our 8 edges, drop any pair with rho > 0.7 (they're really one edge), and combine the rest at equal risk-contribution.
