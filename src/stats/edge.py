"""Edge-ranking utilities: Wilson CI, lift over base rate, two-proportion z-test,
Benjamini-Hochberg correction, expected-R after costs, tradeability score.

All inputs are integer counts (k successes, n trials). No floats-as-rates.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from typing import Iterable

from scipy.stats import norm
from statsmodels.stats.multitest import multipletests


# --- core stats ---------------------------------------------------------------

def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval. Returns (lo, hi) as proportions in [0, 1]."""
    if n == 0:
        return (float("nan"), float("nan"))
    z = norm.ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def two_proportion_z(k1: int, n1: int, k0: int, n0: int) -> tuple[float, float]:
    """Two-proportion z-test, two-sided. Returns (z, p_value).

    H0: p1 == p0 (the conditional rate equals the base rate computed on the
    complementary set or unconditional). H1: p1 != p0.
    """
    if n1 == 0 or n0 == 0:
        return (float("nan"), float("nan"))
    p1, p0 = k1 / n1, k0 / n0
    p_pool = (k1 + k0) / (n1 + n0)
    se = sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n0))
    if se == 0:
        return (0.0, 1.0)
    z = (p1 - p0) / se
    p_two = 2 * (1 - norm.cdf(abs(z)))
    return (z, p_two)


def benjamini_hochberg(p_values: Iterable[float], q: float = 0.10):
    """BH FDR correction. Returns (rejected_bool_list, p_adjusted_list)."""
    pvals = list(p_values)
    rej, p_adj, _, _ = multipletests(pvals, alpha=q, method="fdr_bh")
    return list(rej), list(p_adj)


# --- domain helpers -----------------------------------------------------------

# NQ point value, costs assumed for ranking purposes only. The backtest uses
# its own (higher-fidelity) cost model.
NQ_DOLLAR_PER_POINT = 20.0     # MNQ would be 2.0; full NQ is $20/pt
NQ_TICK = 0.25                 # one tick = 0.25 pts
COMMISSION_RT_USD = 4.0        # round-trip per contract, conservative
SLIPPAGE_TICKS_PER_SIDE = 1.0  # one tick of slippage on entry and on exit


def round_trip_cost_points() -> float:
    """Total cost in NQ points for one round-trip trade, expressed as points
    on a 1-contract basis. Slippage + commission converted via $/pt."""
    slip_pts = 2 * SLIPPAGE_TICKS_PER_SIDE * NQ_TICK
    comm_pts = COMMISSION_RT_USD / NQ_DOLLAR_PER_POINT
    return slip_pts + comm_pts


def expected_r_after_costs(
    hit_rate: float,
    avg_win_pts: float,
    avg_loss_pts: float,
    risk_pts: float,
) -> float:
    """Expectancy in R-multiples after subtracting friction.

    risk_pts is the pre-trade defined risk (the denominator of an R-multiple).
    avg_win/avg_loss are the *raw* point P&L of winners/losers (avg_loss is a
    positive number representing the size of losses).
    """
    cost = round_trip_cost_points()
    win_R = (avg_win_pts - cost) / risk_pts
    loss_R = (avg_loss_pts + cost) / risk_pts
    return hit_rate * win_R - (1 - hit_rate) * loss_R


# --- ranking record -----------------------------------------------------------

@dataclass
class Edge:
    name: str
    family: str           # "intraday-15m" | "daily" | "session-structure"
    k: int                # successes
    n: int                # trials
    base_k: int           # complementary or unconditional successes
    base_n: int           # complementary or unconditional trials
    direction: str        # "predicts_high_retest" / "predicts_expansion" / etc.
    regime_stable: bool | None  # True if confirmed across regimes; None if untested
    notes: str = ""

    @property
    def rate(self) -> float:
        return self.k / self.n if self.n else float("nan")

    @property
    def base_rate(self) -> float:
        return self.base_k / self.base_n if self.base_n else float("nan")

    @property
    def lift(self) -> float:
        """Absolute lift over base rate (percentage points)."""
        return self.rate - self.base_rate

    def wilson(self, alpha: float = 0.05) -> tuple[float, float]:
        return wilson_ci(self.k, self.n, alpha)

    def z_p(self) -> tuple[float, float]:
        return two_proportion_z(self.k, self.n, self.base_k, self.base_n)


def tradeability_score(e: Edge, p_adj: float, n_min: int = 100) -> int:
    """1-5 ranking. Combines size, significance, lift, regime stability.

    5 = strong, large-n, BH-significant, regime-stable, lift >= 10pp
    1 = anecdotal or fails BH
    """
    score = 3
    if e.n < 30:
        return 1
    if e.n < n_min:
        score -= 1
    if p_adj < 0.01:
        score += 1
    elif p_adj > 0.10:
        score -= 1
    lift_pp = abs(e.lift) * 100
    if lift_pp >= 20:
        score += 1
    elif lift_pp < 5:
        score -= 1
    if e.regime_stable is True:
        score += 1
    elif e.regime_stable is False:
        score -= 1
    return max(1, min(5, score))


def edge_to_dict(e: Edge, p_adj: float) -> dict:
    lo, hi = e.wilson()
    z, p = e.z_p()
    d = asdict(e)
    d.update({
        "rate": round(e.rate, 4),
        "base_rate": round(e.base_rate, 4),
        "lift_pp": round(e.lift * 100, 2),
        "wilson_lo": round(lo, 4),
        "wilson_hi": round(hi, 4),
        "z": round(z, 3) if z == z else None,
        "p_value": round(p, 5) if p == p else None,
        "p_adj_bh": round(p_adj, 5),
        "tradeability_1to5": tradeability_score(e, p_adj),
    })
    return d
