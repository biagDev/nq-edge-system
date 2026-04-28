"""Top-Quartile Extension Breakout — secondary strategy.

Spec: analysis/05_strategy_spec.md (Strategy 2).

Setup at close of day t: close in top quartile of today's range -> long bias;
close in bottom quartile -> short bias. Trigger on day t+1: higher high (long)
or lower low (short). Stop at prior_H - 0.5 * prior_range (long); target at
prior_H + 0.5 * prior_range.
"""

from __future__ import annotations

import pandas as pd

from .params import TICK_SIZE, TOPQ_STOP_FRAC, TOPQ_TARGET_FRAC, TOPQ_THRESHOLD
from .signal import Signal


def topq_class(bar: pd.Series) -> str | None:
    """Return 'long', 'short', or None for the day's quartile classification."""
    h, l, c = float(bar["high"]), float(bar["low"]), float(bar["close"])
    rng = h - l
    if rng <= 0:
        return None
    pos = (c - l) / rng                 # 0 at low, 1 at high
    if pos >= TOPQ_THRESHOLD:
        return "long"
    if pos <= (1.0 - TOPQ_THRESHOLD):
        return "short"
    return None


def topq_signal(bars: pd.DataFrame, idx: int) -> list[Signal]:
    bar = bars.iloc[idx]
    side = topq_class(bar)
    if side is None:
        return []
    h, l = float(bar["high"]), float(bar["low"])
    rng = h - l

    if side == "long":
        trigger = h + TICK_SIZE
        stop = h - TOPQ_STOP_FRAC * rng
        target = h + TOPQ_TARGET_FRAC * rng
        risk = trigger - stop
    else:
        trigger = l - TICK_SIZE
        stop = l + TOPQ_STOP_FRAC * rng
        target = l - TOPQ_TARGET_FRAC * rng
        risk = stop - trigger

    setup_date = bars.index[idx].date() if hasattr(bars.index[idx], "date") else bars.index[idx]
    note = f"TopQ side={side} prior_range={rng:.2f}"
    return [Signal(setup_date, "TOPQ", side, trigger, stop, target, risk, note)]
