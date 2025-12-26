from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from algotrader.core import PerformanceMetrics, get_logger

logger = get_logger(__name__)


class MetricsCalculator(ABC):
    """Abstract base class for performance metrics calculation."""

    @abstractmethod
    def calculate(
        self,
        positions: pd.Series,
        prices: pd.Series,
        equity_curve: pd.Series,
    ) -> PerformanceMetrics:
        """Calculate performance metrics.
        
        Args:
            positions: Position series
            prices: Price series
            equity_curve: Equity curve series
            
        Returns:
            Performance metrics
        """
        pass


class StandardMetricsCalculator(MetricsCalculator):
    """Standard performance metrics calculator.
    
    Calculates:
    - Sharpe ratio
    - Sortino ratio
    - Maximum drawdown
    - Total and annual returns
    - Win rate and profit factor
    """

    def __init__(self, periods_per_year: int = 252, risk_free_rate: float = 0.0):
        self.periods_per_year = periods_per_year
        self.risk_free_rate = risk_free_rate
        logger.info(
            f"StandardMetricsCalculator initialized: periods/year={periods_per_year}, "
            f"risk_free_rate={risk_free_rate}"
        )

    def calculate(
        self,
        positions: pd.Series,
        prices: pd.Series,
        equity_curve: pd.Series,
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics."""
        returns = self._calculate_returns(positions, prices)
        
        sharpe = self._sharpe_ratio(returns)
        sortino = self._sortino_ratio(returns)
        max_dd = self._max_drawdown(equity_curve)
        total_ret = self._total_return(equity_curve)
        annual_ret = self._annualized_return(equity_curve)
        trades = self._count_trades(positions)
        win_rate = self._win_rate(returns)
        profit_factor = self._profit_factor(returns)
        
        logger.info(
            f"Metrics calculated: Sharpe={sharpe:.2f}, Sortino={sortino:.2f}, "
            f"MaxDD={max_dd:.2%}, Return={total_ret:.2%}"
        )
        
        return PerformanceMetrics(
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            total_return=total_ret,
            annual_return=annual_ret,
            win_rate=win_rate,
            profit_factor=profit_factor,
            num_trades=trades,
        )

    def _calculate_returns(self, positions: pd.Series, prices: pd.Series) -> pd.Series:
        """Calculate strategy returns."""
        price_returns = prices.pct_change().fillna(0)
        strategy_returns = positions.shift(1).fillna(0) * price_returns
        return strategy_returns

    def _sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate annualized Sharpe ratio."""
        excess_returns = returns - (self.risk_free_rate / self.periods_per_year)
        mean = excess_returns.mean() * self.periods_per_year
        vol = excess_returns.std(ddof=1) * np.sqrt(self.periods_per_year)
        return float(mean / vol) if vol > 0 else 0.0

    def _sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate annualized Sortino ratio (downside deviation)."""
        excess_returns = returns - (self.risk_free_rate / self.periods_per_year)
        mean = excess_returns.mean() * self.periods_per_year
        downside = excess_returns[excess_returns < 0].std(ddof=1) * np.sqrt(self.periods_per_year)
        return float(mean / downside) if downside > 0 else 0.0

    def _max_drawdown(self, equity: pd.Series) -> float:
        """Calculate maximum drawdown."""
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max
        return float(abs(drawdown.min()))

    def _total_return(self, equity: pd.Series) -> float:
        """Calculate total return."""
        return float((equity.iloc[-1] / equity.iloc[0]) - 1)

    def _annualized_return(self, equity: pd.Series) -> float:
        """Calculate annualized return."""
        total_ret = self._total_return(equity)
        num_periods = len(equity)
        years = num_periods / self.periods_per_year
        return float((1 + total_ret) ** (1 / years) - 1) if years > 0 else 0.0

    def _count_trades(self, positions: pd.Series) -> int:
        """Count number of position changes (trades)."""
        position_changes = positions.diff().fillna(0)
        return int((position_changes != 0).sum())

    def _win_rate(self, returns: pd.Series) -> float:
        """Calculate win rate (percentage of profitable periods)."""
        winning_periods = (returns > 0).sum()
        total_periods = (returns != 0).sum()
        return float(winning_periods / total_periods) if total_periods > 0 else 0.0

    def _profit_factor(self, returns: pd.Series) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = returns[returns > 0].sum()
        gross_loss = abs(returns[returns < 0].sum())
        return float(gross_profit / gross_loss) if gross_loss > 0 else 0.0


# Legacy function for backward compatibility
def compute_equity_curve(positions: pd.Series, prices: pd.Series) -> dict:
    """Compute equity curve and basic metrics (legacy interface).
    
    Args:
        positions: Position series
        prices: Price series
        
    Returns:
        Dict with equity_curve, returns, and sharpe
    """
    calculator = StandardMetricsCalculator()
    price_returns = prices.pct_change().fillna(0)
    strategy_returns = positions.shift(1).fillna(0) * price_returns
    equity = (1 + strategy_returns).cumprod()
    
    metrics = calculator.calculate(positions, prices, equity)
    
    return {
        "equity_curve": equity.rename("equity"),
        "returns": strategy_returns.rename("returns"),
        "sharpe": metrics.sharpe_ratio,
    }
