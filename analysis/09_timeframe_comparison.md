# Phase 9 — Timeframe Comparison

The 15m strategy was the natural starting point because the source repo's
strongest edges (D4, C1, D2) were *measured* on 15m bars — the "9:30 candle"
in the source data is literally the 15m bar opening at 9:30 ET. So the
*setup* is a 15m concept by construction.

But the *execution* doesn't have to match the setup's timeframe. So we tested
the same setup logic with finer-grained execution: 5m and 1m.

## Adapted strategy logic

The 9:30 candle's H/L/O/C is now built up across the 3 × 5m bars (or 15 × 1m
bars) that fall within the 9:30-9:45 ET window. Pseudo-code:

```
on bar opening at 9:30 ET:  start tracking H, L, O
on later bars in window:    H = max(H, bar.high), L = min(L, bar.low)
on bar opening at 9:45 ET:  C = previous_bar.close, arm trade
```

Entry / stop / target / cancellation rules are identical to the 15m version,
just measured in the new timeframe's bar units.

## Results

| Timeframe | PF | Win rate | Trades | Avg win | Avg loss | DD | Total P&L | TV history |
|---|---|---|---|---|---|---|---|---|
| **15m** | **2.757** | 67.7% | **93** | +0.11% | −0.09% | 0.69% | +$23,186 | ~11 mo |
| 5m | 2.387 | **86.1%** | 36 | +0.16% | −0.42% | 0.80% | +$14,327 | ~6 mo |
| 1m | n/a* | 100% | 5 | — | — | 0.07% | +$4,025 | ~2 wk |

\*1m has 5 trades, all wins — PF undefined (no losses to divide by).

## What the 5m / 1m runs revealed

**5m has a higher win rate (86%) but worse Profit Factor (2.387) than 15m.**
The asymmetry comes from how losses behave at finer granularity:

- **15m:** Avg loss is small (−0.09%) because when a stop-buy at the 9:30 H
  fires on a 15m bar, that bar typically already contains some upside before
  resolving — many "wins" execute well above the stop, and stop-outs have
  the entire next bar to fill, often filling near the opposite extreme.
- **5m:** Avg loss is **4.7× larger** (−0.42%). Faster bars give the strategy
  no buffer — it triggers on a precise tick break, then if the move fails,
  the stop fills sharply at the 9:30 L without the "averaging-in" benefit
  the 15m bar's wider sampling provides.

Net effect: the higher win rate at 5m doesn't compensate for the larger
losses, and PF is lower despite the surface-attractive 86%. This is a
classic case of "win rate ≠ edge" — the right metric is PF/expectancy, not
hit rate.

**1m is uninformative** because TV's 1m history for NQ is only ~2 weeks. We
got 5 trades, all winners, which means absolutely nothing statistically.

## Verdict

**15m is the production timeframe.** Three reasons:

1. **Highest PF** (2.757 vs 2.387 vs n/a)
2. **Largest sample** (93 trades vs 36 vs 5 — 15m's edge is most reliably
   distinguished from luck)
3. **Most history** in the TV strategy tester (~11 months vs ~6 vs ~2 weeks)

The intuition that "lower timeframes give finer fills which should improve
PF" turns out to be wrong here — the 9:30 setup *needs* the 15m bar's
implicit averaging to keep losses small. Going finer than the setup's
natural granularity actively hurts.

## What this doesn't rule out

Two follow-ups that could still be worth doing with paid 5m/1m data:

1. **Same comparison with deeper history** (Polygon / Databento) — to verify
   that the 5m disadvantage isn't purely a small-sample artifact. With 2-3
   years of 5m data, n could reach 200+ trades and the comparison would be
   more conclusive.
2. **Hybrid timeframe**: setup on 15m, *exit* logic on 5m or 1m — i.e. the
   stop-buy is placed at the 15m H, but the exit (especially the stop) uses
   finer-grained data to avoid the 15m's all-or-nothing fill. This would
   require Pine's `request.security_lower_tf` or chart-of-chart tricks; not
   tested here.

For now: **stay on 15m.**
