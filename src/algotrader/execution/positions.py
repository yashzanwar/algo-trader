"""Position management for tracking manual trades."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class Position:
    """Represents a trading position."""
    
    def __init__(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        entry_time: Optional[datetime] = None
    ):
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_time = entry_time or datetime.now()
    
    def current_pnl(self, current_price: float) -> Dict[str, float]:
        """Calculate current P&L."""
        pnl = (current_price - self.entry_price) * self.quantity
        pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100
        
        return {
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'current_price': current_price,
            'entry_price': self.entry_price
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create from dictionary."""
        return cls(
            symbol=data['symbol'],
            quantity=data['quantity'],
            entry_price=data['entry_price'],
            entry_time=datetime.fromisoformat(data['entry_time'])
        )


class PositionManager:
    """Manages trading positions with file persistence."""
    
    def __init__(self, positions_file: str = "positions.json"):
        """
        Initialize position manager.
        
        Args:
            positions_file: Path to positions JSON file
        """
        self.positions_file = Path(positions_file)
        self.positions: Dict[str, Position] = {}
        self._load_positions()
    
    def _load_positions(self):
        """Load positions from file."""
        if self.positions_file.exists():
            try:
                with open(self.positions_file, 'r') as f:
                    data = json.load(f)
                    self.positions = {
                        symbol: Position.from_dict(pos_data)
                        for symbol, pos_data in data.items()
                    }
                logger.info(f"Loaded {len(self.positions)} positions from {self.positions_file}")
            except Exception as e:
                logger.error(f"Error loading positions: {e}")
                self.positions = {}
        else:
            logger.info("No existing positions file found")
    
    def _save_positions(self):
        """Save positions to file."""
        try:
            data = {
                symbol: pos.to_dict()
                for symbol, pos in self.positions.items()
            }
            with open(self.positions_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.positions)} positions to {self.positions_file}")
        except Exception as e:
            logger.error(f"Error saving positions: {e}")
    
    def add_position(
        self,
        symbol: str,
        quantity: float,
        entry_price: float
    ) -> Position:
        """
        Add a new position.
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            entry_price: Entry price per share
        
        Returns:
            Created Position object
        """
        if symbol in self.positions:
            # Update existing position (average down/up)
            existing = self.positions[symbol]
            total_qty = existing.quantity + quantity
            avg_price = (
                (existing.quantity * existing.entry_price) +
                (quantity * entry_price)
            ) / total_qty
            
            self.positions[symbol] = Position(symbol, total_qty, avg_price)
            logger.info(f"Updated position: {symbol} - {total_qty} shares @ ₹{avg_price:.2f}")
        else:
            self.positions[symbol] = Position(symbol, quantity, entry_price)
            logger.info(f"Added position: {symbol} - {quantity} shares @ ₹{entry_price:.2f}")
        
        self._save_positions()
        return self.positions[symbol]
    
    def remove_position(self, symbol: str) -> bool:
        """
        Remove a position.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            True if removed, False if not found
        """
        if symbol in self.positions:
            del self.positions[symbol]
            self._save_positions()
            logger.info(f"Removed position: {symbol}")
            return True
        return False
    
    def has_position(self, symbol: str) -> bool:
        """Check if we have a position in this symbol."""
        return symbol in self.positions
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol."""
        return self.positions.get(symbol)
    
    def list_positions(self) -> List[Position]:
        """Get all positions."""
        return list(self.positions.values())
    
    def clear_all(self):
        """Clear all positions."""
        self.positions = {}
        self._save_positions()
        logger.info("Cleared all positions")
