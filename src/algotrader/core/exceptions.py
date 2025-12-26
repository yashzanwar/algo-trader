"""Custom exceptions for the AlgoTrader framework."""

from __future__ import annotations


class AlgoTraderError(Exception):
    """Base exception for all AlgoTrader errors."""

    pass


class DataError(AlgoTraderError):
    """Raised when there are issues with data loading or validation."""

    pass


class ConfigurationError(AlgoTraderError):
    """Raised when configuration is invalid or incomplete."""

    pass


class StrategyError(AlgoTraderError):
    """Raised when strategy execution encounters an error."""

    pass


class ValidationError(AlgoTraderError):
    """Raised when input validation fails."""

    pass


class InsufficientDataError(DataError):
    """Raised when there is not enough data for the requested operation."""

    pass
