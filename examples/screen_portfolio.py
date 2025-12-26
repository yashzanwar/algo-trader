#!/usr/bin/env python3
"""Example: Professional multi-stage stock screening for portfolio construction."""

import pandas as pd
import numpy as np
from pathlib import Path

from algotrader.core import setup_logging, BrokerConfig
from algotrader.data import CsvDataSource
from algotrader.engine.backtester import Backtester
from algotrader.execution.broker import SimulatedBroker
from algotrader.strategy import MovingAverageCrossStrategy
from algotrader.screener import StockScreener, ScreeningCriteria

# Setup logging
setup_logging(level="INFO")

# Generate sample universe of stocks
def create_sample_universe(num_stocks: int = 50, seed: int = 42) -> dict[str, pd.DataFrame]:
    """Create sample stock data for screening demonstration."""
    
    # Indian stock sectors
    SECTORS = ['IT', 'Banking', 'Pharma', 'Auto', 'FMCG', 'Energy', 'Metals', 'Realty']
    SECTOR_STOCKS = {
        'IT': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTI', 'COFORGE'],
        'Banking': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK'],
        'Pharma': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON'],
        'Auto': ['MARUTI', 'M&M', 'TATAMOTORS', 'BAJAJ-AUTO', 'EICHERMOT', 'HEROMOTOCO'],
        'FMCG': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR'],
        'Energy': ['RELIANCE', 'ONGC', 'BPCL', 'IOC', 'NTPC', 'POWERGRID'],
        'Metals': ['TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'COALINDIA'],
        'Realty': ['DLF', 'GODREJPROP', 'OBEROIRLTY', 'PRESTIGE', 'PHOENIXLTD']
    }
    
    stocks_data = {}
    metadata = {}
    
    print(f"📊 Generating sample universe of {num_stocks} stocks...")
    
    stock_list = []
    for sector, stocks in SECTOR_STOCKS.items():
        for stock in stocks:
            stock_list.append((f"{stock}.NS", sector))
            if len(stock_list) >= num_stocks:
                break
        if len(stock_list) >= num_stocks:
            break
    
    dates = pd.date_range("2023-01-01", "2025-12-25", freq="B")
    n_days = len(dates)
    
    for i, (symbol, sector) in enumerate(stock_list):
        # Set unique seed for each stock
        np.random.seed(seed + i)
        
        # Different characteristics for different sectors
        if sector in ['IT', 'Banking', 'FMCG']:
            trend = 0.02  # Strong uptrend
            volatility = 1.5
        elif sector in ['Pharma', 'Energy']:
            trend = 0.01  # Moderate uptrend
            volatility = 2.0
        else:
            trend = 0.0  # Sideways
            volatility = 2.5
        
        # Generate price series
        returns = np.random.randn(n_days) * volatility + trend
        close = 100 * np.exp(np.cumsum(returns / 100))
        
        # Ensure realistic price range
        price_multiplier = np.random.choice([1, 5, 10, 20])  # Different price ranges
        close = close * price_multiplier
        
        # Volume based on market cap tier
        market_cap_cr = np.random.choice([500, 2000, 10000, 50000])  # Market cap in crores
        avg_volume = int(market_cap_cr * 1e5 / close.mean())  # Volume ~ market cap / price
        
        df = pd.DataFrame({
            'date': dates,
            'open': close - np.abs(np.random.randn(n_days) * close * 0.01),
            'high': close + np.abs(np.random.randn(n_days) * close * 0.015),
            'low': close - np.abs(np.random.randn(n_days) * close * 0.015),
            'close': close,
            'volume': np.random.randint(int(avg_volume * 0.5), int(avg_volume * 1.5), n_days),
        })
        df.set_index('date', inplace=True)
        
        stocks_data[symbol] = df
        metadata[symbol] = {
            'sector': sector,
            'market_cap_cr': market_cap_cr,
            'avg_volume': avg_volume
        }
        
        print(f"  ✓ {symbol:<20} {sector:<10} MCap: ₹{market_cap_cr:>6,.0f}Cr  Price: ₹{close[-1]:>8.2f}")
    
    return stocks_data, metadata


def main():
    """Run professional stock screening."""
    
    print("\n" + "=" * 100)
    print("PROFESSIONAL STOCK SCREENING FOR ALGO TRADING")
    print("=" * 100)
    
    # Generate sample universe
    stocks_data, metadata = create_sample_universe(num_stocks=50, seed=42)
    
    # Configure screening criteria
    criteria = ScreeningCriteria(
        min_avg_volume_inr=5_00_00_000,  # ₹5 crore minimum
        min_price=50.0,
        max_price=3000.0,
        min_market_cap_cr=500.0,  # ₹500 crore minimum
        price_above_ma200=True,  # Only uptrending stocks
        min_atr_pct=1.0,
        max_atr_pct=6.0,
        min_sharpe=0.8,
        min_win_rate=0.48,
        max_drawdown_pct=20.0,
        min_trades=5,
        max_stocks_per_sector=2,
        target_portfolio_size=10
    )
    
    # Initialize screener
    screener = StockScreener(criteria)
    
    # Configure strategy and broker
    strategy = MovingAverageCrossStrategy(
        fast_window=10,
        slow_window=50,
        min_separation_pct=0.3,
        use_trend_filter=True
    )
    
    broker_config = BrokerConfig(
        commission_bps=7.0,
        slippage_bps=3.0,
        execution_delay_bars=1
    )
    broker = SimulatedBroker(config=broker_config)
    
    # Define backtest function
    def backtest_stock(df: pd.DataFrame) -> dict:
        """Backtest strategy on a single stock."""
        backtester = Backtester(strategy, broker=broker)
        result = backtester.run(df)
        return {
            'sharpe_ratio': result.metrics['sharpe_ratio'],
            'total_return': result.metrics['total_return'],
            'max_drawdown': result.metrics['max_drawdown'],
            'win_rate': result.metrics['win_rate'],
            'profit_factor': result.metrics['profit_factor'],
            'trades': result.trades
        }
    
    # Run screening
    portfolio = screener.screen(stocks_data, backtest_stock, metadata)
    
    # Print results
    screener.print_screening_summary(portfolio)
    
    # Show sector distribution
    if portfolio:
        print("\n📈 Sector Diversification:")
        sector_dist = {}
        for symbol, _ in portfolio:
            sector = metadata[symbol]['sector']
            sector_dist[sector] = sector_dist.get(sector, 0) + 1
        
        for sector, count in sorted(sector_dist.items(), key=lambda x: -x[1]):
            print(f"  {sector:<15} {count} stocks")
    
    print("\n" + "=" * 100)
    print("SCREENING COMPLETE")
    print("=" * 100)
    print("\n💡 Next Steps:")
    print("  1. Allocate capital equally across selected stocks")
    print("  2. Monitor daily and rebalance monthly")
    print("  3. Re-screen quarterly to refresh portfolio")
    print("  4. Replace underperformers (Sharpe < 0.5 for 3 months)")


if __name__ == "__main__":
    main()
