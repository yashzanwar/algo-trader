from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from algotrader.core import RiskConfig, get_logger

logger = get_logger(__name__)


class RiskManager(ABC):
    """Abstract base class for position sizing and risk management.
    
    Risk managers:
    - Size positions based on risk parameters
    - Apply position limits and leverage constraints
    - Enforce stop-loss and take-profit rules
    """

    @abstractmethod
    def size_positions(
        self,
        signals: pd.Series,
        prices: pd.DataFrame | None = None,
        current_positions: pd.Series | None = None,
    ) -> pd.Series:
        """Size positions based on signals and risk constraints.
        
        Args:
            signals: Raw strategy signals (-1, 0, 1)
            prices: Optional price data for adaptive sizing
            current_positions: Optional current position data
            
        Returns:
            Sized target positions
        """
        pass


class BasicRiskManager(RiskManager):
    """Simple risk manager with position limits and optional stops.
    
    Args:
        config: Risk configuration with limits and parameters
    """

    def __init__(self, config: RiskConfig | None = None):
        self.config = config or RiskConfig()
        logger.info(
            f"BasicRiskManager initialized: max_position={self.config.max_position_size}, "
            f"max_leverage={self.config.max_leverage}"
        )

    def size_positions(
        self,
        signals: pd.Series,
        prices: pd.DataFrame | None = None,
        current_positions: pd.Series | None = None,
    ) -> pd.Series:
        """Apply position sizing with risk limits."""
        # Apply position size limit
        sized = signals.clip(
            lower=-self.config.max_position_size,
            upper=self.config.max_position_size,
        )
        
        # Apply leverage constraint (simple scaling)
        if self.config.max_leverage < 1.0:
            sized = sized * self.config.max_leverage
        
        # TODO: Implement stop-loss and take-profit logic when prices provided
        # This would require tracking entry prices and unrealized PnL
        
        logger.debug(
            f"Sized positions: {(sized != 0).sum()} non-zero positions, "
            f"max abs: {sized.abs().max():.2f}"
        )
        
        return sized.rename("target_position")
