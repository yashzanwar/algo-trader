#!/usr/bin/env python3
"""Generate realistic test data for Indian stocks (₹1,200-1,300 range for Reliance)."""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

np.random.seed(42)  # Reproducible data

def generate_realistic_stock_data(
    symbol: str,
    base_price: float,
    volatility: float,
    trend: float,
    days: int = 730
) -> pd.DataFrame:
    """
    Generate realistic stock price data.
    
    Args:
        symbol: Stock symbol
        base_price: Starting price (e.g., 1250 for Reliance)
        volatility: Daily volatility (e.g., 0.02 = 2%)
        trend: Annual trend (e.g., 0.15 = 15% growth/year)
        days: Number of trading days
    """
    dates = pd.date_range(
        end=datetime.now(),
        periods=days,
        freq='D'
    )
    
    # Generate realistic price movement
    returns = np.random.normal(
        trend/252,  # Daily trend
        volatility,
        days
    )
    
    # Price path
    price_multipliers = (1 + returns).cumprod()
    close_prices = base_price * price_multipliers
    
    # Generate OHLC from close
    data = pd.DataFrame(index=dates)
    data['close'] = close_prices
    data['open'] = data['close'].shift(1).fillna(base_price)
    
    # High/Low with realistic spreads
    daily_range = np.random.uniform(0.01, 0.03, days)  # 1-3% daily range
    data['high'] = data['close'] * (1 + daily_range)
    data['low'] = data['close'] * (1 - daily_range)
    
    # Volume (realistic for NSE)
    base_volume = {
        'RELIANCE.NS': 3_000_000,
        'TCS.NS': 2_000_000,
        'INFY.NS': 5_000_000,
        'SBIN.NS': 15_000_000,
        'HDFCBANK.NS': 4_000_000,
    }.get(symbol, 2_000_000)
    
    data['volume'] = np.random.randint(
        base_volume * 0.5,
        base_volume * 2,
        days
    )
    
    data.index.name = 'date'
    return data[['open', 'high', 'low', 'close', 'volume']]


# Stock configurations (realistic current prices)
stocks = {
    'RELIANCE.NS': {
        'base_price': 1250.0,  # ₹1,250 (realistic Dec 2023 price)
        'volatility': 0.018,    # 1.8% daily volatility
        'trend': 0.12,          # 12% annual growth
        'filename': 'reliance_ns.csv'
    },
    'TCS.NS': {
        'base_price': 3200.0,   # ₹3,200
        'volatility': 0.015,
        'trend': 0.10,
        'filename': 'tcs_ns.csv'
    },
    'INFY.NS': {
        'base_price': 1400.0,   # ₹1,400
        'volatility': 0.016,
        'trend': 0.14,
        'filename': 'infy_ns.csv'
    },
    'SBIN.NS': {
        'base_price': 550.0,    # ₹550
        'volatility': 0.022,
        'trend': 0.18,
        'filename': 'sbin_ns.csv'
    },
    'HDFCBANK.NS': {
        'base_price': 1600.0,   # ₹1,600
        'volatility': 0.014,
        'trend': 0.08,
        'filename': 'hdfcbank_ns.csv'
    }
}

# Create data directory
data_dir = Path('examples/data')
data_dir.mkdir(parents=True, exist_ok=True)

print("\n" + "=" * 80)
print("📊 GENERATING REALISTIC TEST DATA")
print("=" * 80)
print("\n💡 Using realistic price ranges for NSE stocks")
print("📅 Generating 2 years (730 days) of data\n")

for symbol, config in stocks.items():
    print(f"\n📈 {symbol}")
    print(f"   Base price: ₹{config['base_price']:,.2f}")
    
    # Generate data
    data = generate_realistic_stock_data(
        symbol=symbol,
        base_price=config['base_price'],
        volatility=config['volatility'],
        trend=config['trend'],
        days=730
    )
    
    # Save to CSV
    output_path = data_dir / config['filename']
    data.to_csv(output_path)
    
    # Summary
    latest_price = data['close'].iloc[-1]
    price_change = ((latest_price / config['base_price']) - 1) * 100
    
    print(f"   Latest price: ₹{latest_price:,.2f}")
    print(f"   Change: {price_change:+.1f}%")
    print(f"   Range: ₹{data['close'].min():,.2f} - ₹{data['close'].max():,.2f}")
    print(f"   💾 Saved to: {output_path}")

print("\n" + "=" * 80)
print("✅ REALISTIC DATA GENERATED!")
print("=" * 80)
print("\n💡 Now run:")
print("   python examples/live_monitor_csv.py")
print("\nYou'll see realistic prices like:")
print("   - RELIANCE.NS: ~₹1,250-1,400")
print("   - TCS.NS: ~₹3,200-3,600")
print("   - SBIN.NS: ~₹550-650")
print("=" * 80 + "\n")
