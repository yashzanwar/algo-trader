from __future__ import annotations

import pandas as pd


class MeanReversionStrategy:
    """Z-score mean-reversion strategy on closing prices.
    
    Generates signals when price deviates from its rolling mean:
    - Short (-1) when z-score exceeds +entry_z threshold (price too high)
    - Long (+1) when z-score falls below -entry_z threshold (price too low)
    - Neutral (0) otherwise
    
    Args:
        lookback: Rolling window size for mean and std calculation
        entry_z: Z-score threshold for entry signals (absolute value)
    """

    name = "mean_reversion"

    def __init__(self, lookback: int = 20, entry_z: float = 1.0):
        self.lookback = lookback
        self.entry_z = entry_z

    def required_columns(self) -> set[str]:
        return {"close"}

    def warmup_bars(self) -> int:
        return self.lookback

    def generate_signals(self, prices: pd.DataFrame) -> pd.Series:
        close = prices["close"]
        rolling_mean = close.rolling(self.lookback).mean()
        rolling_std = close.rolling(self.lookback).std(ddof=0)
        zscore = (close - rolling_mean) / rolling_std
        signals = zscore.apply(self._signal_from_z)
        return signals.fillna(0).rename("signal")

    def _signal_from_z(self, z: float) -> int:
        if z > self.entry_z:
            return -1
        if z < -self.entry_z:
            return 1
        return 0
