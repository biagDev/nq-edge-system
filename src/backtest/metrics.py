"""Backtest metrics: R, expectancy, profit factor, Sharpe, Sortino,
max drawdown, MAR, monthly distribution."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass
class Metrics:
    n_trades: int
    win_rate: float
    avg_win_R: float
    avg_loss_R: float
    expectancy_R: float
    profit_factor: float
    avg_win_dollars: float
    avg_loss_dollars: float
    total_pnl_dollars: float
    cagr: float
    sharpe: float
    sortino: float
    max_drawdown_pct: float
    max_drawdown_dollars: float
    longest_loss_streak: int
    mar_ratio: float


def compute(trades: list, equity_curve: pd.Series, start_equity: float) -> Metrics:
    n = len(trades)
    if n == 0:
        return Metrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    rs = np.array([t.R for t in trades])
    pnls = np.array([t.pnl_dollars for t in trades])
    wins = rs[rs > 0]
    losses = rs[rs <= 0]

    win_rate = len(wins) / n
    avg_win_R = float(wins.mean()) if len(wins) else 0.0
    avg_loss_R = float(losses.mean()) if len(losses) else 0.0
    expectancy_R = float(rs.mean())

    gross_win = pnls[pnls > 0].sum()
    gross_loss = -pnls[pnls < 0].sum()
    profit_factor = float(gross_win / gross_loss) if gross_loss > 0 else float("inf")

    avg_win_dollars = float(pnls[pnls > 0].mean()) if (pnls > 0).any() else 0.0
    avg_loss_dollars = float(pnls[pnls < 0].mean()) if (pnls < 0).any() else 0.0

    total_pnl = float(pnls.sum())
    end_equity = start_equity + total_pnl

    # CAGR from equity curve dates
    if len(equity_curve) >= 2:
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        years = max(0.001, days / 365.25)
        cagr = (end_equity / start_equity) ** (1 / years) - 1
    else:
        cagr = 0.0

    # Sharpe / Sortino on daily equity-curve returns
    rets = equity_curve.pct_change().dropna()
    if len(rets) > 1 and rets.std() > 0:
        sharpe = float(rets.mean() / rets.std() * np.sqrt(252))
        downside = rets[rets < 0]
        sortino = float(rets.mean() / downside.std() * np.sqrt(252)) if len(downside) > 1 and downside.std() > 0 else 0.0
    else:
        sharpe = 0.0
        sortino = 0.0

    # Max drawdown
    eq = equity_curve.values
    peaks = np.maximum.accumulate(eq)
    dd = (eq - peaks) / peaks
    max_dd_pct = float(dd.min())
    max_dd_dollars = float((eq - peaks).min())

    # Longest losing streak
    streak = 0
    longest = 0
    for r in rs:
        if r <= 0:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 0

    mar = abs(cagr / max_dd_pct) if max_dd_pct < 0 else float("inf")

    return Metrics(
        n_trades=n,
        win_rate=round(win_rate, 4),
        avg_win_R=round(avg_win_R, 3),
        avg_loss_R=round(avg_loss_R, 3),
        expectancy_R=round(expectancy_R, 3),
        profit_factor=round(profit_factor, 3),
        avg_win_dollars=round(avg_win_dollars, 2),
        avg_loss_dollars=round(avg_loss_dollars, 2),
        total_pnl_dollars=round(total_pnl, 2),
        cagr=round(cagr, 4),
        sharpe=round(sharpe, 3),
        sortino=round(sortino, 3),
        max_drawdown_pct=round(max_dd_pct, 4),
        max_drawdown_dollars=round(max_dd_dollars, 2),
        longest_loss_streak=int(longest),
        mar_ratio=round(mar, 3),
    )


def monthly_returns(equity_curve: pd.Series) -> pd.Series:
    return equity_curve.resample("M").last().pct_change().dropna()


def buy_and_hold_metrics(bars: pd.DataFrame, start_equity: float) -> dict:
    """Buy-and-hold benchmark: 1 NQ contract bought at first close, held."""
    from ..strategy.params import DOLLAR_PER_POINT
    pts = bars["close"].iloc[-1] - bars["close"].iloc[0]
    pnl = pts * DOLLAR_PER_POINT
    end = start_equity + pnl
    days = (bars.index[-1] - bars.index[0]).days
    years = max(0.001, days / 365.25)
    cagr = (end / start_equity) ** (1 / years) - 1
    rets = bars["close"].pct_change().dropna()
    sharpe = float(rets.mean() / rets.std() * np.sqrt(252)) if rets.std() > 0 else 0.0
    eq = start_equity + (bars["close"] - bars["close"].iloc[0]) * DOLLAR_PER_POINT
    peaks = eq.cummax()
    dd = ((eq - peaks) / peaks).min()
    return {
        "cagr": round(cagr, 4),
        "sharpe": round(sharpe, 3),
        "max_drawdown_pct": round(float(dd), 4),
        "total_pnl_dollars": round(pnl, 2),
        "end_equity": round(end, 2),
    }
