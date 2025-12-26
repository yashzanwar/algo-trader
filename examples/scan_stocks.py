#!/usr/bin/env python3
"""Example: Scan multiple Indian stocks to find best performers."""

from algotrader.core import setup_logging
from algotrader.scanner import INDIAN_LARGECAP, INDIAN_NIFTY50, StockScanner
from algotrader.strategy import MovingAverageCrossStrategy

# Setup logging
setup_logging(level="WARNING")  # Less verbose for scanning

print("=" * 90)
print("STOCK SCANNER - Finding Best Stocks for MA Crossover Strategy")
print("=" * 90)

# Define strategy
strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=20)

# Option 1: Scan top 5 large-cap stocks (faster)
print("\n1. Scanning Indian Large-Cap Stocks (5 stocks)...")
scanner = StockScanner(
    symbols=INDIAN_LARGECAP,
    strategy=strategy,
    start_date="2023-01-01",
    end_date="2024-12-25",
)

results = scanner.scan()
scanner.print_results(results, top_n=5)

# Option 2: Scan top 20 Nifty50 stocks (uncomment to run)
# print("\n2. Scanning Nifty 50 Stocks (top 20)...")
# scanner_nifty = StockScanner(
#     symbols=INDIAN_NIFTY50,
#     strategy=strategy,
#     start_date="2023-01-01",
#     end_date="2024-12-25",
# )
# 
# results_nifty = scanner_nifty.scan()
# scanner_nifty.print_results(results_nifty, top_n=10)

print("\nTip: Modify the symbols list or strategy parameters to customize your scan!")
print("Available stock lists: INDIAN_NIFTY50, INDIAN_LARGECAP, US_TECH, US_SP500_TOP10")
