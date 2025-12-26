"""Strategy module: interface and concrete trading strategies."""

from algotrader.strategy.base import Strategy
from algotrader.strategy.mean_reversion import MeanReversionStrategy
from algotrader.strategy.moving_average import MovingAverageCrossStrategy

__all__ = [
    "Strategy",
    "MeanReversionStrategy",
    "MovingAverageCrossStrategy",
]
