"""Real-time signal monitoring and detection."""

from __future__ import annotations

import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from typing import Protocol, Callable

from algotrader.core import get_logger

logger = get_logger(__name__)


@dataclass
class SignalEvent:
    """A trading signal event to be notified."""
    
    symbol: str
    timestamp: datetime
    signal_type: str  # 'BUY', 'SELL', 'EXIT'
    price: float
    strategy: str
    reason: str
    metadata: dict | None = None
    
    def __str__(self) -> str:
        return (
            f"{self.signal_type} signal for {self.symbol} @ ₹{self.price:.2f}\n"
            f"Strategy: {self.strategy}\n"
            f"Reason: {self.reason}\n"
            f"Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )


class SignalMonitor:
    """Monitor stocks for trading signals in real-time.
    
    Checks for signal changes and triggers notifications when:
    - New BUY signal (was 0 or -1, now +1) - only if NO position
    - New SELL signal (was 0 or +1, now -1) - not implemented yet
    - EXIT signal (was +1 or -1, now 0) - only if HAS position
    
    Args:
        strategy: Strategy instance to generate signals
        notifiers: List of notifier instances to send alerts
        symbols: List of symbols to monitor
        position_manager: Optional PositionManager to track positions
    """
    
    def __init__(
        self,
        strategy,
        notifiers: list,
        symbols: list[str] | None = None,
        position_manager=None
    ):
        self.strategy = strategy
        self.notifiers = notifiers
        self.symbols = symbols or []
        self.position_manager = position_manager
        
        # Track previous signals to detect changes
        self.previous_signals = {}
        
        logger.info(
            f"SignalMonitor initialized: strategy={strategy.name}, "
            f"symbols={len(self.symbols)}, notifiers={len(self.notifiers)}"
        )
    
    def check_for_signals(
        self,
        symbol: str,
        latest_data: pd.DataFrame
    ) -> SignalEvent | None:
        """Check if new signal has been generated.
        
        Position-aware logic:
        - If NO position: only notify BUY signals
        - If HAS position: only notify EXIT signals
        
        Args:
            symbol: Stock symbol
            latest_data: Latest OHLCV data (must include enough history for strategy)
            
        Returns:
            SignalEvent if signal changed, None otherwise
        """
        # Check if we have a position
        has_position = False
        if self.position_manager:
            has_position = self.position_manager.has_position(symbol)
        
        # Generate signals
        signals = self.strategy.generate_signals(latest_data)
        
        # Get current signal (latest bar)
        current_signal = signals.iloc[-1]
        previous_signal = self.previous_signals.get(symbol, 0)
        
        # Detect signal change
        if current_signal != previous_signal:
            # Determine signal type
            if current_signal == 1:
                signal_type = "BUY"
                reason = self._get_buy_reason(latest_data)
                
                # Skip BUY if we already have a position
                if has_position:
                    logger.debug(f"Skipping BUY for {symbol} - already have position")
                    self.previous_signals[symbol] = current_signal
                    return None
                    
            elif current_signal == -1:
                signal_type = "SELL"
                reason = self._get_sell_reason(latest_data)
                
                # We don't use SELL signals currently (only EXIT)
                # Could be used for short selling in future
                logger.debug(f"SELL signal for {symbol} - not implemented")
                self.previous_signals[symbol] = current_signal
                return None
                
            else:
                signal_type = "EXIT"
                reason = "Position closed - MAs converged"
                
                # Skip EXIT if we don't have a position
                if not has_position:
                    logger.debug(f"Skipping EXIT for {symbol} - no position")
                    self.previous_signals[symbol] = current_signal
                    return None
            
            # Create event
            event = SignalEvent(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type=signal_type,
                price=latest_data['close'].iloc[-1],
                strategy=self.strategy.name,
                reason=reason,
                metadata={
                    'previous_signal': int(previous_signal),
                    'current_signal': int(current_signal),
                    'has_position': has_position
                }
            )
            
            # Update tracking
            self.previous_signals[symbol] = current_signal
            
            logger.info(f"Signal detected: {symbol} {signal_type} @ ₹{event.price:.2f}")
            return event
        
        return None
    
    def _get_buy_reason(self, data: pd.DataFrame) -> str:
        """Generate human-readable buy reason."""
        close = data['close'].iloc[-1]
        
        # Check if it's a MA strategy
        if hasattr(self.strategy, 'fast_window'):
            fast_ma = data['close'].rolling(self.strategy.fast_window).mean().iloc[-1]
            slow_ma = data['close'].rolling(self.strategy.slow_window).mean().iloc[-1]
            return f"Golden Cross: {self.strategy.fast_window}-MA (₹{fast_ma:.2f}) crossed above {self.strategy.slow_window}-MA (₹{slow_ma:.2f})"
        
        return "Buy signal generated"
    
    def _get_sell_reason(self, data: pd.DataFrame) -> str:
        """Generate human-readable sell reason."""
        close = data['close'].iloc[-1]
        
        # Check if it's a MA strategy
        if hasattr(self.strategy, 'fast_window'):
            fast_ma = data['close'].rolling(self.strategy.fast_window).mean().iloc[-1]
            slow_ma = data['close'].rolling(self.strategy.slow_window).mean().iloc[-1]
            return f"Death Cross: {self.strategy.fast_window}-MA (₹{fast_ma:.2f}) crossed below {self.strategy.slow_window}-MA (₹{slow_ma:.2f})"
        
        return "Sell signal generated"
    
    def notify(self, event: SignalEvent):
        """Send notification through all configured notifiers.
        
        Args:
            event: Signal event to notify
        """
        logger.info(f"Sending notifications for {event.symbol} {event.signal_type}...")
        
        for notifier in self.notifiers:
            try:
                notifier.send(event)
            except Exception as e:
                logger.error(f"Notifier {notifier.__class__.__name__} failed: {e}")
    
    def scan_and_notify(self, stocks_data: dict[str, pd.DataFrame]):
        """Scan all stocks and send notifications for new signals.
        
        Args:
            stocks_data: Dict of {symbol: OHLCV DataFrame}
        """
        logger.info(f"Scanning {len(stocks_data)} stocks for signals...")
        
        events = []
        for symbol, data in stocks_data.items():
            event = self.check_for_signals(symbol, data)
            if event:
                events.append(event)
                self.notify(event)
        
        if events:
            logger.info(f"Found {len(events)} new signals")
        else:
            logger.debug("No new signals detected")
        
        return events
