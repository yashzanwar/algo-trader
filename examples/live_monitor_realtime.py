#!/usr/bin/env python3
"""
Real-time live monitoring with yfinance.

This script demonstrates how to monitor stocks in real-time and detect signals.
Replace yfinance with Zerodha/Upstox API for true real-time trading.
"""

import time
import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path
import ssl
import urllib.request

from algotrader.core import setup_logging
from algotrader.strategy import MovingAverageCrossStrategy
from algotrader.signals import (
    SignalMonitor,
    ConsoleNotifier,
    DesktopNotifier,
    TelegramNotifier,
    MultiNotifier
)

# Disable SSL verification for corporate networks
ssl._create_default_https_context = ssl._create_unverified_context

# Setup logging
setup_logging(level="INFO")


def get_live_data(symbol: str, period: str = "5d", interval: str = "1m") -> pd.DataFrame:
    """
    Fetch live data from Yahoo Finance.
    
    Note: This has 15-min delay. For real-time, use:
    - Zerodha Kite Connect (WebSocket)
    - Upstox API (WebSocket)
    - Alpha Vantage API
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data is None or data.empty:
            print(f"⚠️  No data returned for {symbol}")
            return None
        
        # Rename columns to match framework
        data.columns = [col.lower() for col in data.columns]
        data.index.name = 'timestamp'
        
        return data
        
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None


def monitor_live(symbols: list[str], check_interval: int = 60):
    """
    Monitor stocks in real-time.
    
    Args:
        symbols: List of symbols to monitor (e.g., ['RELIANCE.NS', 'TCS.NS'])
        check_interval: Seconds between checks (60 = 1 minute)
    """
    
    print("\n" + "=" * 80)
    print("🔴 LIVE MONITORING - Real-Time Signal Detection")
    print("=" * 80)
    print(f"\n📊 Monitoring: {', '.join(symbols)}")
    print(f"⏰ Check interval: {check_interval} seconds")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Press Ctrl+C to stop\n")
    print("=" * 80)
    
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
        symbols=symbols
    )
    
    # Main monitoring loop
    try:
        iteration = 0
        while True:
            iteration += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"print(f"   📡 Fetching {symbol}...", end=" ")
                    data = get_live_data(symbol, period="5d", interval="1m")
                    
                    if data is None:
                        print(f"⚠️  Failed to fetch data")
                        continue
                    
                    if len(data) < 200:
                        print(f"⚠️  Insufficient data ({len(data)} bars, need 200+)")
                        continue
                    
                    latest_price = data['close'].iloc[-1]
                    
                    # Check for signals
                    event = monitor.check_for_signals(symbol, data)
                    
                    if event:
                        # Signal detected!
                        print(f"\n{'=' * 80}")
                        print(f"🚨 SIGNAL DETECTED!")
                        print(f"{'=' * 80}")
                        monitor.notify(event)
                    else:
                        # No signal
                        print(f"₹{latest_price:.2f} ✓")
                
                except Exception as e:
                    print(f"❌ Error: {str(e)[:50]
                        # No signal
                        print(f"   {symbol}: ₹{latest_price:.2f} - No signal")
                
                except Exception as e:
                    print(f"❌ Error fetching {symbol}: {e}")
            
            # Wait before next check
            print(f"\n⏳ Waiting {check_interval} seconds...")
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("🛑 Monitoring stopped by user")
        print("=" * 80)
        print(f"📊 Total iterations: {iteration}")
        print(f"🕐 Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)


if __name__ == "__main__":
    # Define your watchlist (max 10-20 stocks for free API)
    WATCHLIST = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "SBIN.NS",
    ]
    
    # Monitor every 60 seconds (1 minute)
    # For real-time WebSocket, this becomes event-driven (no polling)
    monitor_live(
        symbols=WATCHLIST,
        check_interval=60  # Check every 1 minute
    )
    
    # ============================================================================
    # 🚀 NEXT STEPS:
    # ============================================================================
    # 
    # 1. For Paper Trading:
    #    - Open Upstox/Angel One account (free API)
    #    - Replace get_live_data() with their WebSocket
    #    - Get tick-by-tick updates (no delay)
    # 
    # 2. For Production Trading:
    #    - Use Zerodha Kite Connect WebSocket
    #    - Add order execution (kite.place_order())
    #    - Add risk management (position sizing, stop loss)
    # 
    # 3. Run as Background Service:
    #    - Deploy on VPS/cloud server
    #    - Run during market hours only (9:15 AM - 3:30 PM)
    #    - Use systemd/supervisor for auto-restart
    # 
    # 4. Cron Schedule (Linux/Mac):
    #    - Start at 9:15 AM: 15 9 * * 1-5 /path/to/script.py
    #    - Stop at 3:30 PM: 30 15 * * 1-5 pkill -f live_monitor
    # 
    # ============================================================================
