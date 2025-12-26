"""Core data models and types for the AlgoTrader framework."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class SignalType(Enum):
    """Position signal types."""

    LONG = 1
    FLAT = 0
    SHORT = -1


class OrderSide(Enum):
    """Order side enumeration."""

    BUY = "buy"
    SELL = "sell"


class Bar(BaseModel):
    """OHLCV bar data model with validation."""

    timestamp: datetime
    open: Decimal = Field(gt=0, description="Opening price")
    high: Decimal = Field(gt=0, description="Highest price")
    low: Decimal = Field(gt=0, description="Lowest price")
    close: Decimal = Field(gt=0, description="Closing price")
    volume: Decimal = Field(ge=0, description="Trading volume")

    @field_validator("high")
    @classmethod
    def validate_high(cls, v: Decimal, info) -> Decimal:
        """Ensure high >= low, open, close."""
        values = info.data
        if "low" in values and v < values["low"]:
            raise ValueError("high must be >= low")
        if "open" in values and v < values["open"]:
            raise ValueError("high must be >= open")
        if "close" in values and v < values["close"]:
            raise ValueError("high must be >= close")
        return v

    @field_validator("low")
    @classmethod
    def validate_low(cls, v: Decimal, info) -> Decimal:
        """Ensure low <= open, close."""
        values = info.data
        if "open" in values and v > values["open"]:
            raise ValueError("low must be <= open")
        if "close" in values and v > values["close"]:
            raise ValueError("low must be <= close")
        return v

    model_config = {"frozen": True}


class Position(BaseModel):
    """Position information."""

    size: float = Field(description="Position size (negative for short)")
    entry_price: float | None = Field(default=None, description="Average entry price")
    timestamp: datetime | None = Field(default=None, description="Position timestamp")

    model_config = {"frozen": True}


class Signal(BaseModel):
    """Trading signal with metadata."""

    timestamp: datetime
    value: Literal[-1, 0, 1] = Field(description="Signal value: -1 (short), 0 (flat), 1 (long)")
    strength: float | None = Field(default=None, ge=0, le=1, description="Signal strength/confidence")
    metadata: dict[str, float | str] | None = Field(default=None, description="Additional signal metadata")

    model_config = {"frozen": True}


class PerformanceMetrics(BaseModel):
    """Performance metrics with validation."""

    sharpe_ratio: float
    sortino_ratio: float | None = None
    max_drawdown: float | None = Field(default=None, ge=0, le=1)
    total_return: float
    annual_return: float | None = None
    win_rate: float | None = Field(default=None, ge=0, le=1)
    profit_factor: float | None = Field(default=None, ge=0)
    num_trades: int = Field(ge=0)

    model_config = {"frozen": True}
