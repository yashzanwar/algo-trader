#!/usr/bin/env python3
"""
Download REAL historical data from Angel One and save to CSV.

This downloads data once and saves it locally, so you can use it for backtesting
without hitting the API every time.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys
import time  # For rate limiting

sys.path.insert(0, 'src')

from algotrader.data.angel_one import AngelOneDataSource

# Angel One credentials
API_KEY = "OF6qV328"
CLIENT_ID = "DEMO123"
PASSWORD = "1234"
TOTP_SECRET = "ABCDEFGHIJKLMNOP"

# Stocks to download
WATCHLIST = [
    "RELIANCE",
    "TCS",
    "INFY",
    "SBIN",
    "HDFCBANK",
]

# Data directory
data_dir = Path("examples/data")
data_dir.mkdir(parents=True, exist_ok=True)

print("\n" + "=" * 80)
print("📥 DOWNLOADING REAL DATA FROM ANGEL ONE")
print("=" * 80)

try:
    # Connect to Angel One
    print("\n1️⃣  Connecting to Angel One...", end=" ", flush=True)
    angel = AngelOneDataSource(API_KEY, CLIENT_ID, PASSWORD, TOTP_SECRET)
    print("✅")
    
    # Download data for each stock
    print("\n📊 Downloading 2 years of historical data...")
    print("⏱️  Adding 5-second delays between requests to avoid rate limits...\n")
    
    for symbol in WATCHLIST:
        try:
            print(f"   📈 {symbol}...", end=" ", flush=True)
            
            # Download 2 years of daily data
            data = angel.load(
                symbol=symbol,
                from_date=datetime.now() - timedelta(days=730),
                to_date=datetime.now(),
                interval="ONE_DAY"
            )
            
            # Save to CSV
            filename = f"{symbol.lower()}_ns.csv"
            output_path = data_dir / filename
            
            # Prepare data
            data.index.name = 'date'
            data.to_csv(output_path)
            
            # Show summary
            print(f"✅ {len(data)} days saved to {filename}")
            
            # Rate limiting: Wait 5 seconds before next request
            if symbol != WATCHLIST[-1]:  # Don't wait after last stock
                time.sleep(5)
            latest_price = data['close'].iloc[-1]
            first_date = data.index[0].date()
            last_date = data.index[-1].date()
            
            print(f"✅ {len(data)} days | ₹{latest_price:.2f}")
            print(f"      Range: {first_date} to {last_date}")
            print(f"      Saved: {output_path}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ REAL DATA DOWNLOADED!")
    print("=" * 80)
    print("\n📊 You now have REAL market data from Angel One!")
    print("\n💡 Next steps:")
    print("   1. Run backtests with real data:")
    print("      python examples/backtest_strategies.py")
    print("\n   2. Start live monitoring:")
    print("      python examples/live_monitor_angel.py")
    print("=" * 80 + "\n")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease check your Angel One credentials.")
