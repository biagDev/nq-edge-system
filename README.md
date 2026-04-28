# nq-edge-system

A standalone, end-to-end research and backtesting project that converts the statistical studies in
[biagDev/data-collection](https://github.com/biagDev/data-collection) into a backtestable intraday
trading system for **NQ (Nasdaq-100 futures)**.

This repository is **read/write**. The source repository is **read-only** and is cloned to
`../_source` outside of this directory; copies of the data we actually use live under
`data/raw/` with a `PROVENANCE.md` recording the source path and commit SHA.

## Source pin

- Source repo: https://github.com/biagDev/data-collection
- Source commit (HEAD at clone): `92e5f9c29b53f49b400f07aadef6d13a3107dc69`

## Structure

```
analysis/        Phase reports (markdown). 00 final, 01..06 phase outputs.
data/raw/        Copies of source datasets actually used (with PROVENANCE.md).
data/processed/  Cleaned datasets generated here.
notebooks/       Numbered exploratory notebooks.
src/stats/       Edge-ranking utilities (Wilson CI, lift, multiple-testing correction).
src/strategy/    Signal / entry / exit / sizing logic — mirrors the strategy spec.
src/backtest/    Engine, metrics, plots.
results/         Backtest tables, equity curves.
references/      Web-research notes and citations.
```

## Reproducing

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python -m src.backtest.run` (regenerates `results/` once Phase 6 lands)

Headline results, the strategy spec, and the pre-live checklist live in
[`analysis/00_final_report.md`](analysis/00_final_report.md) once Phase 7 completes.
