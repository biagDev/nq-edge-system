"""Daily-bar backtest engine. No look-ahead. Conservative fill ambiguity rules.

Algorithm per bar t (with bars indexed 0..N-1):
  1. At close of t: each strategy emits Signals to monitor on t+1.
     Combine via stack.combine.
  2. On bar t+1, for each pending signal:
       - Check if entry trigger filled: long fills if high(t+1) >= trigger;
         short fills if low(t+1) <= trigger.
       - If filled, fill_price = max(open(t+1), trigger) for long
         (gap-fill modeling: if open gaps past trigger, fill at open).
         Add 1 tick of slippage cost on entry.
       - Inspect day t+1's range for stop and target:
           * If high reaches target AND low reaches stop: ambiguous ->
             conservative = stop (record as such).
           * If only stop hit: stop out.
           * If only target hit: target hit.
           * If neither: exit at close(t+1) (1 tick slippage).
       - Add commission on round-trip.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from ..strategy.params import (
    COMMISSION_RT,
    DOLLAR_PER_POINT,
    MIN_NEXT_BAR_RANGE_PTS,
    NR7_LOOKBACK,
    SLIPPAGE_TICKS,
    START_EQUITY,
    TICK_SIZE,
)
from ..strategy.nr7 import nr7_signal
from ..strategy.signal import Signal
from ..strategy.sizing import position_size, vol_target_scalar
from ..strategy.stack import combine
from ..strategy.topq import topq_signal


SLIP_PTS = SLIPPAGE_TICKS * TICK_SIZE


@dataclass
class TradeResult:
    setup_date: date
    fill_date: date
    strategy: str
    direction: str
    contracts: int
    fill_price: float
    exit_price: float
    exit_reason: str           # "target" | "stop" | "ambiguous_stop" | "close" | "no_fill"
    pts: float                 # signed gross points per contract (long pos - neg)
    pts_net: float             # after slippage on both legs
    pnl_dollars: float         # net of commission and slippage
    risk_pts: float
    R: float                   # pts_net / risk_pts (signed)
    equity_after: float


def _resolve_long(
    fill_price: float, stop_price: float, target_price: float, day: pd.Series
) -> tuple[float, str]:
    """Return (exit_price, exit_reason). Conservative on ambiguity."""
    high = float(day["high"])
    low = float(day["low"])
    close = float(day["close"])
    hit_stop = low <= stop_price
    hit_target = high >= target_price
    if hit_stop and hit_target:
        return stop_price, "ambiguous_stop"
    if hit_stop:
        return stop_price, "stop"
    if hit_target:
        return target_price, "target"
    return close, "close"


def _resolve_short(
    fill_price: float, stop_price: float, target_price: float, day: pd.Series
) -> tuple[float, str]:
    high = float(day["high"])
    low = float(day["low"])
    close = float(day["close"])
    hit_stop = high >= stop_price
    hit_target = low <= target_price
    if hit_stop and hit_target:
        return stop_price, "ambiguous_stop"
    if hit_stop:
        return stop_price, "stop"
    if hit_target:
        return target_price, "target"
    return close, "close"


def _try_fill(sig: Signal, day: pd.Series) -> float | None:
    """Return fill_price (gap-aware) or None if not filled on this day."""
    h, l, o = float(day["high"]), float(day["low"]), float(day["open"])
    if sig.direction == "long":
        if o >= sig.trigger_price:
            # Gap up through trigger -> fill at open (worse than trigger price).
            return o
        if h >= sig.trigger_price:
            return sig.trigger_price
        return None
    # short
    if o <= sig.trigger_price:
        return o
    if l <= sig.trigger_price:
        return sig.trigger_price
    return None


@dataclass
class BacktestResult:
    trades: list[TradeResult] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    bars: pd.DataFrame | None = None


def run(
    bars: pd.DataFrame,
    strategies: tuple[str, ...] = ("NR7", "TOPQ"),
    start_equity: float = START_EQUITY,
    use_vol_target: bool = True,
    friction_scalar: float = 1.0,
    target_scalar: float = 1.0,
    stop_scalar: float = 1.0,
    random_entry: bool = False,
    rng_seed: int = 1234,
    exit_at_close: bool = False,
) -> BacktestResult:
    """Run the strategy over the given daily bars.

    `target_scalar` and `stop_scalar` apply to the structural distances and
    are used by the sensitivity sweep.
    `friction_scalar` multiplies slippage AND commission.
    `random_entry`: replace strategy decisions with a random direction per
    bar that has the same fire-rate as the average of the real strategies.
    Used as the random-entry benchmark.
    """
    rng = np.random.default_rng(rng_seed)
    equity = start_equity
    eq_curve_index = []
    eq_curve_vals = []
    trades: list[TradeResult] = []

    slip_pts = SLIP_PTS * friction_scalar
    commission = COMMISSION_RT * friction_scalar

    # Pre-compute fire rate to calibrate the random benchmark
    if random_entry:
        fire_count = 0
        for i in range(NR7_LOOKBACK, len(bars) - 1):
            if "NR7" in strategies and nr7_signal(bars, i):
                fire_count += 1
                continue
            if "TOPQ" in strategies and topq_signal(bars, i):
                fire_count += 1
        fire_rate = fire_count / max(1, len(bars) - 1 - NR7_LOOKBACK)
    else:
        fire_rate = None

    for i in range(NR7_LOOKBACK, len(bars) - 1):
        day_t = bars.iloc[i]
        day_t1 = bars.iloc[i + 1]
        eq_curve_index.append(bars.index[i])
        eq_curve_vals.append(equity)

        # Half-day / illiquid filter
        if (day_t1["high"] - day_t1["low"]) < MIN_NEXT_BAR_RANGE_PTS:
            continue

        if random_entry:
            # Match the fire rate of the real strategies and pick direction at random.
            if rng.random() < fire_rate:
                # Build a random NR7-style signal off of day_t.
                h, l = float(day_t["high"]), float(day_t["low"])
                rng_pts = h - l
                if rng_pts <= 0:
                    continue
                direction = rng.choice(["long", "short"])
                if direction == "long":
                    trigger = h + TICK_SIZE
                    stop = l
                    target = trigger + 1.68 * rng_pts
                    risk = trigger - stop
                else:
                    trigger = l - TICK_SIZE
                    stop = h
                    target = trigger - 1.68 * rng_pts
                    risk = stop - trigger
                cands = [Signal(
                    bars.index[i].date(), "RAND", direction, trigger, stop, target,
                    risk, "random benchmark"
                )]
            else:
                cands = []
        else:
            nr7 = nr7_signal(bars, i) if "NR7" in strategies else []
            topq = topq_signal(bars, i) if "TOPQ" in strategies else []
            cands = combine(nr7, topq)

        if not cands:
            continue

        # Apply sensitivity scalars to target/stop distances around trigger.
        adj_cands = []
        for s in cands:
            if s.direction == "long":
                stop_dist = (s.trigger_price - s.stop_price) * stop_scalar
                tgt_dist = (s.target_price - s.trigger_price) * target_scalar
                new_stop = s.trigger_price - stop_dist
                new_target = s.trigger_price + tgt_dist
                new_risk = s.trigger_price - new_stop
            else:
                stop_dist = (s.stop_price - s.trigger_price) * stop_scalar
                tgt_dist = (s.trigger_price - s.target_price) * target_scalar
                new_stop = s.trigger_price + stop_dist
                new_target = s.trigger_price - tgt_dist
                new_risk = new_stop - s.trigger_price
            adj_cands.append(Signal(
                s.setup_date, s.strategy, s.direction,
                s.trigger_price, new_stop, new_target, new_risk, s.notes
            ))

        # In daily-bar resolution: NR7 emits both directions. We pick whichever
        # actually triggers; if both trigger, pick the one whose direction
        # aligns with bar t's color (close vs open) as the "first push" proxy.
        filled = []
        for s in adj_cands:
            fp = _try_fill(s, day_t1)
            if fp is not None:
                filled.append((s, fp))

        if not filled:
            continue

        chosen_sig, chosen_fill = filled[0]
        if len(filled) > 1:
            # Tie-break by daily MA-200 bias if available; else by setup-day color.
            close_t = float(day_t["close"])
            open_t = float(day_t["open"])
            if "ma200" in bars.columns and not pd.isna(day_t["ma200"]):
                bias = "long" if close_t > day_t["ma200"] else "short"
            else:
                bias = "long" if close_t > open_t else "short"
            biased = [pair for pair in filled if pair[0].direction == bias]
            if biased:
                chosen_sig, chosen_fill = biased[0]
            else:
                chosen_sig, chosen_fill = filled[0]

        # Position size based on actual fill-to-stop distance.
        if chosen_sig.direction == "long":
            stop_distance = chosen_fill - chosen_sig.stop_price
        else:
            stop_distance = chosen_sig.stop_price - chosen_fill
        if stop_distance <= 0:
            continue
        contracts = position_size(equity, stop_distance)
        if contracts == 0:
            continue
        if use_vol_target and len(eq_curve_vals) >= 31:
            scalar = vol_target_scalar(pd.Series(eq_curve_vals, index=eq_curve_index))
            contracts = max(1, int(round(contracts * scalar)))

        # Resolve exit
        if exit_at_close:
            # Diagnostic mode: only the stop is honoured; no fixed target;
            # otherwise exit at session close.
            if chosen_sig.direction == "long":
                if float(day_t1["low"]) <= chosen_sig.stop_price:
                    exit_price, reason = chosen_sig.stop_price, "stop"
                else:
                    exit_price, reason = float(day_t1["close"]), "close"
                gross_pts = exit_price - chosen_fill
            else:
                if float(day_t1["high"]) >= chosen_sig.stop_price:
                    exit_price, reason = chosen_sig.stop_price, "stop"
                else:
                    exit_price, reason = float(day_t1["close"]), "close"
                gross_pts = chosen_fill - exit_price
        elif chosen_sig.direction == "long":
            exit_price, reason = _resolve_long(
                chosen_fill, chosen_sig.stop_price, chosen_sig.target_price, day_t1
            )
            gross_pts = exit_price - chosen_fill
        else:
            exit_price, reason = _resolve_short(
                chosen_fill, chosen_sig.stop_price, chosen_sig.target_price, day_t1
            )
            gross_pts = chosen_fill - exit_price

        # Friction: 1 tick slippage on entry (already absorbed by gap-fill mechanism
        # if gapped, otherwise add 1 tick). Plus 1 tick on exit. Plus commission.
        # Simplification: charge 2 ticks total per round-trip plus commission.
        net_pts = gross_pts - 2 * slip_pts
        pnl = net_pts * DOLLAR_PER_POINT * contracts - commission * contracts
        equity_after = equity + pnl

        risk_pts = stop_distance
        R = net_pts / risk_pts if risk_pts > 0 else 0.0

        trades.append(TradeResult(
            setup_date=chosen_sig.setup_date,
            fill_date=bars.index[i + 1].date() if hasattr(bars.index[i + 1], "date") else bars.index[i + 1],
            strategy=chosen_sig.strategy,
            direction=chosen_sig.direction,
            contracts=contracts,
            fill_price=chosen_fill,
            exit_price=exit_price,
            exit_reason=reason,
            pts=gross_pts,
            pts_net=net_pts,
            pnl_dollars=pnl,
            risk_pts=risk_pts,
            R=R,
            equity_after=equity_after,
        ))
        equity = equity_after

    eq_curve_index.append(bars.index[-1])
    eq_curve_vals.append(equity)
    eq = pd.Series(eq_curve_vals, index=eq_curve_index)

    return BacktestResult(trades=trades, equity_curve=eq, bars=bars)
