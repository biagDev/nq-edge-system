"""Position sizing. 0.5% per-trade risk, optional vol-target overlay."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .params import (
    DOLLAR_PER_POINT,
    RISK_PER_TRADE_FRAC,
    VOL_TARGET_ANNUAL,
)


def position_size(equity: float, stop_distance_pts: float) -> int:
    """Contracts to trade. Floors at 0; min 1 if budget allows."""
    if stop_distance_pts <= 0 or equity <= 0:
        return 0
    risk_dollars = equity * RISK_PER_TRADE_FRAC
    contracts = math.floor(risk_dollars / (stop_distance_pts * DOLLAR_PER_POINT))
    return max(0, contracts)


def vol_target_scalar(equity_curve: pd.Series, lookback: int = 30) -> float:
    """Scalar (0.25..1.5) to apply to nominal size, given recent equity vol."""
    if len(equity_curve) < lookback + 1:
        return 1.0
    rets = equity_curve.pct_change().dropna().tail(lookback)
    realized = rets.std() * np.sqrt(252)
    if realized <= 0:
        return 1.0
    scalar = VOL_TARGET_ANNUAL / realized
    return float(min(1.5, max(0.25, scalar)))
