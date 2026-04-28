# Provenance — `data/raw/`

All files under this directory are **copies** from the read-only source repo
[biagDev/data-collection](https://github.com/biagDev/data-collection).

- **Source commit SHA:** `92e5f9c29b53f49b400f07aadef6d13a3107dc69`
- **Source commit message:** `Add Daily Patterns Vol.2 + 9:30 followthrough analyses`
- **Cloned to:** `/Users/biag/Claude/_source` (outside this repo)
- **Copied on:** 2026-04-27

## What was copied

For every analysis in `_source/analyses/<study>/`:

- `data/results.json` — the canonical aggregate stat
- `data/*.csv` — supporting tables (aggregate, by_dow, body_split, dayclose_table, etc.)
- `pine/*.pine` — the Pine Script source that produced the numbers (used as the spec when we
  re-implement bar-mapping logic in Python)

`data/raw/SOURCE_AUDIT.md` is a verbatim copy of `_source/AUDIT.md`. It documents bugs found and
fixed during the source repo's own audit. Read it before relying on any specific number.

## What was deliberately NOT copied

- `_source/tradingview-mcp/` — vendored MCP server tooling, not analytical content. Not needed.
- `_source/analyses/*/README.md` and `EASY_READ.md` — verbose write-ups already summarized in our
  `analysis/01_inventory.md`. Re-fetch from source if needed.
- `.git`, `.mcp.json`, top-level `README.md` — repo-shape files, not data.

## Mapping (study → path here)

| Source | Local copy |
|---|---|
| `analyses/930-candle-hit-stats/` | `data/raw/analyses/930-candle-hit-stats/` |
| `analyses/945-candle-hit-stats/` | `data/raw/analyses/945-candle-hit-stats/` |
| `analyses/1000-candle-hit-stats/` | `data/raw/analyses/1000-candle-hit-stats/` |
| `analyses/1015-candle-hit-stats/` | `data/raw/analyses/1015-candle-hit-stats/` |
| `analyses/1030-candle-hit-stats/` | `data/raw/analyses/1030-candle-hit-stats/` |
| `analyses/1045-candle-hit-stats/` | `data/raw/analyses/1045-candle-hit-stats/` |
| `analyses/9am-1h-candle-hit-stats/` | `data/raw/analyses/9am-1h-candle-hit-stats/` |
| `analyses/6am-4h-candle-hit-stats/` | `data/raw/analyses/6am-4h-candle-hit-stats/` |
| `analyses/930-followthrough/` | `data/raw/analyses/930-followthrough/` |
| `analyses/extended-stats/01..09` | `data/raw/analyses/extended-stats/01..09` |
| `analyses/daily-patterns-v1/` | `data/raw/analyses/daily-patterns-v1/` |
| `analyses/daily-patterns-v2/` | `data/raw/analyses/daily-patterns-v2/` |
| `AUDIT.md` | `data/raw/SOURCE_AUDIT.md` |

## Important: no raw bars

None of the files under `data/raw/` are OHLCV bars. The source repo computed every stat in Pine
Script over TradingView's `CME_MINI:NQ1!` continuous front-month feed without persisting the
underlying bars. To run a Phase-6 backtest we must independently fetch NQ data from a vendor
(TradingView export, Polygon, Databento, Stooq for daily, etc.). When we do, those bars will
land under `data/raw/bars/` with this provenance file updated.
