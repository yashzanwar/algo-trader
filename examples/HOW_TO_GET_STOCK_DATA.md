# How to Get Stock Data for Backtesting

This guide explains how to get historical stock data for your strategies.

## Method 1: Yahoo Finance (Quick & Free)

**Note**: May have SSL issues on corporate networks. If Yahoo Finance doesn't work, use Method 2 or 3.

```python
from algotrader.data import YahooFinanceDataSource

# Indian stocks (NSE)
data_source = YahooFinanceDataSource(
    symbol="RELIANCE.NS",  # .NS for NSE, .BO for BSE
    start_date="2023-01-01",
    end_date="2024-12-25"
)
prices = data_source.load()

# US stocks
data_source = YahooFinanceDataSource(
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2024-12-25"
)
```

### Common Indian Stock Symbols:
- `RELIANCE.NS` - Reliance Industries
- `TCS.NS` - Tata Consultancy Services
- `HDFCBANK.NS` - HDFC Bank
- `INFY.NS` - Infosys
- `ITC.NS` - ITC Ltd

## Method 2: CSV from Your Broker

Most brokers provide historical data download. Download and use CSV:

```python
from pathlib import Path
from algotrader.data import CsvDataSource

data_source = CsvDataSource(
    path=Path("data/reliance.csv"),
    datetime_column="date"  # or "timestamp", "datetime", etc.
)
prices = data_source.load()
```

### Required CSV Format:
```csv
date,open,high,low,close,volume
2024-01-02,2450.00,2475.50,2440.25,2468.75,5234567
2024-01-03,2470.00,2489.00,2465.00,2482.50,4567890
```

### Where to Get CSV Data:

**India:**
- **NSE Website**: https://www.nseindia.com/ (Historical Data section)
- **BSE Website**: https://www.bseindia.com/
- **Zerodha Kite**: Use "Instruments" to download
- **Upstox**: Historical data in account section
- **TradingView**: Export from charts (Free account)

**USA:**
- **Yahoo Finance**: Download CSV from stock page
- **Google Finance**: Historical data tab
- **Alpha Vantage**: Free API (requires key)

## Method 3: Paid Data Providers (Professional)

For production trading, use professional data:

```python
# Example structure (you'll need to implement the data source)
from algotrader.data.source import DataSource

class AlphaVantageDataSource(DataSource):
    def __init__(self, api_key: str, symbol: str):
        self.api_key = api_key
        self.symbol = symbol
    
    def load(self) -> pd.DataFrame:
        # Fetch from Alpha Vantage API
        pass
```

### Recommended Providers:
- **Alpha Vantage**: Free tier available (5 calls/min)
- **Polygon.io**: $199/month for real-time
- **IEX Cloud**: $9/month starter
- **Quandl**: Various datasets

## Method 4: Generate Sample Data (Testing Only)

For strategy development and testing:

```python
import pandas as pd
import numpy as np

# Generate sample price data
dates = pd.date_range("2023-01-01", periods=250, freq="B")
close = 100 + np.cumsum(np.random.randn(250) * 2)

df = pd.DataFrame({
    "date": dates,
    "open": close - np.random.uniform(0, 2, 250),
    "high": close + np.random.uniform(0, 3, 250),
    "low": close - np.random.uniform(0, 3, 250),
    "close": close,
    "volume": np.random.randint(100000, 1000000, 250),
})

df.to_csv("data/sample.csv", index=False)
```

## Stock Screening Tips

### 1. Start with Large-Cap Stocks
Large-cap stocks have:
- Better liquidity
- Lower slippage
- More reliable data
- Less manipulation

```python
from algotrader.scanner import INDIAN_LARGECAP

# Predefined list
symbols = INDIAN_LARGECAP
# Or create your own
symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
```

### 2. Use Scanner to Find Best Stocks

```python
from algotrader.scanner import StockScanner
from algotrader.strategy import MovingAverageCrossStrategy

scanner = StockScanner(
    symbols=["RELIANCE.NS", "TCS.NS", "INFY.NS"],
    strategy=MovingAverageCrossStrategy(5, 20),
    start_date="2023-01-01",
    end_date="2024-01-01"
)

results = scanner.scan()
scanner.print_results(results)
```

### 3. Filter Criteria

Good stocks for algorithmic trading:
- **High liquidity**: Volume > 1M shares/day
- **Low volatility**: For mean reversion
- **High volatility**: For breakout strategies
- **Trending**: For momentum/MA strategies
- **Range-bound**: For mean reversion

### 4. Sectoral Rotation

Focus on sectors:
```python
# IT Sector
IT_STOCKS = ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"]

# Banking
BANKING = ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS"]

# Energy
ENERGY = ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS"]
```

## Best Practices

1. **Start Small**: Test on 1-2 stocks before scaling
2. **Validate Data**: Always check for missing/corrupt data
3. **Use Recent Data**: 2-3 years is good for most strategies
4. **Match Timeframe**: Daily data for swing trading, intraday for day trading
5. **Check Splits/Bonuses**: Ensure data is adjusted for corporate actions

## Troubleshooting

### Yahoo Finance Not Working?
- Corporate firewall blocking
- SSL certificate issues
- Try: Use CSV from broker instead

### Data Looks Wrong?
- Check for stock splits (prices jump/drop suddenly)
- Verify symbol (RELIANCE.NS not RELIANCE)
- Check date format in CSV

### No Volume Data?
- Some free sources don't provide volume
- Use volume=1 as placeholder if strategy doesn't need it

## Next Steps

1. Get 1-2 years of data for Reliance
2. Run backtest with your strategy
3. Compare with Nifty 50 index benchmark
4. Optimize parameters
5. Paper trade before live
