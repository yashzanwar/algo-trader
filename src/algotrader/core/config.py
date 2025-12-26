"""Configuration models for the AlgoTrader framework."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class DataSourceConfig(BaseModel):
    """Configuration for data sources."""

    source_type: Literal["csv", "api", "database"] = "csv"
    path: Path | None = None
    datetime_column: str = "date"
    required_columns: set[str] = {"open", "high", "low", "close", "volume"}

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Path | None, info) -> Path | None:
        """Validate path exists for file-based sources."""
        values = info.data
        if values.get("source_type") == "csv" and v is not None and not v.exists():
            raise ValueError(f"CSV file does not exist: {v}")
        return v


class BrokerConfig(BaseModel):
    """Configuration for broker/execution."""

    slippage_bps: float = Field(default=0.0, ge=0, le=1000, description="Slippage in basis points")
    commission_bps: float = Field(default=0.0, ge=0, le=1000, description="Commission in basis points")
    execution_delay_bars: int = Field(default=1, ge=0, description="Execution delay in bars")

    model_config = {"frozen": True}


class RiskConfig(BaseModel):
    """Configuration for risk management."""

    max_position_size: float = Field(default=1.0, gt=0, description="Maximum absolute position size")
    max_leverage: float = Field(default=1.0, gt=0, le=10, description="Maximum leverage")
    stop_loss_pct: float | None = Field(default=None, ge=0, le=1, description="Stop loss percentage")
    take_profit_pct: float | None = Field(default=None, ge=0, description="Take profit percentage")

    model_config = {"frozen": True}


class BacktestConfig(BaseModel):
    """Configuration for backtesting."""

    initial_capital: float = Field(default=100_000.0, gt=0)
    data_source: DataSourceConfig
    broker: BrokerConfig = Field(default_factory=BrokerConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    benchmark: str | None = Field(default=None, description="Benchmark symbol for comparison")

    model_config = {"frozen": True}


class StrategyConfig(BaseModel):
    """Base configuration for strategies."""

    name: str
    parameters: dict[str, int | float | str] = Field(default_factory=dict)

    model_config = {"frozen": True}
