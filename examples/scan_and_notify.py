#!/usr/bin/env python3
"""
Scan watchlist for signals and send notifications.
Uses REAL Angel One data from CSV files.
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from datetime import datetime
from algotrader.data.source import CsvDataSource
from algotrader.strategy import MovingAverageCrossStrategy
from algotrader.signals.monitor import SignalEvent
from algotrader.signals.notifier import (
    TelegramNotifier,
    DesktopNotifier,
    ConsoleNotifier,
    MultiNotifier
)

# Telegram config
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "7849078894"

# Watchlist
WATCHLIST = {
    "RELIANCE": "examples/data/reliance_ns.csv",
    "TCS": "examples/data/tcs_ns.csv",
    "SBIN": "examples/data/sbin_ns.csv",
    "INFY": "examples/data/infy_ns.csv",
    "HDFCBANK": "examples/data/hdfcbank_ns.csv",
}

print("\n" + "=" * 80)
print("🔍 SCANNING FOR TRADING SIGNALS (REAL Angel One Data)")
print("=" * 80)

# Setup notifications
notifier = MultiNotifier([
    ConsoleNotifier(),
    DesktopNotifier(),
    TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
])

# Setup strategy
strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=20)

signals_found = []

for symbol, csv_path in WATCHLIST.items():
    if not Path(csv_path).exists():
        print(f"⚠️  {symbol}: CSV not found")
        continue
    
    try:
        # Load REAL data
        ds = CsvDataSource(csv_path, datetime_column='date')
        df = ds.load()
        
        # Generate signals
        signal_series = strategy.generate_signals(df)
        
        # Check latest signal
        latest_signal = signal_series.iloc[-1]
        latest_price = df.iloc[-1]['close']
        latest_date = df.index[-1]
        
        print(f"\n📊 {symbol:12} ₹{latest_price:8.2f}  ({latest_date.strftime('%Y-%m-%d')})", end="")
        
        if latest_signal == 1:
            print("  🟢 BUY")
            signals_found.append({
                'symbol': symbol,
                'signal': 'BUY',
                'price': latest_price,
                'date': latest_date
            })
            
            # Create signal event
            event = SignalEvent(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type='BUY',
                price=latest_price,
                strategy='MA Cross (5/20)',
                reason=f'Fast MA crossed above Slow MA on {latest_date.strftime("%Y-%m-%d")}',
                metadata={'source': 'Angel One (REAL data)', 'date': latest_date.strftime('%Y-%m-%d')}
            )
            
            # Send notification
            notifier.send(event)
            
        elif latest_signal == -1:
            print("  🔴 SELL")
            signals_found.append({
                'symbol': symbol,
                'signal': 'SELL',
                'price': latest_price,
                'date': latest_date
            })
            Create signal event
            event = SignalEvent(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type='SELL',
                price=latest_price,
                strategy='MA Cross (5/20)',
                reason=f'Fast MA crossed below Slow MA on {latest_date.strftime("%Y-%m-%d")}',
                metadata={'source': 'Angel One (REAL data)', 'date': latest_date.strftime('%Y-%m-%d')}
            )
            
            # Send notification
            notifier.send(event
            notifier.notify(message)
        else:
            print("  ⚪ HOLD")
            
    except Exception as e:
        print(f"\n❌ {symbol}: Error - {e}")

print("\n" + "=" * 80)
if signals_found:
    print(f"✅ Found {len(signals_found)} signal(s)")
    print("📱 Notifications sent to Telegram + Desktop")
else:
    print("⚪ No active signals")
print("=" * 80 + "\n")
