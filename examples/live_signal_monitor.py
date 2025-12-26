#!/usr/bin/env python3
"""Real-time signal monitoring - Get notified when crossovers happen."""

import pandas as pd
import time
from pathlib import Path
from datetime import datetime

from algotrader.core import setup_logging
from algotrader.data import CsvDataSource
from algotrader.strategy import MovingAverageCrossStrategy
from algotrader.signals import SignalMonitor, ConsoleNotifier, DesktopNotifier, TelegramNotifier, MultiNotifier

# Setup logging
setup_logging(level="INFO")


def simulate_live_monitoring():
    """Simulate live monitoring by progressively adding new bars."""
    
    print("\n" + "=" * 80)
    print("🔴 LIVE SIGNAL MONITORING - MA Cross (10/50) on SBIN.NS")
    print("=" * 80)
    print("\n📊 Monitoring for Golden Cross (BUY) and Death Cross (SELL) signals...")
    print("💡 You'll get notified when crossover happens\n")
    
    # Load historical data - use RELIANCE since we have it
    csv_path = Path("examples/data/reliance_ns.csv")
    symbol = "RELIANCE.NS"
    
    if not csv_path.exists():
        print(f"❌ Error: {csv_path} not found")
        print("💡 Run: python examples/scan_stocks_csv.py first to generate data")
        return
    
    data_source = CsvDataSource(path=csv_path)
    full_data = data_source.load()
    
    # Setup strategy
    strategy = MovingAverageCrossStrategy(
        fast_window=10,
        slow_window=50,
        min_separation_pct=0.3,
        use_trend_filter=True
    )
    
    # Setup notifiers
    notifiers = [
        ConsoleNotifier(),  # Always show in console
        DesktopNotifier(),  # Desktop notification (macOS/Linux)
        TelegramNotifier(
            bot_token='YOUR_BOT_TOKEN',
            chat_ids=['YOUR_CHAT_ID']
        ),
    ]
    
    multi_notifier = MultiNotifier(notifiers)
    
    # Initialize monitor
    monitor = SignalMonitor(
        strategy=strategy,
        notifiers=[multi_notifier],
        symbols=[symbol]
    )
    
    # Simulate live monitoring by adding bars progressively
    # Start from bar 200 (need history for 200-day MA)
    warmup = 200
    print(f"📈 Starting simulation from bar {warmup} (after warmup period)...")
    print(f"📅 Data range: {full_data.index[warmup]} to {full_data.index[-1]}")
    print(f"⏰ Simulating ~{len(full_data) - warmup} days of trading...\n")
    print("=" * 80 + "\n")
    
    signal_count = 0
    
    for i in range(warmup, len(full_data)):
        # Get data up to current bar
        current_data = full_data.iloc[:i+1]
        current_date = current_data.index[-1]
        current_price = current_data['close'].iloc[-1]
        
        # Check for signals
        event = monitor.check_for_signals(symbol, current_data)
        
        if event:
            signal_count += 1
            monitor.notify(event)
            time.sleep(1)  # Brief pause to see notification
        else:
            # Show progress every 10 days
            if i % 10 == 0:
                print(f"⏳ {current_date.strftime('%Y-%m-%d')}: Monitoring... Price: ₹{current_price:.2f} (No signal)")
    
    print("\n" + "=" * 80)
    print("✅ SIMULATION COMPLETE")
    print("=" * 80)
    print(f"📊 Total signals detected: {signal_count}")
    print(f"📅 Period monitored: {full_data.index[warmup]} to {full_data.index[-1]}")
    print("\n💡 In real-time:")
    print("  - Run this script as a cron job every 15 minutes")
    print("  - Fetch latest price from broker API")
    print("  - Get notified instantly when crossover happens")
    print("=" * 80 + "\n")


def live_monitoring_template():
    """Template for real-time monitoring with live data."""
    
    print("\n" + "=" * 80)
    print("📌 TEMPLATE: Real-Time Monitoring (Use with live data)")
    print("=" * 80)
    
    template = """
# Real-time monitoring script (run every 15 minutes via cron)

import yfinance as yf
from datetime import datetime, timedelta

def fetch_live_data(symbol):
    \"\"\"Fetch latest data from Yahoo Finance or your broker API.\"\"\"
    ticker = yf.Ticker(symbol)
    # Get last 300 days for MA calculations
    end_date = datetime.now()
    start_date = end_date - timedelta(days=300)
    df = ticker.history(start=start_date, end=end_date)
    return df

# Monitor every 15 minutes
while True:
    # Fetch latest data
    data = fetch_live_data('SBIN.NS')
    
    # Check for signals
    event = monitor.check_for_signals('SBIN.NS', data)
    
    if event:
        monitor.notify(event)  # You'll get instant notification!
    
    # Sleep for 15 minutes
    time.sleep(15 * 60)

# Or set up as cron job:
# */15 9-15 * * 1-5  cd /path/to/project && python live_monitor.py
# (Every 15 min, 9am-3pm, weekdays only)
"""
    
    print(template)
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--template':
        live_monitoring_template()
    else:
        simulate_live_monitoring()
