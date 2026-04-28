# nq-edge-system

A standalone, end-to-end research and backtesting project that converts the
statistical studies in [biagDev/data-collection](https://github.com/biagDev/data-collection)
into a backtestable intraday trading system for **NQ (Nasdaq-100 futures)**.

This repository is **read/write**. The source repository is **read-only** and
is cloned to `../_source` outside of this directory; copies of the data we
actually use live under `data/raw/` with a `PROVENANCE.md` recording the
source path and commit SHA.

## Headline result

**The system as specified is not live-deployable.** Across 21 years of NQ=F
daily bars (2005–2026), the spec'd two-strategy stack (NR7 + Top-Q) produces:

- 1,299 trades, win rate 42.7%, **expectancy −0.18R, profit factor 0.58**
- CAGR −8.2%, max drawdown −84%
- 0 of 36 sensitivity-sweep parameter combinations clear PF ≥ 1.1
- IS/OOS expectancy drift −0.002R (the negative result is *robust*, not a
  regime artifact)
- Marginally outperforms random-entry benchmark; underperforms buy-and-hold

**The diagnostic underneath is the real deliverable**: the NR7 signal *is*
real (+0.017R per trade with no fixed target, exit at close) but too small
to overcome friction at the daily timeframe. The strongest *framework-fit*
edge in the source repo — **D4 (9:30 candle color predicts retest side, +50pp
lift, n≈115/color)** — lives at 15m granularity and was not backtestable
because the source repo doesn't persist 15m bars. That's the highest-priority
next research step.

Full report: [`analysis/00_final_report.md`](analysis/00_final_report.md).

## Source pin

- Source repo: https://github.com/biagDev/data-collection
- Source commit (HEAD at clone): `92e5f9c29b53f49b400f07aadef6d13a3107dc69`
- Source state recorded verbatim in [`data/raw/SOURCE_AUDIT.md`](data/raw/SOURCE_AUDIT.md)

## Repo structure

```
analysis/
  00_final_report.md             Phase 7: executive doc
  01_inventory.md                Phase 1: catalog of every source study
  02_edge_ranking.md             Phase 2: Wilson CI + BH FDR ranking of 17 edges
  03_research_synthesis.md       Phase 3: professional frameworks, citations
  04_edge_to_framework_mapping.md Phase 4: each edge -> its framework + trigger
  05_strategy_spec.md            Phase 5: unambiguous trading rules
  06_backtest_results.md         Phase 6: 21-year backtest + sensitivity
data/raw/
  PROVENANCE.md                  what was copied from where
  SOURCE_AUDIT.md                verbatim source-repo audit
  analyses/                      every results.json, .csv, .pine from source
  bars/nq_daily.csv              NQ=F daily from yfinance, 2005-2026
data/processed/
  edge_ranking.json              machine-readable Phase 2 output
notebooks/                       (empty — analysis is in src/)
references/A..O_*.md             15 per-topic web-research notes (Phase 3)
results/
  equity_curve.png
  r_distribution.png
  monthly_returns.png
  trades_full.csv
  metrics.json
  equity_curve_full.csv
src/stats/                       Wilson CI, BH, tradeability score
src/strategy/                    spec mirrored in code
src/backtest/                    engine, metrics, run-all driver
```

## Reproducing

```sh
# 1. Source repo (read-only) — clone outside this folder
cd ..
git clone https://github.com/biagDev/data-collection ./_source
cd nq-edge-system

# 2. Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Re-fetch NQ daily bars (saves to data/raw/bars/nq_daily.csv)
python -c "import yfinance as yf; \
  df=yf.download('NQ=F', start='2005-01-01', end='2026-04-26', progress=False, auto_adjust=False); \
  df.columns=[c[0].lower() for c in df.columns]; \
  df=df[['open','high','low','close','volume']].dropna(); \
  df.index.name='date'; \
  df.to_csv('data/raw/bars/nq_daily.csv')"

# 4. Phase 2 — re-rank edges
python -m src.stats.run_ranking
# emits: analysis/02_edge_ranking.md, data/processed/edge_ranking.json

# 5. Phase 6 — re-run backtest
python -m src.backtest.run
# emits: analysis/06_backtest_results.md, results/*.png, results/*.csv, results/metrics.json
```

Phases 1, 3, 4, 5, 7 are markdown deliverables in `analysis/` and `references/` —
no commands needed.

## Operating principles (from the original brief, preserved)

- The source repo is **read-only**; all new artifacts live here.
- Be skeptical of the source's own conclusions. We applied Wilson CI + BH FDR
  to all 17 candidate edges; 15 survived BH at q=0.10, but **operationalizing
  them into a stop-and-target trade does not preserve the edge** at the daily
  timeframe.
- Prefer fewer strong edges over many weak ones.
- Cite sources for any web-derived claim ([`references/`](references/)).
- Commit per phase. Git history reads like a research log:

```
$ git log --oneline
... Phase 7: final report and README polish
... Phase 6: backtest engine + sensitivity + benchmarks (honest negative result)
... Phase 5: strategy spec + code
... Phase 4: edge-to-framework mapping with stacking model
... Phase 3: web research synthesis on day-trading frameworks
... Phase 2: edge ranking with Wilson CI + BH correction
... Phase 1: source inventory + raw data copy with provenance
... Initial scaffold: dirs, README, requirements, .gitignore
```

## What's next

See the "Recommended next research" section of
[`analysis/00_final_report.md`](analysis/00_final_report.md). The single
highest-leverage step is **acquiring 15-minute NQ bar data** (Databento,
Polygon, Firstrate, or IQFeed) and implementing the carry-forward
**B1+D4 intraday IB-retest fade** strategy whose spec already lives in
[`analysis/05_strategy_spec.md`](analysis/05_strategy_spec.md) and whose code
stub is at [`src/strategy/intraday_b1_d4.py`](src/strategy/intraday_b1_d4.py).
