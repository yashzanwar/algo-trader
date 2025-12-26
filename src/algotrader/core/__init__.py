"""Core module for shared types, config, exceptions, and logging."""

from algotrader.core.config import (
    BacktestConfig,
    BrokerConfig,
    DataSourceConfig,
    RiskConfig,
    StrategyConfig,
)
from algotrader.core.exceptions import (
    AlgoTraderError,
    ConfigurationError,
    DataError,
    InsufficientDataError,
    StrategyError,
    ValidationError,
)
from algotrader.core.logging import get_logger, setup_logging
from algotrader.core.types import (
    Bar,
    OrderSide,
    PerformanceMetrics,
    Position,
    Signal,
    SignalType,
)

__all__ = [
    # Config
    "BacktestConfig",
    "BrokerConfig",
    "DataSourceConfig",
    "RiskConfig",
    "StrategyConfig",
    # Exceptions
    "AlgoTraderError",
    "ConfigurationError",
    "DataError",
    "InsufficientDataError",
    "StrategyError",
    "ValidationError",
    # Logging
    "get_logger",
    "setup_logging",
    # Types
    "Bar",
    "OrderSide",
    "PerformanceMetrics",
    "Position",
    "Signal",
    "SignalType",
]
