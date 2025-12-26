"""Stock screening and scanning utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from algotrader.core import get_logger
from algotrader.data.yahoo_finance import YahooFinanceDataSource
from algotrader.engine.backtester import Backtester, BacktestResult
from algotrader.strategy import Strategy

logger = get_logger(__name__)


@dataclass
class ScreeningResult:
    """Results from stock screening."""
    
    symbol: str
    backtest_result: BacktestResult | None = None
    error: str | None = None
    
    @property
    def sharpe(self) -> float:
        if self.backtest_result:
            return self.backtest_result.metrics["sharpe_ratio"]
        return 0.0
    
    @property
    def total_return(self) -> float:
        if self.backtest_result:
            return self.backtest_result.metrics["total_return"]
        return 0.0


class StockScanner:
    """Scan multiple stocks with a strategy to find best performers.
    
    Examples:
        >>> # Indian large-cap stocks
        >>> symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
        >>> scanner = StockScanner(
        ...     symbols=symbols,
        ...     strategy=MovingAverageCrossStrategy(5, 20),
        ...     start_date="2023-01-01",
        ...     end_date="2024-01-01"
        ... )
        >>> results = scanner.scan()
        >>> scanner.print_results(results)
    """

    def __init__(
        self,
        symbols: list[str],
        strategy: Strategy,
        start_date: str,
        end_date: str | None = None,
        min_data_points: int = 100,
    ):
        self.symbols = symbols
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.min_data_points = min_data_points
        
        logger.info(
            f"StockScanner initialized: {len(symbols)} symbols, "
            f"strategy={strategy.name}"
        )

    def scan(self) -> list[ScreeningResult]:
        """Run backtest on all symbols and return ranked results."""
        results = []
        
        for symbol in self.symbols:
            logger.info(f"Scanning {symbol}...")
            result = self._scan_symbol(symbol)
            results.append(result)
        
        # Sort by Sharpe ratio (best first)
        results.sort(key=lambda r: r.sharpe, reverse=True)
        
        logger.info(f"Scan complete: {len(results)} symbols processed")
        return results

    def _scan_symbol(self, symbol: str) -> ScreeningResult:
        """Backtest a single symbol."""
        try:
            # Fetch data
            data_source = YahooFinanceDataSource(
                symbol=symbol,
                start_date=self.start_date,
                end_date=self.end_date,
            )
            prices = data_source.load()
            
            # Check minimum data
            if len(prices) < self.min_data_points:
                return ScreeningResult(
                    symbol=symbol,
                    error=f"Insufficient data: {len(prices)} bars"
                )
            
            # Run backtest
            backtester = Backtester(strategy=self.strategy)
            result = backtester.run(prices)
            
            return ScreeningResult(symbol=symbol, backtest_result=result)
            
        except Exception as e:
            logger.warning(f"Failed to scan {symbol}: {e}")
            return ScreeningResult(symbol=symbol, error=str(e))

    def print_results(self, results: list[ScreeningResult], top_n: int = 10) -> None:
        """Print formatted screening results."""
        print("\n" + "=" * 90)
        print(f"STOCK SCREENING RESULTS - Top {top_n}")
        print("=" * 90)
        print(
            f"{'Rank':<6} {'Symbol':<15} {'Sharpe':<10} {'Return':<12} "
            f"{'MaxDD':<10} {'Trades':<8} {'Status'}"
        )
        print("-" * 90)
        
        for i, result in enumerate(results[:top_n], 1):
            if result.backtest_result:
                metrics = result.backtest_result.metrics
                print(
                    f"{i:<6} {result.symbol:<15} "
                    f"{metrics['sharpe_ratio']:<10.2f} "
                    f"{metrics['total_return']:<12.2%} "
                    f"{metrics['max_drawdown']:<10.2%} "
                    f"{result.backtest_result.trades:<8} "
                    f"✓"
                )
            else:
                print(
                    f"{i:<6} {result.symbol:<15} "
                    f"{'N/A':<10} {'N/A':<12} {'N/A':<10} {'N/A':<8} "
                    f"✗ {result.error}"
                )
        
        print("=" * 90)
        print()


# Predefined stock lists
INDIAN_NIFTY50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS",
    "ITC.NS", "ASIANPAINT.NS", "LT.NS", "AXISBANK.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "WIPRO.NS",
]

INDIAN_LARGECAP = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
]

US_TECH = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX",
]

US_SP500_TOP10 = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "JNJ",
]
