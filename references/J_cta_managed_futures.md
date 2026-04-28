# J. CTA / managed-futures intraday models

## Summary
The public CTA literature is overwhelmingly about **medium-to-long-horizon trend-following** (20-day to 500-day breakouts, time-series momentum). The canonical references (Moskowitz/Ooi/Pedersen 2012 *Time Series Momentum*, Hurst/Ooi/Pedersen *A Century of Evidence on Trend-Following*, AQR Trends Everywhere 2024) demonstrate robust positive Sharpes for trend across asset classes over a century. **Intraday CTA models exist but are not publicly disclosed** — most large CTAs (Winton, Man AHL, Aspect, Two Sigma's CTA arm) layer short-horizon trade-execution and microstructure models on top of slower trend signals, but they do not publish those layers. Recent academic work (Re-evaluating Short- and Long-Term Trend Factors in CTA Replication, Bayesian Graphical Approach, arXiv 2025) decomposes CTA returns into 20/60/125/250/500-day mono-horizon strategies and finds that adding short-horizon trend (20-day) modestly improves Sharpe but introduces higher turnover and execution sensitivity. Public-domain practitioner guidance (Return Stacked Portfolios, CFA Institute "Decoding CTA Allocations by Trend Horizon") confirms the consensus: short-horizon CTA-style trend has thinner edges and is more cost-sensitive than long-horizon.

The relevance to our project is limited but real: the trend-day vs balance-day distinction (per Dalton) matters for *which of our edges fires correctly*. On trend days, retest edges (D1, D2, B1) decay (because IB extremes break and don't get retested) while extension edges (E1b, E1c) work. On balance days the inverse. So a CTA-style daily trend filter could be useful as a *regime gate*, not as a signal source.

## What's evidence vs marketing
- **Evidence-grade**: Long-horizon trend-following has overwhelming academic and live-track-record evidence. AQR Trends Everywhere is the gold-standard citation.
- **Evidence-thin**: Specific intraday CTA techniques are not publicly disclosed, and most public "CTA-style intraday" content is retail repackaging.
- **Marketing**: ETF wrappers (Simplify CTA etc.) sell the concept but don't reveal models.

## Sources
- Moskowitz, T., Ooi, Y. H., Pedersen, L. — "Time Series Momentum", *Journal of Financial Economics*, 2012.
- Hurst, B., Ooi, Y. H., Pedersen, L. — "A Century of Evidence on Trend-Following Investing" (AQR working paper, multiple updates).
- AQR — "Trends Everywhere" (JOIM, 2024). https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/AQR-Trends-Everywhere_JOIM.pdf
- "Re-evaluating Short- and Long-Term Trend Factors in CTA Replication: A Bayesian Graphical Approach", arXiv 2507.15876, 2025. https://arxiv.org/html/2507.15876v1
- CFA Institute — "Decoding CTA Allocations by Trend Horizon", Jan 2026. https://blogs.cfainstitute.org/investor/2026/01/28/decoding-cta-allocations-by-trend-horizon/

## Verdict
Use a daily trend filter (e.g., sign of 20-day return, or close vs 50-day SMA on NQ) as a **regime gate** on our intraday edges, especially to suppress retest edges on trend days.
