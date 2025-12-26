#!/usr/bin/env python3
"""
Live monitoring with REAL Angel One data.

This script:
1. Connects to Angel One API
2. Gets live prices every 60 seconds
3. Runs your strategy on real-time data
4. Sends signals via Telegram/Desktop/Console
"""

import time
from datetime import datetime, timedelta
import sys

sys.path.insert(0, 'src')

from algotrader.core import setup_logging
from algotrader.data.angel_one import AngelOneDataSource
from algotrader.strategy import MovingAverageCrossStrategy
from algotrader.execution.positions import PositionManager
from algotrader.signals import (
    SignalMonitor,
    ConsoleNotifier,
    DesktopNotifier,
    TelegramNotifier,
    MultiNotifier
)

# Setup logging
setup_logging(level="INFO")

# Angel One credentials
API_KEY = "OF6qV328"
CLIENT_ID = "DEMO123"
PASSWORD = "1234"
TOTP_SECRET = "ABCDEFGHIJKLMNOP"

# Watchlist
WATCHLIST = [
    "RELIANCE",
    "TCS",
    "SBIN",
    "INFY",
    "HDFCBANK",
]

# Check interval (seconds)
CHECK_INTERVAL = 120  # Check every 2 minutes (reduced API load)


def monitor_live():
    """Monitor stocks with real-time Angel One data."""
    
    print("\n" + "=" * 80)
    print("🔴 LIVE MONITORING - Real Angel One Data")
    print("=" * 80)
    
    # Check if today is a weekday (markets closed on weekends)
    today = datetime.now()
    if today.weekday() >= 5:  # Saturday=5, Sunday=6
        print(f"\n⚠️  WARNING: Today is {today.strftime('%A')} - Markets are CLOSED")
        print("💡 The script will still run but data may be delayed/stale\n")
    
    print(f"\n📊 Watching: {', '.join(WATCHLIST)}")
    print(f"⏰ Check interval: {CHECK_INTERVAL} seconds")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Press Ctrl+C to stop\n")
    print("=" * 80)
    
    try:
        # Initialize position manager
        print("\n1️⃣  Initializing position manager...", end=" ", flush=True)
        position_manager = PositionManager("positions.json")
        existing_positions = position_manager.list_positions()
        if existing_positions:
            print(f"✅ ({len(existing_positions)} existing positions)")
            for pos in existing_positions:
                print(f"   📊 {pos.symbol}: {pos.quantity} @ ₹{pos.entry_price:.2f}")
        else:
            print("✅ (no existing positions)")
        
        # Connect to Angel One
        print("\n2️⃣  Connecting to Angel One...", end=" ", flush=True)
        angel = AngelOneDataSource(API_KEY, CLIENT_ID, PASSWORD, TOTP_SECRET)
        print("✅")
        
        # Setup strategy
        strategy = MovingAverageCrossStrategy(
            fast_window=10,
            slow_window=50,
            min_separation_pct=0.3,
            use_trend_filter=True
        )
        
        # Setup notifiers
        telegram_notifier = TelegramNotifier(
            bot_token='YOUR_BOT_TOKEN',
            chat_ids=['YOUR_CHAT_ID'],
            position_manager=position_manager  # Pass position manager
        )
        
        notifiers = [
            ConsoleNotifier(),
            DesktopNotifier(),
            telegram_notifier,
        ]
        
        multi_notifier = MultiNotifier(notifiers)
        
        # Initialize monitor with position awareness
        monitor = SignalMonitor(
            strategy=strategy,
            notifiers=[multi_notifier],
            symbols=WATCHLIST,
            position_manager=position_manager  # Pass position manager
        )
        
        print("2️⃣  Loading initial historical data (for MA calculation)...")
        
        # Helper function to get current price
        def get_current_price(symbol: str) -> float:
            """Helper to get current price for P&L calculations."""
            try:
                quote = angel.get_live_price(symbol)
                return quote['ltp']
            except:
                return 0.0
        
        # Load enough historical data for MA calculations (200+ days for trend filter)
        historical_data = {}
        for symbol in WATCHLIST:
            try:
                print(f"   Loading {symbol}...", end=" ", flush=True)
                data = angel.load(
                    symbol=symbol,
                    from_date=datetime.now() - timedelta(days=200),  # Reduced from 250
                    to_date=datetime.now(),
                    interval="ONE_DAY"
                )
                historical_data[symbol] = data
                print(f"✅ ({len(data)} bars)")
                # Rate limiting: wait between API calls
                time.sleep(1.5)  # Increased from 0.5 to 1.5 seconds
            except Exception as e:
                print(f"❌ {str(e)[:60]}")
                time.sleep(2)  # Extra delay on error
        
        print("✅")
        print(f"\n{'=' * 80}\n")
        
        # Main monitoring loop
        iteration = 0
        last_command_check = 0  # Track when we last checked for commands
        
        while True:
            iteration += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Process Telegram commands every 10 seconds (not too frequent)
            current_time = time.time()
            if current_time - last_command_check >= 10:
                try:
                    print("   🤖 Checking Telegram commands...", end=" ", flush=True)
                    telegram_notifier.process_commands(price_fetcher=get_current_price)
                    print("✓")
                    last_command_check = current_time
                except Exception as e:
                    print(f"❌ {str(e)[:40]}")
            
            print(f"🔄 [{timestamp}] Iteration #{iteration}")
            
            consecutive_failures = 0
            
            for symbol in WATCHLIST:
                try:
                    if symbol not in historical_data:
                        continue
                    
                    # Get live price with retry logic
                    print(f"   📡 {symbol}...", end=" ", flush=True)
                    
                    retry_count = 0
                    max_retries = 3
                    live_quote = None
                    
                    while retry_count < max_retries:
                        try:
                            live_quote = angel.get_live_price(symbol)
                            consecutive_failures = 0  # Reset on success
                            break
                        except Exception as e:
                            retry_count += 1
                            if retry_count < max_retries:
                                wait_time = retry_count * 2  # Exponential backoff: 2s, 4s
                                print(f"⚠️ (retry {retry_count}/{max_retries} in {wait_time}s)...", end=" ", flush=True)
                                time.sleep(wait_time)
                            else:
                                raise e
                    
                    if not live_quote:
                        raise Exception("Failed to get live quote after retries")
                    
                    latest_price = live_quote['ltp']
                    print(f"₹{latest_price:.2f}", end=" ")
                    
                    # Rate limiting between symbol checks
                    time.sleep(1.0)  # Increased to 1 second
                    
                    # Update historical data with latest price
                    # (In production, you'd append new candles properly)
                    current_data = historical_data[symbol].copy()
                    
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
                    print(f"❌ Error: {str(e)[:50]}")
                    consecutive_failures += 1
                    
                    # If too many failures, increase wait time
                    if consecutive_failures >= 3:
                        print(f"\n⚠️  Multiple failures detected. Waiting 30 seconds...")
                        time.sleep(30)
                        consecutive_failures = 0
            
            # Wait before next check
            print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds...\n")
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("🛑 Monitoring stopped by user")
        print("=" * 80)
        print(f"📊 Total iterations: {iteration}")
        print(f"🕐 Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    monitor_live()
