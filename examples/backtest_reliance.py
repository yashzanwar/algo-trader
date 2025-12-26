#!/usr/bin/env python3
"""Example: Backtest a strategy on Reliance stock."""

from algotrader.core import setup_logging
from algotrader.data.yahoo_finance import YahooFinanceDataSource
from algotrader.engine.backtester import Backtester
from algotrader.strategy import MovingAverageCrossStrategy

# Setup logging to see what's happening
setup_logging(level="INFO")

# Fetch Reliance data from Yahoo Finance
# Note: Use .NS for NSE (National Stock Exchange) or .BO for BSE (Bombay Stock Exchange)
print("Fetching Reliance data from Yahoo Finance...")
data_source = YahooFinanceDataSource(
    symbol="RELIANCE.NS",  # Reliance on NSE
    start_date="2023-01-01",
    end_date="2024-12-25",
)

prices = data_source.load()

print(f"\nLoaded {len(prices)} days of data")
print(f"Date range: {prices.index[0].date()} to {prices.index[-1].date()}")
print(f"\nFirst few rows:")
print(prices.head())

# Create a strategy (Moving Average Crossover: 5-day vs 20-day)
strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=20)

# Run backtest
print("\n" + "=" * 50)
print("Running backtest on RELIANCE.NS...")
print("=" * 50)

backtester = Backtester(strategy)
result = backtester.run(prices)

# Print results
print("\n" + "=" * 50)
print("BACKTEST RESULTS - RELIANCE.NS")
print("=" * 50)
print(f"Strategy:          {strategy.name}")
print(f"Period:            {prices.index[0].date()} to {prices.index[-1].date()}")
print(f"Total Days:        {len(prices)}")
print("-" * 50)
print(f"Sharpe Ratio:      {result.metrics['sharpe_ratio']:>10.2f}")
print(f"Sortino Ratio:     {result.metrics['sortino_ratio']:>10.2f}")
print(f"Total Return:      {result.metrics['total_return']:>10.2%}")
print(f"Annual Return:     {result.metrics['annual_return']:>10.2%}")
print(f"Max Drawdown:      {result.metrics['max_drawdown']:>10.2%}")
print(f"Win Rate:          {result.metrics['win_rate']:>10.2%}")
print(f"Profit Factor:     {result.metrics['profit_factor']:>10.2f}")
print(f"Number of Trades:  {result.trades:>10}")
print(f"Final Equity:      {result.equity_curve.iloc[-1]:>10.4f}")
print("=" * 50)

# Show recent performance
print("\nRecent Equity Curve (last 10 days):")
print(result.equity_curve.tail(10))
