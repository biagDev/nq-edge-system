"""Stub for the carry-forward intraday B1 + D4 strategy.

Activation requires 15-minute NQ RTH bars, which the source repo does not
provide and which we do not fetch in v1. This file exists so the spec is
mirrored in code and so a future implementation has a clear entry point.

Spec: analysis/05_strategy_spec.md, "B1 + D4 — Intraday IB-retest fade".
"""

from __future__ import annotations


class NotImplementedYet(Exception):
    """Raised by intraday strategy until 15m bars are wired in."""


def b1_d4_signal(*_args, **_kwargs):
    raise NotImplementedYet(
        "B1+D4 intraday strategy requires 15m bar data. See "
        "analysis/05_strategy_spec.md 'Carry-forward' section."
    )
