#!/usr/bin/env python3
"""Debug MA strategy to understand signal generation."""

import pandas as pd
import numpy as np
from pathlib import Path

from algotrader.data import CsvDataSource
from algotrader.strategy import MovingAverageCrossStrategy

# Load sample data
csv_path = Path("examples/data/reliance_ns.csv")
if not csv_path.exists():
    print(f"Error: {csv_path} not found. Run scan_stocks_csv.py first.")
    exit(1)

data_source = CsvDataSource(path=csv_path)
prices = data_source.load()

# Generate signals
strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=20)
signals = strategy.generate_signals(prices)

# Show first 50 signals
print("Date            Close      Fast MA    Slow MA    Signal")
print("=" * 70)

close = prices["close"]
fast_ma = close.rolling(5).mean()
slow_ma = close.rolling(20).mean()

for i in range(20, min(70, len(prices))):
    date = prices.index[i]
    print(f"{str(date)[:10]}  {close.iloc[i]:8.2f}  {fast_ma.iloc[i]:8.2f}  {slow_ma.iloc[i]:8.2f}  {signals.iloc[i]:6.0f}")

# Count signals
print(f"\n\nSignal Distribution:")
print(f"Long signals (+1):  {(signals == 1).sum()}")
print(f"Short signals (-1): {(signals == -1).sum()}")
print(f"Neutral (0):        {(signals == 0).sum()}")
print(f"Total bars:         {len(signals)}")
