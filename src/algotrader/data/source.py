from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from algotrader.core import DataError, get_logger

logger = get_logger(__name__)


class DataSource(ABC):
    """Abstract base class for loading price data with a datetime index.
    
    All data sources must:
    - Return a DataFrame with datetime index
    - Include OHLCV columns at minimum
    - Handle data validation and cleaning
    """

    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Load and return validated price data.
        
        Returns:
            DataFrame with datetime index and OHLCV columns
            
        Raises:
            DataError: If data loading or validation fails
        """
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean the loaded data.
        
        Args:
            df: Raw dataframe to validate
            
        Returns:
            Validated and cleaned dataframe
            
        Raises:
            DataError: If validation fails
        """
        pass


class CsvDataSource(DataSource):
    """CSV file-based data loader with validation.
    
    Args:
        path: Path to CSV file
        datetime_column: Column name containing datetime data
        required_columns: Set of required column names
    """

    def __init__(
        self,
        path: Path,
        datetime_column: str = "date",
        required_columns: set[str] | None = None,
    ):
        self.path = Path(path)
        self.datetime_column = datetime_column
        self.required_columns = required_columns or {"open", "high", "low", "close", "volume"}
        
        if not self.path.exists():
            raise DataError(f"CSV file not found: {self.path}")
        
        logger.info(f"Initialized CsvDataSource: {self.path}")

    def load(self) -> pd.DataFrame:
        """Load CSV data with validation."""
        try:
            logger.debug(f"Loading CSV from {self.path}")
            df = pd.read_csv(self.path)
            df = self.validate(df)
            logger.info(f"Loaded {len(df)} bars from {self.path}")
            return df
        except Exception as e:
            raise DataError(f"Failed to load CSV from {self.path}: {e}") from e

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and prepare CSV data."""
        # Check datetime column
        if self.datetime_column not in df.columns:
            raise DataError(
                f"Missing datetime column '{self.datetime_column}' in {self.path}. "
                f"Available columns: {list(df.columns)}"
            )
        
        # Parse and set datetime index
        df[self.datetime_column] = pd.to_datetime(df[self.datetime_column])
        df = df.set_index(self.datetime_column).sort_index()
        
        # Check required columns
        missing = self.required_columns.difference(df.columns)
        if missing:
            raise DataError(
                f"Missing required columns: {sorted(missing)}. "
                f"Available: {sorted(df.columns)}"
            )
        
        # Validate OHLC relationships
        if not (df["high"] >= df["low"]).all():
            raise DataError("Data validation failed: high < low detected")
        if not (df["high"] >= df["close"]).all():
            raise DataError("Data validation failed: high < close detected")
        if not (df["low"] <= df["close"]).all():
            raise DataError("Data validation failed: low > close detected")
        
        # Check for NaN values
        if df[list(self.required_columns)].isnull().any().any():
            raise DataError("Data contains NaN values in required columns")
        
        return df
