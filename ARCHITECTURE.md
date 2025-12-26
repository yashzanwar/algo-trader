# Architecture Documentation

## Overview

AlgoTrader is built on enterprise design patterns with a focus on extensibility, testability, and maintainability. The architecture follows SOLID principles and uses dependency injection throughout.

## Design Patterns

### 1. Dependency Injection (DI)

All major components are injected into the `Backtester`, making it easy to swap implementations:

```python
backtester = Backtester(
    strategy=MyStrategy(),
    broker=SimulatedBroker(config),
    risk_manager=AdvancedRiskManager(config),
    metrics_calculator=CustomMetrics(),
)
```

**Benefits:**
- Easy to test (mock dependencies)
- Swap implementations without changing backtester
- Clear component boundaries

### 2. Protocol/ABC Pattern

Every major component has an abstract interface:

- `Strategy` (Protocol) - Signal generation
- `DataSource` (ABC) - Data loading
- `Broker` (ABC) - Order execution
- `RiskManager` (ABC) - Position sizing
- `MetricsCalculator` (ABC) - Performance analysis

**Benefits:**
- Duck typing with runtime checks
- Clear contracts
- Easy to extend

### 3. Immutability

Configuration and results use Pydantic's frozen models:

```python
class BrokerConfig(BaseModel):
    slippage_bps: float = 0.0
    commission_bps: float = 0.0
    
    model_config = {"frozen": True}  # Immutable
```

**Benefits:**
- Thread-safe
- No accidental mutations
- Easier debugging

### 4. Strategy Pattern

Strategies are interchangeable implementations of the `Strategy` protocol:

```python
# Swap strategies easily
strategy = MeanReversionStrategy(lookback=20)
# OR
strategy = MovingAverageCrossStrategy(fast=5, slow=20)

backtester = Backtester(strategy)  # Works with any strategy
```

### 5. Factory Pattern (Future)

For complex object creation:

```python
# Future enhancement
strategy = StrategyFactory.create("mean_reversion", config)
broker = BrokerFactory.create("simulated", config)
```

## Component Responsibilities

### Core Module
- **types.py**: Shared data models (Bar, Signal, Position, Metrics)
- **config.py**: Validated configuration models
- **exceptions.py**: Custom exception hierarchy
- **logging.py**: Structured logging setup

### Data Module
- **DataSource ABC**: Interface for data loading
- **CsvDataSource**: CSV file implementation
- Validates OHLC relationships and handles errors

### Strategy Module
- **Strategy Protocol**: Signal generation interface
- Each strategy in separate file
- Declares required columns and warmup period

### Execution Module
- **Broker ABC**: Order execution interface
- **SimulatedBroker**: Realistic fill simulation
- Handles slippage, commission, execution delay

### Risk Module
- **RiskManager ABC**: Position sizing interface
- **BasicRiskManager**: Simple position limits
- Extensible for advanced risk models (VaR, Kelly, etc.)

### Metrics Module
- **MetricsCalculator ABC**: Performance metrics interface
- **StandardMetricsCalculator**: Comprehensive metrics
- Sharpe, Sortino, drawdown, win rate, profit factor

### Engine Module
- **Backtester**: Orchestrates all components
- Validates data and configurations
- Logs execution flow
- Returns immutable results

## Data Flow

```
CSV File → DataSource.load() → Validated DataFrame
    ↓
Strategy.generate_signals() → Raw Signals
    ↓
RiskManager.size_positions() → Sized Positions
    ↓
Broker.execute() → Filled Positions
    ↓
MetricsCalculator.calculate() → Performance Metrics
    ↓
BacktestResult (immutable)
```

## Error Handling

Custom exception hierarchy:

```
AlgoTraderError (base)
├── DataError
│   └── InsufficientDataError
├── ConfigurationError
├── StrategyError
└── ValidationError
```

All exceptions are caught, logged, and re-raised with context.

## Logging Strategy

Structured logging at multiple levels:

- **DEBUG**: Detailed execution trace
- **INFO**: Key events (data loaded, backtest started)
- **WARNING**: Potential issues
- **ERROR**: Errors with full context

Logger names follow module hierarchy: `algotrader.{module}.{class}`

## Configuration Management

All configuration uses Pydantic models with validation:

```python
class RiskConfig(BaseModel):
    max_position_size: float = Field(gt=0)
    max_leverage: float = Field(gt=0, le=10)
    stop_loss_pct: float | None = Field(ge=0, le=1)
    
    model_config = {"frozen": True}
```

**Benefits:**
- Type validation
- Range checks
- Immutability
- Self-documenting

## Testing Strategy

- **Unit tests**: Test each component in isolation
- **Integration tests**: Test component interactions
- **Fixtures**: Shared test data
- **Mocking**: Mock external dependencies

## Future Enhancements

### Event-Driven Architecture
For live trading, add event bus:

```python
class Event:
    pass

class MarketDataEvent(Event):
    pass

class SignalEvent(Event):
    pass

class OrderEvent(Event):
    pass

class EventBus:
    def publish(self, event: Event): ...
    def subscribe(self, handler): ...
```

### Plugin System
Load strategies dynamically:

```python
StrategyRegistry.register("my_strategy", MyStrategy)
strategy = StrategyRegistry.get("my_strategy")(config)
```

### Async/Await
For live trading with websockets:

```python
class AsyncBroker(Broker):
    async def execute_async(self, order): ...
```

## Performance Considerations

- **Vectorization**: Use pandas operations, not row-by-row
- **Lazy evaluation**: Only compute what's needed
- **Caching**: Cache expensive computations
- **Parallel backtesting**: Use Ray/Dask for parameter sweeps

## Scalability Path

1. **Single strategy** ✅ (current)
2. **Multi-strategy portfolio**
3. **Parameter optimization**
4. **Walk-forward analysis**
5. **Distributed backtesting**
6. **Live trading**
