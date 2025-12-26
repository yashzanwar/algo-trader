"""AlgoTrader framework package - Professional algorithmic trading research framework.

Key modules:
- core: Shared types, config, exceptions, logging
- data: Data loading and validation
- strategy: Trading strategy interfaces and implementations
- execution: Broker simulation and order execution
- risk: Position sizing and risk management
- metrics: Performance analysis and reporting
- engine: Backtesting orchestration
"""

__version__ = "0.1.0"

__all__ = [
    "core",
    "data",
    "strategy",
    "engine",
    "execution",
    "risk",
    "metrics",
    "runner",
]
