from __future__ import annotations

import pandas as pd

from algotrader.core import InsufficientDataError, ValidationError, get_logger
from algotrader.execution.broker import Broker, SimulatedBroker
from algotrader.metrics.report import MetricsCalculator, StandardMetricsCalculator
from algotrader.risk.manager import BasicRiskManager, RiskManager
from algotrader.strategy import Strategy

logger = get_logger(__name__)


class BacktestResult:
    """Immutable backtest results with comprehensive metrics.
    
    Attributes:
        equity_curve: Time series of portfolio equity
        positions: Time series of position sizes
        signals: Time series of raw strategy signals
        metrics: Performance metrics
        trades: Number of trades executed
    """

    def __init__(
        self,
        equity_curve: pd.Series,
        positions: pd.Series,
        signals: pd.Series,
        metrics: dict,
        trades: int,
    ):
        self._equity_curve = equity_curve
        self._positions = positions
        self._signals = signals
        self._metrics = metrics
        self._trades = trades

    @property
    def equity_curve(self) -> pd.Series:
        return self._equity_curve

    @property
    def positions(self) -> pd.Series:
        return self._positions

    @property
    def signals(self) -> pd.Series:
        return self._signals

    @property
    def metrics(self) -> dict:
        return self._metrics

    @property
    def trades(self) -> int:
        return self._trades

    def __repr__(self) -> str:
        return (
            f"BacktestResult(trades={self.trades}, "
            f"sharpe={self.metrics.get('sharpe_ratio', 0):.2f}, "
            f"return={self.metrics.get('total_return', 0):.2%})"
        )


class Backtester:
    """Modular backtesting engine with dependency injection.
    
    The backtester orchestrates the interaction between:
    - Strategy: Generates trading signals
    - RiskManager: Sizes positions based on signals
    - Broker: Simulates order execution
    - MetricsCalculator: Computes performance metrics
    
    All components are injected, making the backtester fully extensible
    and testable.
    
    Args:
        strategy: Strategy instance implementing signal generation
        broker: Broker instance for execution simulation
        risk_manager: Risk manager for position sizing
        metrics_calculator: Calculator for performance metrics
    """

    def __init__(
        self,
        strategy: Strategy,
        broker: Broker | None = None,
        risk_manager: RiskManager | None = None,
        metrics_calculator: MetricsCalculator | None = None,
    ) -> None:
        self.strategy = strategy
        self.broker = broker or SimulatedBroker()
        self.risk_manager = risk_manager or BasicRiskManager()
        self.metrics_calculator = metrics_calculator or StandardMetricsCalculator()
        
        logger.info(
            f"Backtester initialized with strategy: {getattr(strategy, 'name', strategy.__class__.__name__)}"
        )

    def run(self, prices: pd.DataFrame) -> BacktestResult:
        """Execute backtest with full validation and logging.
        
        Args:
            prices: OHLCV price data with datetime index
            
        Returns:
            BacktestResult with equity curve, positions, signals, and metrics
            
        Raises:
            ValidationError: If required columns are missing
            InsufficientDataError: If not enough data for strategy warmup
        """
        logger.info(f"Starting backtest with {len(prices)} bars of data")
        
        # Validate required columns
        self._validate_data(prices)
        
        # Generate signals
        logger.debug("Generating strategy signals...")
        signals = self.strategy.generate_signals(prices)
        
        # Apply warmup period
        warmup = self.strategy.warmup_bars()
        if warmup >= len(prices):
            raise InsufficientDataError(
                f"Insufficient data: strategy requires {warmup} warmup bars "
                f"but only {len(prices)} bars available"
            )
        
        if warmup > 0:
            signals = signals.copy()
            signals.iloc[:warmup] = 0
            logger.debug(f"Applied {warmup}-bar warmup period")
        
        # Size positions
        logger.debug("Sizing positions with risk manager...")
        targets = self.risk_manager.size_positions(signals, prices)
        
        # Execute trades
        logger.debug("Executing trades with broker...")
        positions, transaction_costs = self.broker.execute(prices, targets)
        
        # Calculate returns and equity
        returns = prices["close"].pct_change().fillna(0)
        strategy_returns = positions.shift(1).fillna(0) * returns
        
        # Subtract transaction costs from returns
        net_returns = strategy_returns - transaction_costs
        equity_curve = (1 + net_returns).cumprod()
        
        # Calculate metrics
        logger.debug("Computing performance metrics...")
        metrics_obj = self.metrics_calculator.calculate(positions, prices["close"], equity_curve)
        
        # Convert to dict for backward compatibility
        metrics = {
            "sharpe_ratio": metrics_obj.sharpe_ratio,
            "sortino_ratio": metrics_obj.sortino_ratio,
            "max_drawdown": metrics_obj.max_drawdown,
            "total_return": metrics_obj.total_return,
            "annual_return": metrics_obj.annual_return,
            "win_rate": metrics_obj.win_rate,
            "profit_factor": metrics_obj.profit_factor,
        }
        
        result = BacktestResult(
            equity_curve=equity_curve.rename("equity"),
            positions=positions,
            signals=signals,
            metrics=metrics,
            trades=metrics_obj.num_trades,
        )
        
        logger.info(f"Backtest completed: {result}")
        return result

    def _validate_data(self, prices: pd.DataFrame) -> None:
        """Validate price data has required columns."""
        missing = self.strategy.required_columns().difference(prices.columns)
        if missing:
            raise ValidationError(
                f"Missing required price columns for strategy: {sorted(missing)}. "
                f"Available: {sorted(prices.columns)}"
            )
