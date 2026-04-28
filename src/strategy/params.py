"""Single-point-of-edit for strategy parameters. Mirrors analysis/05_strategy_spec.md."""

NR7_LOOKBACK = 7
NR7_TARGET_MULTIPLE = 1.68      # mean expansion ratio (E1c stat)

TOPQ_THRESHOLD = 0.75            # close >= H - (1-thr)*range
TOPQ_TARGET_FRAC = 0.5           # of prior-day range, past the trigger
TOPQ_STOP_FRAC = 0.5             # of prior-day range, below the trigger

RISK_PER_TRADE_FRAC = 0.005      # 0.5% of equity per trade
AGGREGATE_RISK_CAP_FRAC = 0.015  # 1.5% concurrent risk cap (informational)
VOL_TARGET_ANNUAL = 0.15

TICK_SIZE = 0.25                 # NQ tick (same for NQ and MNQ)
DOLLAR_PER_POINT = 2.0           # MNQ (= 1/10 of full NQ). $100k account sizes here.
COMMISSION_RT = 1.5              # USD per MNQ contract round-trip (typical retail)
SLIPPAGE_TICKS = 1.0             # ticks per side

START_EQUITY = 100_000.0

MIN_NEXT_BAR_RANGE_PTS = 25.0    # holiday/half-day filter
