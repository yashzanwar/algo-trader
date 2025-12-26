"""Yahoo Finance data source for fetching stock data."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

from algotrader.core import DataError, get_logger
from algotrader.data.source import DataSource

logger = get_logger(__name__)


class YahooFinanceDataSource(DataSource):
    """Fetch OHLCV data from Yahoo Finance.
    
    Supports:
    - Individual stocks (e.g., "RELIANCE.NS" for NSE, "AAPL" for NASDAQ)
    - ETFs and indices
    - Automatic data validation
    
    Args:
        symbol: Ticker symbol (use .NS for NSE, .BO for BSE)
        start_date: Start date for data (YYYY-MM-DD or datetime)
        end_date: End date for data (YYYY-MM-DD or datetime)
        interval: Data interval (1d, 1h, 5m, etc.)
        auto_adjust: Adjust OHLC for splits and dividends
    
    Examples:
        >>> # Indian stocks (NSE)
        >>> source = YahooFinanceDataSource("RELIANCE.NS", "2023-01-01", "2024-01-01")
        >>> # US stocks
        >>> source = YahooFinanceDataSource("AAPL", "2023-01-01", "2024-01-01")
    """

    def __init__(
        self,
        symbol: str,
        start_date: str | datetime,
        end_date: str | datetime | None = None,
        interval: str = "1d",
        auto_adjust: bool = True,
    ):
        self.symbol = symbol.upper()
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        self.interval = interval
        self.auto_adjust = auto_adjust
        
        logger.info(
            f"Initialized YahooFinanceDataSource: {self.symbol} "
            f"from {self.start_date} to {self.end_date}"
        )

    def load(self) -> pd.DataFrame:
        """Fetch data from Yahoo Finance with validation."""
        try:
            logger.debug(f"Fetching {self.symbol} data from Yahoo Finance...")
            
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(
                start=self.start_date,
                end=self.end_date,
                interval=self.interval,
                auto_adjust=self.auto_adjust,
            )
            
            if df.empty:
                raise DataError(
                    f"No data returned for {self.symbol}. "
                    "Check symbol format (use .NS for NSE, .BO for BSE)"
                )
            
            # Standardize column names
            df.columns = df.columns.str.lower()
            
            # Validate
            df = self.validate(df)
            
            logger.info(
                f"Loaded {len(df)} bars for {self.symbol} "
                f"({df.index[0].date()} to {df.index[-1].date()})"
            )
            
            return df
            
        except Exception as e:
            raise DataError(f"Failed to fetch {self.symbol} from Yahoo Finance: {e}") from e

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate Yahoo Finance data."""
        # Check required columns
        required = {"open", "high", "low", "close", "volume"}
        missing = required.difference(df.columns)
        if missing:
            raise DataError(f"Missing columns: {missing}")
        
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            raise DataError("Index is not DatetimeIndex")
        
        # Sort by date
        df = df.sort_index()
        
        # Validate OHLC relationships
        if not (df["high"] >= df["low"]).all():
            raise DataError("Data validation failed: high < low")
        if not (df["high"] >= df["close"]).all():
            raise DataError("Data validation failed: high < close")
        if not (df["high"] >= df["open"]).all():
            raise DataError("Data validation failed: high < open")
        if not (df["low"] <= df["close"]).all():
            raise DataError("Data validation failed: low > close")
        if not (df["low"] <= df["open"]).all():
            raise DataError("Data validation failed: low > open")
        
        # Check for NaN
        if df[list(required)].isnull().any().any():
            logger.warning("Found NaN values, forward-filling...")
            df = df.fillna(method="ffill")
        
        # Remove any remaining NaN rows
        df = df.dropna(subset=list(required))
        
        return df

    def save_to_csv(self, path: Path) -> None:
        """Fetch and save data to CSV for offline use."""
        df = self.load()
        df.to_csv(path)
        logger.info(f"Saved {len(df)} bars to {path}")
