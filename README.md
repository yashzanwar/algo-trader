# AlgoTrader Framework

**Professional-grade Python framework for algorithmic trading research and backtesting.**

Enterprise-ready architecture with dependency injection, comprehensive validation, structured logging, and extensible design patterns. Built for scalability from single-strategy backtests to production-ready multi-strategy portfolios.

## 🏗️ Architecture

### Design Principles
- **Dependency Injection**: All components are injectable and swappable
- **Protocol-Based Interfaces**: ABC/Protocol for every major component
- **Immutability**: Configuration and results are immutable using Pydantic
- **Type Safety**: Comprehensive type hints throughout
- **Validation**: Pydantic models validate all configurations and data
- **Logging**: Structured logging with configurable levels
- **Separation of Concerns**: Clear boundaries between modules

### Core Components

```
algotrader/
├── core/              # Shared types, config, exceptions, logging
│   ├── types.py       # Pydantic models for Bar, Signal, Position, Metrics
│   ├── config.py      # Configuration models with validation
│   ├── exceptions.py  # Custom exception hierarchy
│   └── logging.py     # Structured logging setup
├── data/              # Data loading with validation
│   └── source.py      # DataSource ABC + CSV implementation
├── strategy/          # Strategy interface and implementations
│   ├── base.py        # Strategy Protocol
│   ├── mean_reversion.py
│   └── moving_average.py
├── execution/         # Order execution and fill simulation
│   └── broker.py      # Broker ABC + SimulatedBroker
├── risk/              # Position sizing and risk management
│   └── manager.py     # RiskManager ABC + BasicRiskManager
├── metrics/           # Performance analysis
│   └── report.py      # MetricsCalculator ABC + StandardMetrics
└── engine/            # Backtesting orchestration
    └── backtester.py  # Dependency-injected backtester
```

## ✨ Features

### Current
- ✅ Modular, testable architecture with dependency injection
- ✅ Comprehensive data validation (OHLC relationships, NaN detection)
- ✅ Multiple strategy implementations (mean reversion, MA crossover)
- ✅ Configurable broker simulation (slippage, commission, execution delay)
- ✅ Advanced metrics (Sharpe, Sortino, max drawdown, win rate, profit factor)
- ✅ Structured logging with configurable levels
- ✅ Type-safe configuration using Pydantic
- ✅ Custom exception hierarchy for better error handling
- ✅ CLI with rich output formatting

### Roadmap
- 🔜 Live data adapters (WebSocket, REST APIs)
- 🔜 Advanced risk models (VaR, CVaR, Kelly criterion)
- 🔜 Multi-asset portfolio backtesting
- 🔜 Walk-forward optimization
- 🔜 Event-driven live trading engine
- 🔜 Database persistence (TimescaleDB, InfluxDB)
- 🔜 Distributed backtesting (Ray, Dask)

## 🚀 Getting Started

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -U pip
pip install -e '.[dev]'
```

### Quick Example

```python
from pathlib import Path
from algotrader.core import BrokerConfig, RiskConfig, setup_logging
from algotrader.data import CsvDataSource
from algotrader.engine import Backtester
from algotrader.execution import SimulatedBroker
from algotrader.risk import BasicRiskManager
from algotrader.strategy import MovingAverageCrossStrategy

# Setup logging
setup_logging(level="INFO")

# Load data
data_source = CsvDataSource(path=Path("data/prices.csv"))
prices = data_source.load()

# Configure components
broker = SimulatedBroker(BrokerConfig(slippage_bps=5, commission_bps=2))
risk_mgr = BasicRiskManager(RiskConfig(max_position_size=1.0))

# Create strategy and run backtest
strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=20)
backtester = Backtester(strategy, broker=broker, risk_manager=risk_mgr)
result = backtester.run(prices)

# Access results
print(f"Sharpe: {result.metrics['sharpe_ratio']:.2f}")
print(f"Return: {result.metrics['total_return']:.2%}")
print(f"Max DD: {result.metrics['max_drawdown']:.2%}")
```

### CLI Usage

```bash
# Run with custom parameters
algotrader --csv data/prices.csv --lookback 10 --entry-z 1.5 --log-level INFO

# See all options
algotrader --help
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=algotrader --cov-report=html

# Run specific test
pytest tests/test_backtester.py -v
```

## 🎯 Adding New Strategies

Implement the `Strategy` Protocol:

```python
from algotrader.strategy.base import Strategy
import pandas as pd

class MyCustomStrategy:
    name = "my_strategy"
    
    def required_columns(self) -> set[str]:
        return {"close", "volume"}
    
    def warmup_bars(self) -> int:
        return 50
    
    def generate_signals(self, prices: pd.DataFrame) -> pd.Series:
        # Your logic here
        signals = pd.Series(0, index=prices.index)
        # ... compute signals (-1, 0, 1)
        return signals.rename("signal")
```

## 📊 Performance Metrics

The framework calculates:
- **Risk-Adjusted Returns**: Sharpe, Sortino ratios
- **Drawdown Analysis**: Maximum drawdown, recovery periods
- **Win/Loss Stats**: Win rate, profit factor
- **Returns**: Total, annualized returns

## 🔧 Configuration

Use Pydantic models for type-safe configuration:

```python
from algotrader.core import BacktestConfig, DataSourceConfig, BrokerConfig

config = BacktestConfig(
    initial_capital=100_000,
    data_source=DataSourceConfig(
        source_type="csv",
        path=Path("data/prices.csv")
    ),
    broker=BrokerConfig(slippage_bps=5, commission_bps=2),
)
```

## 📝 Code Quality

- **Type hints**: Complete type coverage
- **Linting**: Ruff for fast, comprehensive linting
- **Formatting**: Black for consistent code style
- **Testing**: pytest with comprehensive test coverage
- **Documentation**: Docstrings following Google style

```bash
# Check code quality
ruff check src/
black --check src/
```

## 🤝 Contributing

This is a foundation for building best-in-class algorithmic trading infrastructure. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with modern Python best practices and enterprise-grade design patterns for production algorithmic trading systems.
