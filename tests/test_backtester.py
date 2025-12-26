import pandas as pd

from algotrader.core import setup_logging
from algotrader.engine.backtester import Backtester
from algotrader.strategy import MeanReversionStrategy

# Suppress logging during tests
setup_logging(level="CRITICAL")


def test_backtest_runs_and_returns_equity():
    prices = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=30, freq="D"),
            "open": 100 + pd.Series(range(30)),
            "high": 101 + pd.Series(range(30)),
            "low": 99 + pd.Series(range(30)),
            "close": 100 + pd.Series(range(30)).astype(float),
            "volume": 10_000,
        }
    ).set_index("date")

    strategy = MeanReversionStrategy(lookback=5, entry_z=0.5)
    backtester = Backtester(strategy)
    result = backtester.run(prices)

    assert not result.equity_curve.empty
    assert result.metrics["sharpe_ratio"] == result.metrics["sharpe_ratio"]  # not NaN
    assert "total_return" in result.metrics
    assert "max_drawdown" in result.metrics
    assert result.trades >= 0
