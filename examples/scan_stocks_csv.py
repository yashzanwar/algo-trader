#!/usr/bin/env python3
"""Stock scanner using local CSV files - works without internet."""

import pandas as pd
import numpy as np
from pathlib import Path

from algotrader.core import setup_logging, BrokerConfig
from algotrader.data import CsvDataSource
from algotrader.engine.backtester import Backtester
from algotrader.execution.broker import SimulatedBroker
from algotrader.strategy import MovingAverageCrossStrategy, MeanReversionStrategy

# Suppress verbose logging
setup_logging(level="WARNING")

# Generate sample data for multiple stocks
def create_sample_stock_data(symbol: str, trend: str = "sideways", seed: int = 42) -> Path:
    """Create realistic sample stock data with fixed seed for reproducibility."""
    csv_path = Path(f"examples/data/{symbol.replace('.', '_').lower()}.csv")
    
    if csv_path.exists():
        return csv_path
    
    # Set seed for reproducibility - same seed = same data every time
    np.random.seed(seed + hash(symbol) % 1000)
    
    # Last 2 years of trading data
    dates = pd.date_range("2024-12-25", "2025-12-25", freq="B")
    n_days = len(dates)
    
    # Different price patterns for different stocks
    if trend == "uptrend":
        close = 100 + np.cumsum(np.random.randn(n_days) * 2 + 0.3)
    elif trend == "downtrend":
        close = 100 + np.cumsum(np.random.randn(n_days) * 2 - 0.3)
    else:  # sideways
        close = 100 + np.cumsum(np.random.randn(n_days) * 1.5)
    
    df = pd.DataFrame({
        "date": dates,
        "open": close - np.abs(np.random.randn(n_days) * 2),
        "high": close + np.abs(np.random.randn(n_days) * 3),
        "low": close - np.abs(np.random.randn(n_days) * 3),
        "close": close,
        "volume": np.random.randint(1000000, 5000000, n_days),
    })
    
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path


# Define sample stocks with different characteristics
SAMPLE_STOCKS = {
    "RELIANCE.NS": "uptrend",
    "TCS.NS": "sideways",
    "HDFCBANK.NS": "uptrend",
    "INFY.NS": "sideways",
    "ICICIBANK.NS": "downtrend",
}


def scan_stock(symbol: str, csv_path: Path, strategy, broker=None) -> dict:
    """Scan a single stock."""
    try:
        data_source = CsvDataSource(path=csv_path)
        prices = data_source.load()
        
        if len(prices) < 100:
            return {"symbol": symbol, "error": "Insufficient data"}
        
        backtester = Backtester(strategy, broker=broker)
        result = backtester.run(prices)
        
        return {
            "symbol": symbol,
            "sharpe": result.metrics["sharpe_ratio"],
            "total_return": result.metrics["total_return"],
            "max_drawdown": result.metrics["max_drawdown"],
            "win_rate": result.metrics["win_rate"],
            "profit_factor": result.metrics["profit_factor"],
            "trades": result.trades,
            "error": None,
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def print_results(results: list, strategy_name: str):
    """Print formatted results."""
    # Sort by Sharpe
    results.sort(key=lambda x: x.get("sharpe", -999), reverse=True)
    
    print("\n" + "=" * 100)
    print(f"SCAN RESULTS - {strategy_name}")
    print("=" * 100)
    print(f"{'Rank':<6} {'Symbol':<15} {'Sharpe':<10} {'Return':<12} {'MaxDD':<10} {'Win%':<10} {'PF':<8} {'Trades':<8}")
    print("-" * 100)
    
    for i, r in enumerate(results, 1):
        if r["error"]:
            print(f"{i:<6} {r['symbol']:<15} {'ERROR':<10} {'-':<12} {'-':<10} {'-':<10} {'-':<8} {'-':<8}")
        else:
            print(
                f"{i:<6} {r['symbol']:<15} "
                f"{r['sharpe']:<10.2f} "
                f"{r['total_return']:<12.2%} "
                f"{r['max_drawdown']:<10.2%} "
                f"{r['win_rate']:<10.1%} "
                f"{r['profit_factor']:<8.2f} "
                f"{r['trades']:<8}"
            )
    
    print("=" * 100)


# Main scanning
print("=" * 100)
print("MULTI-STOCK SCANNER - Testing Strategies on Sample Data")
print("=" * 100)

# Configure realistic Indian brokerage costs
broker_config = BrokerConfig(
    commission_bps=7.0,  # Brokerage + STT + charges (~0.07%)
    slippage_bps=3.0,    # Market impact/slippage (~0.03%)
    execution_delay_bars=1
)
broker = SimulatedBroker(config=broker_config)

print("\n💰 Brokerage Settings:")
print(f"   Commission: {broker_config.commission_bps} bps (0.{broker_config.commission_bps:02.0f}%)")
print(f"   Slippage:   {broker_config.slippage_bps} bps (0.{broker_config.slippage_bps:02.0f}%)")
print(f"   Total Cost: ~0.{broker_config.commission_bps + broker_config.slippage_bps:02.0f}% per trade")

print("\n📊 Generating sample stock data (with fixed seed for reproducibility)...")

# Create sample data for all stocks
stock_files = {}
for symbol, trend in SAMPLE_STOCKS.items():
    csv_path = create_sample_stock_data(symbol, trend, seed=42)
    stock_files[symbol] = csv_path
    print(f"  ✓ {symbol:<15} ({trend})")

# Test multiple MA strategies
strategies = [
    ("MA Cross (5/20) - Standard", MovingAverageCrossStrategy(fast_window=5, slow_window=20, min_separation_pct=0.2, use_trend_filter=True)),
    ("MA Cross (5/20) - Strict Filter", MovingAverageCrossStrategy(fast_window=5, slow_window=20, min_separation_pct=0.5, use_trend_filter=True)),
    ("MA Cross (10/50)", MovingAverageCrossStrategy(fast_window=10, slow_window=50, min_separation_pct=0.3, use_trend_filter=True)),
    ("MA Cross (20/100)", MovingAverageCrossStrategy(fast_window=20, slow_window=100, min_separation_pct=0.5, use_trend_filter=True)),
    ("MA Cross (10/50) - No Filter", MovingAverageCrossStrategy(fast_window=10, slow_window=50, min_separation_pct=0.0, use_trend_filter=False)),
]

for strategy_name, strategy in strategies:
    print(f"\n\n🔍 Scanning with {strategy_name}...")
    results = []
    
    for symbol, csv_path in stock_files.items():
        result = scan_stock(symbol, csv_path, strategy, broker=broker)
        results.append(result)
    
    print_results(results, strategy_name)

print("\n\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print("✅ Scanned 5 stocks with 4 different strategies")
print("📈 Best stocks are ranked by Sharpe ratio (higher is better)")
print("💡 Sharpe > 1.0 is good, > 2.0 is excellent")
print("\n� All returns include realistic costs:")
print("   • Brokerage + STT + charges: ~0.07% per trade")
print("   • Slippage: ~0.03% per trade")
print("   • Total impact: ~0.10% per round-trip")
print("\n�📝 NOTE: This uses sample data. For real trading:")
print("   1. Download real stock data from your broker")
print("   2. Save as CSV in examples/data/")
print("   3. Update SAMPLE_STOCKS dict with actual file paths")
print("=" * 100)
