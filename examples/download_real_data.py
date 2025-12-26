#!/usr/bin/env python3
"""Download real historical data for stocks."""

import yfinance as yf
import pandas as pd
from pathlib import Path
import ssl

# Disable SSL verification for corporate networks
ssl._create_default_https_context = ssl._create_unverified_context

# Create data directory
data_dir = Path("examples/data")
data_dir.mkdir(parents=True, exist_ok=True)

# Stocks to download
stocks = {
    "RELIANCE.NS": "reliance_ns.csv",
    "TCS.NS": "tcs_ns.csv",
    "INFY.NS": "infy_ns.csv",
    "SBIN.NS": "sbin_ns.csv",
    "HDFCBANK.NS": "hdfcbank_ns.csv",
}

print("\n📥 Downloading real historical data from Yahoo Finance...\n")
print("=" * 80)

for symbol, filename in stocks.items():
    try:
        print(f"\n📊 Fetching {symbol}...")
        
        # Download 2 years of daily data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="2y", interval="1d")
        
        if data.empty:
            print(f"   ❌ No data available")
            continue
        
        # Save to CSV
        output_path = data_dir / filename
        
        # Prepare data
        data.index.name = 'date'
        data.columns = [col.lower() for col in data.columns]
        
        # Save
        data.to_csv(output_path)
        
        # Show summary
        latest = data.iloc[-1]
        print(f"   ✅ Downloaded {len(data)} bars")
        print(f"   📅 Range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"   💰 Latest price: ₹{latest['close']:.2f}")
        print(f"   💾 Saved to: {output_path}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ Download complete!")
print("\n💡 Now you can run:")
print("   python examples/live_monitor_csv.py")
print("=" * 80 + "\n")
