#!/usr/bin/env python3
"""Test notifications with REAL trading signals."""

import sys
from datetime import datetime
sys.path.insert(0, 'src')

from algotrader.data.source import CsvDataSource
from algotrader.strategy import MovingAverageCrossStrategy
from algotrader.signals import (
    ConsoleNotifier,
    DesktopNotifier,
    TelegramNotifier,
    MultiNotifier,
    SignalEvent
)

# Telegram config
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "7849078894"

# Stocks to check
WATCHLIST = {
    "RELIANCE": "examples/data/reliance_ns.csv",
    "TCS": "examples/data/tcs_ns.csv",
    "SBIN": "examples/data/sbin_ns.csv",
    "INFY": "examples/data/infy_ns.csv",
    "HDFCBANK": "examples/data/hdfcbank_ns.csv",
}

print("\n" + "=" * 80)
print("📱 TESTING NOTIFICATIONS WITH REAL SIGNALS")
print("=" * 80)

# Setup notifiers
notifier = MultiNotifier([
    ConsoleNotifier(),
    DesktopNotifier(),
    TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
])

# Setup strategy
strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=20)

print("\n🔍 Scanning for signals...\n")

signals_found = []

for symbol, csv_path in WATCHLIST.items():
    try:
        # Load data
        ds = CsvDataSource(csv_path, datetime_column='date')
        df = ds.load()
        
        # Generate signals
        signal_series = strategy.generate_signals(df)
        
        # Check latest signal
        if len(signal_series) > 0:
            latest_signal = signal_series.iloc[-1]
            latest_price = df.iloc[-1]['close']
            latest_date = df.index[-1]
            
            if latest_signal == 1:
                print(f"   🟢 {symbol:12} BUY  @ ₹{latest_price:.2f}")
                signals_found.append({
                    'symbol': symbol,
                    'signal': 'BUY',
                    'price': latest_price,
                    'date': latest_date
                })
            elif latest_signal == -1:
                print(f"   🔴 {symbol:12} SELL @ ₹{latest_price:.2f}")
                signals_found.append({
                    'symbol': symbol,
                    'signal': 'SELL',
                    'price': latest_price,
                    'date': latest_date
                })
            else:
                print(f"   ⚪ {symbol:12} HOLD @ ₹{latest_price:.2f}")
                
    except Exception as e:
        print(f"   ❌ {symbol:12} Error: {e}")

# Send notifications for each signal
if signals_found:
    print(f"\n📨 Sending {len(signals_found)} notifications...\n")
    
    for sig in signals_found:
        # Create SignalEvent
        event = SignalEvent(
            symbol=sig['symbol'],
            signal=sig['signal'],
            price=sig['price'],
            timestamp=datetime.now(),
            strategy='MA Cross 5/20',
            metadata={'source': 'Angel One REAL data', 'date': str(sig['date'].date())}
        )
        
        # Send notification
        try:
            notifier.send(event)
            print(f"   ✅ Sent {sig['signal']} notification for {sig['symbol']}")
        except Exception as e:
            print(f"   ❌ Failed to send {sig['symbol']}: {e}")
else:
    print("\n⚪ No active signals found\n")

print("\n" + "=" * 80)
print("✅ NOTIFICATION TEST COMPLETE!")
print("=" * 80)
print("\n💡 Check:")
print("   - Console output above")
print("   - Desktop notification popup")
print("   - Telegram app for message")
print("=" * 80 + "\n")
