"""NR7 Expansion Breakout — primary strategy.

Spec: analysis/05_strategy_spec.md (Strategy 1).

Setup at close of day t: today's range is the smallest of the last 7 daily
ranges. Trigger on day t+1: break of prior_high (long) or prior_low (short).
Stop at the OPPOSITE extreme of the NR7 day. Target = 1.68 x NR7 range past
the trigger.
"""

from __future__ import annotations

import pandas as pd

from .params import NR7_LOOKBACK, NR7_TARGET_MULTIPLE, TICK_SIZE
from .signal import Signal


def is_nr7_day(bars: pd.DataFrame, idx: int) -> bool:
    """True iff bar at integer position `idx` is an NR7 day.

    `bars` must be a DataFrame indexed by date with at least columns
    high, low. The check looks back `NR7_LOOKBACK` rows including current.
    """
    if idx < NR7_LOOKBACK - 1:
        return False
    window = bars.iloc[idx - NR7_LOOKBACK + 1: idx + 1]
    rng = window["high"] - window["low"]
    today_range = bars.iloc[idx]["high"] - bars.iloc[idx]["low"]
    if today_range <= 0:
        return False
    return today_range == rng.min()


def nr7_signal(bars: pd.DataFrame, idx: int, ma200: float | None = None) -> list[Signal]:
    """Return Signal objects for the next bar's potential trades.

    For NR7 we emit BOTH a long and a short Signal (whichever triggers first
    on day t+1 is the actual trade — engine resolves). When both extremes are
    breached on t+1, the engine picks the side aligned with the 200MA bias.
    """
    if not is_nr7_day(bars, idx):
        return []
    bar = bars.iloc[idx]
    h, l = float(bar["high"]), float(bar["low"])
    rng = h - l

    long_trigger = h + TICK_SIZE
    long_stop = l                       # opposite extreme of NR7 day
    long_target = long_trigger + NR7_TARGET_MULTIPLE * rng
    long_risk = long_trigger - long_stop

    short_trigger = l - TICK_SIZE
    short_stop = h
    short_target = short_trigger - NR7_TARGET_MULTIPLE * rng
    short_risk = short_stop - short_trigger

    setup_date = bars.index[idx].date() if hasattr(bars.index[idx], "date") else bars.index[idx]
    note = f"NR7 range={rng:.2f} ma200={'na' if ma200 is None else f'{ma200:.2f}'}"
    return [
        Signal(setup_date, "NR7", "long",  long_trigger,  long_stop,  long_target,  long_risk,  note),
        Signal(setup_date, "NR7", "short", short_trigger, short_stop, short_target, short_risk, note),
    ]
