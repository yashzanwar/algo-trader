import pandas as pd
import pytest

from algotrader.core import setup_logging
from algotrader.strategy import MovingAverageCrossStrategy

# Suppress logging during tests
setup_logging(level="CRITICAL")


def test_moving_average_crossover_signals_raise_on_invalid_windows():
    with pytest.raises(ValueError):
        MovingAverageCrossStrategy(fast_window=5, slow_window=5)
    with pytest.raises(ValueError):
        MovingAverageCrossStrategy(fast_window=0, slow_window=5)


def test_moving_average_crossover_emits_buy_and_sell_signals():
    prices = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=12, freq="D"),
            "close": [10, 10, 10, 10, 30, 30, 30, 30, 5, 5, 5, 5],
        }
    ).set_index("date")

    strategy = MovingAverageCrossStrategy(fast_window=2, slow_window=4)
    signals = strategy.generate_signals(prices)

    # Golden cross: fast MA moves above slow MA around index 4
    assert signals.iloc[4] == 1
    # Death cross: fast MA falls back below slow MA around index 7
    assert signals.iloc[7] == -1
    # No spurious signals elsewhere
    assert signals.sum() == 0
