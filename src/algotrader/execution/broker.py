from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from algotrader.core import BrokerConfig, get_logger

logger = get_logger(__name__)


class Broker(ABC):
    """Abstract base class for order execution and fill simulation.
    
    Brokers handle:
    - Order execution with realistic slippage/commission
    - Position tracking
    - Fill simulation based on market data
    """

    @abstractmethod
    def execute(
        self,
        prices: pd.DataFrame,
        target_positions: pd.Series,
    ) -> tuple[pd.Series, pd.Series]:
        """Execute trades to reach target positions.
        
        Args:
            prices: OHLCV price data
            target_positions: Desired position sizes
            
        Returns:
            Tuple of (filled_positions, transaction_costs_pct)
            - filled_positions: Series of actual filled positions
            - transaction_costs_pct: Series of costs as percentage of portfolio value
        """
        pass


class SimulatedBroker(Broker):
    """Realistic fill simulation with configurable costs.
    
    Assumes next-bar execution with slippage and commissions.
    
    Args:
        config: Broker configuration with slippage/commission settings
    """

    def __init__(self, config: BrokerConfig | None = None):
        self.config = config or BrokerConfig()
        logger.info(
            f"SimulatedBroker initialized: slippage={self.config.slippage_bps}bps, "
            f"commission={self.config.commission_bps}bps, delay={self.config.execution_delay_bars}bars"
        )

    def execute(
        self,
        prices: pd.DataFrame,
        target_positions: pd.Series,
    ) -> tuple[pd.Series, pd.Series]:
        """Simulate order execution with realistic costs."""
        close = prices["close"]
        
        # Apply execution delay (default: next bar)
        delayed_targets = target_positions.shift(self.config.execution_delay_bars).fillna(0)
        
        # Calculate position changes (trades)
        prev_position = delayed_targets.shift(1).fillna(0)
        trades = delayed_targets - prev_position
        
        # Calculate transaction costs as percentage
        # Cost = (slippage + commission) * |trade_size|
        total_cost_bps = self.config.slippage_bps + self.config.commission_bps
        transaction_costs = (total_cost_bps / 10_000) * trades.abs()
        
        logger.debug(
            f"Executed {trades[trades != 0].count()} trades, "
            f"avg cost: {transaction_costs[trades != 0].mean():.4f}%"
        )
        
        return delayed_targets.fillna(0).rename("position"), transaction_costs.rename("costs")
