# C. Mark Fisher's ACD Method

## Summary
ACD is Fisher's framework — published in *The Logical Trader* (Wiley, 2002) — for using the daily Opening Range as the day's primary reference. The opening range length is calibrated to instrument volatility (Fisher uses ~10-15 minutes for liquid futures; on NQ practitioners typically use the 9:30-9:45 window). Four reference points are placed against the OR: **A-up / A-down** = a breakout of the OR by a noise-tuned increment (the "A" amount, derived from average true range); these are the early-trend trigger. **C-up / C-down** = a failure / reversal of an A signal (price re-enters the OR after triggering A); these are mean-reversion triggers. **B / D** are symmetric definitions used as stops. Layered on top is the "Pivot Range" (PR), a 3-day average of (H+L+C)/3, H, L — used as a longer-horizon bias filter: when the OR is entirely above the PR, A-up signals get higher conviction. ACD's main insight is *not* that ORs predict — it's that conditional on an A-then-not-C, the day usually trends; conditional on a C, the day is rotational.

## What's evidence vs marketing
- **Evidence-grade**: Fisher's "A vs C" distinction is the conceptual ancestor of both the modern "double-break filter" used in NQ ORB studies and ICT's "liquidity sweep then return". The Pivot Range bias filter is just a 3-day rolling pivot — uncontroversial.
- **Softer**: The exact A/C offset values Fisher publishes are calibrated to early-2000s volatility on a small set of instruments and need re-tuning for NQ post-2018 vol regime. Fisher himself reportedly told seminar attendees (Elite Trader threads) that "if you just trade the levels you will be a net loser — you still need execution skill." Treat ACD as a *framework* that pairs with our retest stats, not as a turnkey signal.
- **Marketing fluff**: Several paid "ACD indicator" packages on TradingView/MT5 are reskins of the public formula. The original book is the source.

## Sources
- Fisher, Mark B. — *The Logical Trader: Applying a Method to the Madness*, Wiley, 2002. Foreword by Paul Tudor Jones; especially Ch. 1 (OR definition + A/C derivation), Ch. 3 (Pivot Range), Ch. 5 (combining OR with PR for daily bias). https://www.amazon.com/Logical-Trader-Mark-B-Fisher/dp/0471215511
- Elite Trader thread — "Excerpts From the (1400 page) ACD Method Thread (Mark Fisher)" — practitioner discussion, including Fisher's own caveats. https://www.elitetrader.com/et/threads/excerpts-from-the-1400-page-acd-method-thread-mark-fisher.377419/
- NexusFi Academy — "ACD Trading Method: Mark Fisher's Opening Range Framework for Futures". https://nexusfi.com/a/strategies/acd-trading-method
- DAcharts — "Mark Fisher's Logical Trader ACD Method" (clean diagrammatic walkthrough). http://www.dacharts.com/templates/descr/ACDmethod.htm

## Verdict
Most directly useful framework for D4 (9:30 candle color → which side retests). The A/C taxonomy gives us a vocabulary for "the open extended one way then the other side became the magnet" which is exactly D4's mechanism.
