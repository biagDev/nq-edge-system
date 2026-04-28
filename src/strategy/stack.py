"""Stacking rule: when primary (NR7) and secondary (TOPQ) both fire,
trade only the primary if directions agree; skip both if they disagree.

NR7 emits a long+short pair (engine resolves which fires); TOPQ pre-commits
to one direction. Stack handles cross-strategy conflicts only.
"""

from __future__ import annotations

from .signal import Signal


def combine(nr7_signals: list[Signal], topq_signals: list[Signal]) -> list[Signal]:
    """Return the final list of Signals to monitor next bar.

    Decision rules:
      - If TOPQ fires AND NR7 fires:
          * If TOPQ direction matches one side of the NR7 long/short pair -> trade NR7 only
            (the matching-direction NR7 signal). The other NR7 side is dropped to avoid
            triggering the wrong way.
          * If TOPQ direction conflicts with the NR7 bias as established by 200MA
            we cannot test here (no MA in scope) — keep both NR7 signals; engine resolves.
            But if topq has a direction and the OPPOSITE-direction NR7 signal would
            also fire, we keep only the directionally-agreeing NR7 signal as the "won"
            convergence.
          * If TOPQ direction matches NEITHER side of NR7 (impossible since NR7 emits
            both), this branch is unreachable; pass through.
      - If only NR7 fires: pass through (engine handles long/short ambiguity).
      - If only TOPQ fires: pass through.
      - If neither fires: empty list.
    """
    if not nr7_signals and not topq_signals:
        return []
    if nr7_signals and not topq_signals:
        return list(nr7_signals)
    if topq_signals and not nr7_signals:
        return list(topq_signals)

    # Both fire. TOPQ is single-direction; NR7 has both.
    topq = topq_signals[0]
    matching = [s for s in nr7_signals if s.direction == topq.direction]
    if matching:
        # Convergence: keep only the matching-direction NR7 signal (primary takes
        # precedence over secondary for sizing). TOPQ is "logged but not traded"
        # per spec — the backtest engine writes a "secondary fired but suppressed"
        # row to the trade log via the notes field.
        m = matching[0]
        m.notes = f"{m.notes} | TOPQ-CONFIRM"
        return [m]
    # Directions opposite -> per spec, both skipped.
    return []
