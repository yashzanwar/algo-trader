from __future__ import annotations

import argparse
from pathlib import Path

from algotrader.core import setup_logging
from algotrader.data.source import CsvDataSource
from algotrader.engine.backtester import Backtester
from algotrader.strategy import MeanReversionStrategy


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple mean-reversion backtest")
    parser.add_argument("--csv", type=Path, required=True, help="Path to CSV with OHLCV and date column")
    parser.add_argument("--lookback", type=int, default=20, help="Lookback window for z-score")
    parser.add_argument("--entry-z", type=float, default=1.0, help="Entry threshold in z-score units")
    parser.add_argument("--log-level", default="WARNING", help="Logging level")
    args = parser.parse_args()

    # Setup logging
    setup_logging(level=args.log_level)

    # Load data and run backtest
    data = CsvDataSource(path=args.csv).load()
    strategy = MeanReversionStrategy(lookback=args.lookback, entry_z=args.entry_z)
    backtester = Backtester(strategy=strategy)
    result = backtester.run(data)

    # Print results
    print("\n" + "=" * 50)
    print("BACKTEST SUMMARY")
    print("=" * 50)
    print(f"Sharpe Ratio:      {result.metrics['sharpe_ratio']:>8.2f}")
    print(f"Sortino Ratio:     {result.metrics['sortino_ratio']:>8.2f}")
    print(f"Total Return:      {result.metrics['total_return']:>8.2%}")
    print(f"Annual Return:     {result.metrics['annual_return']:>8.2%}")
    print(f"Max Drawdown:      {result.metrics['max_drawdown']:>8.2%}")
    print(f"Win Rate:          {result.metrics['win_rate']:>8.2%}")
    print(f"Profit Factor:     {result.metrics['profit_factor']:>8.2f}")
    print(f"Number of Trades:  {result.trades:>8}")
    print(f"Final Equity:      {result.equity_curve.iloc[-1]:>8.4f}")
    print("=" * 50)
    print("\nLast 5 equity values:")
    print(result.equity_curve.tail())
    print()


if __name__ == "__main__":
    main()
