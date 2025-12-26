#!/usr/bin/env python3
"""Example: Backtest on Reliance using CSV data."""

from pathlib import Path

from algotrader.core import setup_logging
from algotrader.data import CsvDataSource
from algotrader.engine.backtester import Backtester
from algotrader.strategy import MovingAverageCrossStrategy, MeanReversionStrategy

# Setup logging
setup_logging(level="INFO")

# Create sample Reliance data file if it doesn't exist
csv_path = Path("examples/data/reliance_sample.csv")
if not csv_path.exists():
    print("Creating sample Reliance data...")
    import pandas as pd
    import numpy as np
    
    # Create sample data (you should replace this with real data)
    dates = pd.date_range("2023-01-01", periods=250, freq="B")  # Business days
    close_prices = 2400 + (pd.Series(range(250)) * 0.5) + (np.random.randn(250) * 20)
    
    df = pd.DataFrame({
        "date": dates,
        "open": close_prices - np.random.randn(250) * 5,
        "high": close_prices + np.random.uniform(5, 15, 250),
        "low": close_prices - np.random.uniform(5, 15, 250),
        "close": close_prices,
        "volume": np.random.randint(1000000, 5000000, 250),
    })
    
    csv_path.parent.mkdir(exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"Created sample data at {csv_path}")

# Load data
print("\nLoading Reliance data from CSV...")
data_source = CsvDataSource(path=csv_path)
prices = data_source.load()

print(f"Loaded {len(prices)} days of data")
print(f"Date range: {prices.index[0].date()} to {prices.index[-1].date()}")
print(f"\nPrice summary:")
print(prices[["open", "high", "low", "close", "volume"]].describe())

# Test both strategies
strategies = [
    ("Moving Average Crossover", MovingAverageCrossStrategy(fast_window=5, slow_window=20)),
    ("Mean Reversion", MeanReversionStrategy(lookback=20, entry_z=1.0)),
]

for name, strategy in strategies:
    print("\n" + "=" * 70)
    print(f"BACKTEST: {name}")
    print("=" * 70)
    
    backtester = Backtester(strategy)
    result = backtester.run(prices)
    
    print(f"Sharpe Ratio:      {result.metrics['sharpe_ratio']:>10.2f}")
    print(f"Sortino Ratio:     {result.metrics['sortino_ratio']:>10.2f}")
    print(f"Total Return:      {result.metrics['total_return']:>10.2%}")
    print(f"Annual Return:     {result.metrics['annual_return']:>10.2%}")
    print(f"Max Drawdown:      {result.metrics['max_drawdown']:>10.2%}")
    print(f"Win Rate:          {result.metrics['win_rate']:>10.2%}")
    print(f"Profit Factor:     {result.metrics['profit_factor']:>10.2f}")
    print(f"Number of Trades:  {result.trades:>10}")

print("\n" + "=" * 70)
print("\n📝 NOTE: This uses sample data. For real backtesting:")
print("1. Download real Reliance data from your broker or data provider")
print("2. Save as CSV with columns: date,open,high,low,close,volume")
print("3. Place in examples/data/reliance.csv")
print("4. Update csv_path in this script")
