from __future__ import annotations

import pandas as pd
import numpy as np


class MovingAverageCrossStrategy:
    """Improved two-line moving-average crossover strategy with trend filters.
    
    Generates signals based on fast/slow MA crossovers with proper position holding:
    - Long (+1) when fast MA > slow MA (golden cross) - HOLDS position
    - Short (-1) when fast MA < slow MA (death cross) - HOLDS position
    - Optional filters to reduce whipsaws:
      - Minimum separation threshold between MAs
      - Trend confirmation using longer-term MA
    
    Args:
        fast_window: Fast moving average period (e.g., 5)
        slow_window: Slow moving average period (e.g., 20)
        min_separation_pct: Minimum % separation between MAs to avoid whipsaws (default 0.2%)
        use_trend_filter: Use 200-day MA as trend filter (only long in uptrend)
    """

    name = "moving_average_cross"

    def __init__(
        self, 
        fast_window: int = 5, 
        slow_window: int = 20,
        min_separation_pct: float = 0.2,
        use_trend_filter: bool = True
    ):
        if fast_window <= 0 or slow_window <= 0:
            raise ValueError("Windows must be positive integers")
        if fast_window >= slow_window:
            raise ValueError("fast_window must be strictly less than slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.min_separation_pct = min_separation_pct
        self.use_trend_filter = use_trend_filter
        self.trend_window = 200

    def required_columns(self) -> set[str]:
        return {"close"}

    def warmup_bars(self) -> int:
        if self.use_trend_filter:
            return max(self.slow_window, self.trend_window)
        return self.slow_window

    def generate_signals(self, prices: pd.DataFrame) -> pd.Series:
        close = prices["close"]
        
        # Calculate MAs
        fast_ma = close.rolling(self.fast_window).mean()
        slow_ma = close.rolling(self.slow_window).mean()
        
        # Calculate MA separation percentage
        ma_separation = ((fast_ma - slow_ma) / slow_ma * 100).abs()
        
        # Base signal: +1 when fast > slow, -1 when fast < slow
        raw_signals = pd.Series(0, index=prices.index)
        raw_signals[fast_ma > slow_ma] = 1
        raw_signals[fast_ma < slow_ma] = -1
        
        # Apply minimum separation filter to avoid noise
        if self.min_separation_pct > 0:
            # Only allow signals when MAs are sufficiently separated
            too_close = ma_separation < self.min_separation_pct
            raw_signals[too_close] = 0
        
        # Apply trend filter (only long in uptrends, only short in downtrends)
        if self.use_trend_filter and len(prices) >= self.trend_window:
            trend_ma = close.rolling(self.trend_window).mean()
            in_uptrend = close > trend_ma
            in_downtrend = close < trend_ma
            
            # Only allow long signals in uptrend
            raw_signals[(raw_signals == 1) & ~in_uptrend] = 0
            # Only allow short signals in downtrend  
            raw_signals[(raw_signals == -1) & ~in_downtrend] = 0
        
        return raw_signals.fillna(0).rename("signal")
