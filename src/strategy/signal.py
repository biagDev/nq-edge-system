"""Common signal dataclass shared by all strategies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Signal:
    """A pre-trade decision evaluated at end-of-day t. Trade fires next bar."""
    setup_date: date
    strategy: str            # "NR7" | "TOPQ" | ...
    direction: str           # "long" | "short"
    trigger_price: float     # stop-buy/sell level
    stop_price: float        # invalidation level
    target_price: float      # primary profit target
    risk_pts: float          # trigger -> stop, in NQ points
    notes: str = ""

    @property
    def reward_pts(self) -> float:
        return abs(self.target_price - self.trigger_price)

    @property
    def rr(self) -> float:
        return self.reward_pts / self.risk_pts if self.risk_pts > 0 else 0.0
