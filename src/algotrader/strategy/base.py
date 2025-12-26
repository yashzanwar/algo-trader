from __future__ import annotations

from typing import Protocol
import pandas as pd


class Strategy(Protocol):
    """Interface for strategies that emit position signals aligned to price index.
    
    All strategies must implement:
    - name: str | None - strategy identifier
    - required_columns() -> set[str] - OHLCV columns needed
    - warmup_bars() -> int - minimum bars before valid signals
    - generate_signals(prices) -> pd.Series - produce -1/0/+1 position signals
    """

    name: str | None

    def required_columns(self) -> set[str]:  # pragma: no cover - interface only
        ...

    def warmup_bars(self) -> int:  # pragma: no cover - interface only
        ...

    def generate_signals(self, prices: pd.DataFrame) -> pd.Series:  # pragma: no cover - interface only
        ...
