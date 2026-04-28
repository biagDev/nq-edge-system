# M. Van Tharp R-multiples / expectancy

## Summary
Van Tharp (*Trade Your Way to Financial Freedom*, 1998; *Definitive Guide to Position Sizing*, 2008) standardized the language and bookkeeping of trading-system evaluation. **R** = the initial dollar risk on a trade (entry minus stop, times contract size). Every trade outcome is then expressed as a **multiple of R** (1R win = made what you risked; -1R loss = stop-out; 3R win = made three times the risk). **Expectancy** = average R-multiple per trade = win_rate × avg_win_R − loss_rate × avg_loss_R. The framework decomposes a trading system into orthogonal building blocks:

1. **Setup** — context filter (e.g., "NR7 day", "open is green and inside last 30-day range")
2. **Trigger** — entry signal that fires given setup (e.g., "break above 9:45 high")
3. **Entry** — order type and price (market, limit at level, stop)
4. **Stop / Invalidation** — the price that kills the thesis; defines R
5. **Profit target / exit rule** — fixed multiple of R, structural target, time stop, or trailing
6. **Position sizing** — number of contracts as a function of R-per-contract and account R-per-trade

Tharp's **System Quality Number** (SQN = expectancy / std(R) × √N) is a Sharpe-analog at the trade level. The framework is uncontroversial bookkeeping — it doesn't manufacture edge but it makes edges comparable across instruments and styles, and it cleanly separates *signal quality* (expectancy in R) from *bet sizing* (R per trade in dollars).

## What's evidence vs marketing
- **Evidence-grade**: The decomposition is just clean accounting and is universally adopted by professional traders, prop firms, and automated systems.
- **Marketing**: Tharp's institute also sells personality-typing courses ("trader psychology") that are weaker. Stick to the R-multiple bookkeeping; ignore the personality marketing.

## Sources
- Van Tharp — *Trade Your Way to Financial Freedom*, McGraw-Hill, 2nd ed. 2007. Ch. 6 (Expectancy), Ch. 12-14 (Position Sizing).
- Van Tharp Institute — "Tharp Think Trading Concepts" (free summary). https://vantharpinstitute.com/tharp-think-trading-concepts/
- TraderLion — "R and R-Multiples". https://traderlion.com/risk-management/r-and-r-multiples/
- Trademetria — "What Are R-Multiples? The Key Metric Every Trader Should Know". https://trademetria.com/blog/what-are-r-multiples-the-key-metric-every-trader-should-know/
- The Trade Risk — "Every trader should think in R-Multiples". https://www.thetraderisk.com/every-trader-should-think-in-r-multiples/

## Verdict
Adopt the Setup-Trigger-Entry-Stop-Target-Sizing decomposition as the **canonical strategy spec format** for Phase 4. Every shortlisted edge gets converted to this skeleton.
