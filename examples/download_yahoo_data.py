#!/usr/bin/env python3
"""Download REAL historical data from Yahoo Finance."""

import yfinance as yf
import pandas as pd
from pathlib import Path

# Create data directory
data_dir = Path("examples/data")
data_dir.mkdir(parents=True, exist_ok=True)

# Stocks to download - REAL DATA
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "SBIN.NS",
    "HDFCBANK.NS",
]

print("\n" + "=" * 80)
print("📥 DOWNLOADING REAL DATA FROM YAHOO FINANCE")
print("=" * 80)
print("\nTesting network access to Yahoo Finance API...\n")

for symbol in stocks:
    try:
        print(f"📊 Downloading {symbol}...", end=" ", flush=True)
        
        # Download REAL 2 years of daily data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="2y", interval="1d")
        
        if data.empty:
            print("❌ No data returned")
            continue
        
        # Prepare data
        data.index.name = 'date'
        data.columns = [col.lower() for col in data.columns]
        
        # Save to CSV
        filename = f"{symbol.lower().replace('.', '_')}.csv"
        output_path = data_dir / filename
        data.to_csv(output_path)
        
        # Show summary
        latest_price = data['close'].iloc[-1]
        first_date = data.index[0].date()
        last_date = data.index[-1].date()
        
        print(f"✅ SUCCESS!")
        print(f"   📅 Range: {first_date} to {last_date} ({len(data)} days)")
        print(f"   💰 Latest close: ₹{latest_price:.2f}")
        print(f"   💾 Saved: {output_path}")
        print()
        
    except Exception as e:
        print(f"❌ FAILED")
        print(f"   Error: {str(e)[:100]}")
        print(f"\n⚠️  Yahoo Finance blocked by your network!")
        print(f"   Error details: {type(e).__name__}")
        break

print("=" * 80)
