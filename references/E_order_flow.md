# E. Order flow / footprint / delta / absorption

## Summary
Order flow analysis works at a finer granularity than OHLC. The core constructs are: **footprint chart** (per-bar bid×price×ask volume matrix), **delta** (signed net of aggressor-buyer minus aggressor-seller volume in a bar), **cumulative delta** (CVD, the running sum), **absorption** (large aggressive volume on one side that fails to move price — interpreted as a passive limit-order wall), and **imbalance** (asymmetric stacked bid vs offer prints across diagonals). The honest professional view: order flow is primarily an **execution refinement layer** — it sharpens entries and exits inside an edge that already has positive expectancy at the bar level, but it does not, on its own, manufacture edge. The HFT literature (Easley/de Prado VPIN, Cont/Kukanov/Stoikov OFI) supports the existence of micro-structural information in flow over horizons of seconds-to-minutes, but its decay is fast and its capture requires low-latency infrastructure that retail simply doesn't have. For our shortlist (which lives at 1m-15m bar-level edges), order flow is best treated as: (a) optional confirmation for the *retest entry* (e.g., absorption at the prior-day high), (b) optional invalidation for fades (delta divergence), (c) NOT a precondition.

## What's evidence vs marketing
- **Evidence-grade (academic)**: Order Flow Imbalance (Cont et al. 2014) predicts very-short-horizon returns. VPIN (Easley/de Prado) predicts adverse-selection regimes. These are real but operate on ms-to-second scales.
- **Evidence-thin**: Specific "footprint patterns" (single-print imbalance ladders, exhaustion stacks) sold by retail orderflow vendors typically have no published statistical validation. Most prop-firm and YouTube content on absorption is anecdotal.
- **Marketing fluff**: "Read the tape and beat algos" courses. You cannot out-tape institutional algos at retail latency. The legitimate retail use is *contextual confirmation*, not *signal generation*.

## Sources
- Cont, R., Kukanov, A., Stoikov, S. — "The Price Impact of Order Book Events" (Journal of Financial Econometrics, 2014). Foundational OFI paper.
- Easley, López de Prado, O'Hara — "The Microstructure of the Flash Crash: Flow Toxicity, Liquidity Crashes and the Probability of Informed Trading" (JPM, 2011). VPIN.
- NinjaTrader — "Footprint Charts Explained: Order Flow Trading" (vendor guide; useful taxonomy, treat conclusions as marketing). https://ninjatrader.com/futures/blogs/ninjatrader-order-flow/
- ATAS — "Delta and Cumulative Delta: how could they help a day trader?". https://atas.net/atas-possibilities/indicators/what-is-delta/
- LiteFinance / DayTradingProfitCalculator overviews of footprint+delta+CVD (representative retail-vendor framing). https://www.litefinance.org/blog/for-beginners/trading-strategies/order-flow-trading-with-footprint-charts/

## Verdict
Optional execution refinement only. Do **not** make order-flow signals a precondition for any of the eight shortlisted edges; possibly add a small order-flow confirmation gate (e.g., delta sign agrees with retest direction) as an A/B variant in Phase 4.
