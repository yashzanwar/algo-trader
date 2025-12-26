#!/usr/bin/env python3
"""Test REAL Angel One data downloaded to CSV."""

import sys
sys.path.insert(0, 'src')

from algotrader.data.source import CsvDataSource
from algotrader.strategy import MovingAverageCrossStrategy

print("\n" + "=" * 80)
print("📊 TESTING REAL ANGEL ONE DATA")
print("=" * 80)

# Test with REAL Reliance data
ds = CsvDataSource('examples/data/reliance_ns.csv', datetime_column='date')
df = ds.load()

print(f'\n✅ Loaded {len(df)} days of REAL Reliance data from Angel One')
print(f'📊 Latest close: ₹{df.iloc[-1]["close"]:.2f}')
print(f'📅 Date range: {df.index[0].date()} to {df.index[-1].date()}')

# Run strategy
print(f'\n📈 Running MA Cross strategy (5/20)...')
strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=20)
signals = strategy.generate_signals(df)

# Check latest signal
if len(signals) > 0:
    latest_signal = signals.iloc[-1]  # Series, not scalar
    print(f'\n📊 Current signal status:')
    if latest_signal == 1:
        print('🟢 BUY SIGNAL detected!')
    elif latest_signal == -1:
        print('🔴 SELL SIGNAL detected!')
    else:
        print('⚪ No active signal (HOLD)')
        
print("\n" + "=" * 80)
print("✅ REAL DATA INTEGRATION WORKING!")
print("=" * 80)
print("\n💡 You can now:")
print("   1. Run backtests with REAL data")
print("   2. Monitor stocks using downloaded CSV files")
print("   3. Get fresh data anytime with: python examples/download_angel_data.py")
print("=" * 80 + "\n")
