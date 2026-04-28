# K. Walk-forward, purged k-fold, Deflated Sharpe (López de Prado)

## Summary
Marcos López de Prado's *Advances in Financial Machine Learning* (Wiley, 2018) is the single most important practical reference for "your backtest Sharpe lies to you." The core insight: standard k-fold cross-validation **leaks information** in financial time series because (a) labels overlap (a 30-min forward return label at t-1 partially uses t+0 data), and (b) train and test sets are temporally adjacent. AFML proposes two corrections: **Purging** — drop training observations whose labels' time spans overlap test labels — and **Embargo** — additionally drop training observations within a small buffer after the test set, to prevent serial-correlation leakage. The combined technique is **Purged K-Fold Cross-Validation** (Ch. 7). For backtest combinatorics where you've tested many strategies and want to claim the best one is real, López de Prado's **Combinatorial Purged Cross-Validation (CPCV)** (Ch. 12) constructs many different train/test path combinations and reports the distribution of out-of-sample Sharpes. Recent comparison work (Arian et al., 2024) confirms CPCV materially outperforms walk-forward in false-discovery prevention.

The **Deflated Sharpe Ratio** (Bailey & López de Prado, 2014) handles the orthogonal problem of *selection bias from multiple testing*. If you tested N strategies and report the Sharpe of the best, the unconditional expected best-Sharpe-of-N-noise-strategies is positive even when all true Sharpes are zero — the **False Strategy Theorem**. DSR adjusts the observed best Sharpe downward by an explicit factor depending on (i) the variance of the candidate Sharpes you computed, (ii) the number of trials N, and (iii) skew/kurtosis of returns (since fat tails inflate naive Sharpe-to-p-value mappings).

The implication for us: with 14 studies tested and 10 BH-significant ones, we have a serious multiple-testing exposure. BH controls FDR but does not correct *Sharpe magnitude inflation*. Phase 4 must (a) re-validate via purged k-fold or CPCV, (b) report DSR for the combined system, (c) reserve a strict held-out 2025-2026 OOS window we never look at until final.

## What's evidence vs marketing
- **Evidence-grade**: All of this is published, peer-reviewed, and adopted by professional quant teams. There is no serious counterargument.
- **Caveat**: CPCV is computationally expensive and assumes label-time overlap is identifiable; for our intraday bar-level edges, label horizon = exit time, and we can construct it cleanly.

## Sources
- López de Prado, M. — *Advances in Financial Machine Learning*, Wiley, 2018. Ch. 7 (Cross-Validation in Finance, including Purging and Embargo), Ch. 12 (Backtesting through Cross-Validation, CPCV).
- Bailey, D. H., López de Prado, M. — "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", *Journal of Portfolio Management*, 2014. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 — full PDF: https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
- Arian, H., Norouzi, D., Seco, L. — "Backtest Overfitting in the Machine Learning Era: A Comparison of Out-of-Sample Testing Methods", 2024. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376
- Wikipedia — Purged cross-validation (clean technical summary). https://en.wikipedia.org/wiki/Purged_cross-validation
- Wikipedia — Deflated Sharpe Ratio. https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio

## Verdict
**Mandatory adoption.** Phase 4 validation must include purged k-fold (or CPCV) and DSR on the combined system. Without this, the 70-90% reported hit rates on our shortlist cannot be trusted as live Sharpe.
