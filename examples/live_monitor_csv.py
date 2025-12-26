#!/usr/bin/env python3
"""
Live monitoring using CSV data (works offline, no API issues).

This is perfect for:
- Testing your strategy
- Corporate networks with blocked APIs
- Development without internet
- Reliable monitoring without rate limits
"""

import time
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

from algotrader.core import setup_logging
from algotrader.data import CsvDataSource
from algotrader.strategy import MovingAverageCrossStrategy
from algotrader.signals import (
    SignalMonitor,
    ConsoleNotifier,
    DesktopNotifier,
    TelegramNotifier,
    MultiNotifier
)

# Setup logging
setup_logging(level="INFO")


def simulate_live_from_csv(csv_path: Path, symbol: str, check_interval: int = 5):
    """
    Simulate live monitoring by progressively revealing CSV data.
    
    This simulates real-time by:
    1. Loading full historical data
    2. Revealing bars one at a time (like real-time updates)
    3. Checking for signals on each new bar
    """
    
    print("\n" + "=" * 80)
    print("🔴 SIMULATED LIVE MONITORING - CSV Data")
    print("=" * 80)
    print(f"\n📊 Symbol: {symbol}")
    print(f"📁 Data source: {csv_path}")
    print(f"⏰ Simulating checks every {check_interval} seconds")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Press Ctrl+C to stop\n")
    print("=" * 80)
    
    # Load full historical data
    data_source = CsvDataSource(path=csv_path)
    full_data = data_source.load()
    
    print(f"\n📈 Loaded {len(full_data)} bars")
    print(f"📅 Date range: {full_data.index[0]} to {full_data.index[-1]}")
    
    # Setup strategy
    strategy = MovingAverageCrossStrategy(
        fast_window=10,
        slow_window=50,
        min_separation_pct=0.3,
        use_trend_filter=True
    )
    
    # Setup notifiers
    notifiers = [
        ConsoleNotifier(),
        DesktopNotifier(),
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
    
    # Start from bar 200 (after warmup for 200-day MA)
    start_bar = 200
    
    print(f"\n📊 Starting simulation from bar {start_bar} (after warmup period)...")
    print(f"⏰ Will simulate {len(full_data) - start_bar} bars")
    print("\n" + "=" * 80 + "\n")
    
    # Main monitoring loop
    try:
        for i in range(start_bar, len(full_data)):
            # Simulate "current time" - only data up to this bar
            current_data = full_data.iloc[:i+1].copy()
            
            timestamp = current_data.index[-1]
            latest_price = current_data['close'].iloc[-1]
            
            print(f"🔄 [{timestamp}] Bar {i}/{len(full_data)-1} - Price: ₹{latest_price:.2f}", end=" ")
            
            try:
                # Check for signals
                event = monitor.check_for_signals(symbol, current_data)
                
                if event:
                    # Signal detected!
                    print(f"\n\n{'=' * 80}")
                    print(f"🚨 SIGNAL DETECTED!")
                    print(f"{'=' * 80}")
                    monitor.notify(event)
                    print(f"{'=' * 80}\n")
                else:
                    # No signal
                    print("✓")
            
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Wait before next "tick" (simulate real-time delay)
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("🛑 Monitoring stopped by user")
        print("=" * 80)
        print(f"🕐 Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)


if __name__ == "__main__":
    # Use existing CSV data
    csv_path = Path("examples/data/reliance_ns.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        print("\n💡 Run this first to generate data:")
        print("   python examples/scan_stocks_csv.py")
        exit(1)
    
    # Simulate live monitoring
    simulate_live_from_csv(
        csv_path=csv_path,
        symbol="RELIANCE.NS",
        check_interval=2  # 2 seconds per bar (fast simulation)
    )
    
    # ============================================================================
    # 🎯 WHY USE CSV INSTEAD OF LIVE API?
    # ============================================================================
    # 
    # ✅ Advantages:
    # - Works offline (no internet needed)
    # - No rate limits
    # - No SSL/firewall issues
    # - Consistent data for testing
    # - Faster than real-time (adjust check_interval)
    # - Perfect for development
    # 
    # ❌ Limitations:
    # - Historical data only (not truly live)
    # - No actual trading
    # 
    # 💡 Use this for:
    # 1. Testing your strategy logic
    # 2. Validating signal detection
    # 3. Testing notifications (Console/Desktop/Telegram)
    # 4. Development in corporate networks
    # 
    # Then switch to live API (Upstox/Zerodha) for real trading!
    # ============================================================================
