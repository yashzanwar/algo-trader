# Quick Start Guide: Backtesting Reliance Stock

## Setup (One-Time)

Already done! Your environment is ready.

## Step 1: Get Real Reliance Data

### Option A: Download from NSE/BSE (Recommended)

1. **NSE Website**:
   - Go to https://www.nseindia.com/
   - Search for "RELIANCE"
   - Click "Historical Data"
   - Select date range (e.g., Jan 1, 2023 to Dec 25, 2024)
   - Download CSV

2. **Zerodha Kite** (if you have account):
   - Open Kite
   - Search "RELIANCE"
   - Click chart → More → Download Historical Data
   - Select date range and download

3. **TradingView** (Free):
   - Go to https://www.tradingview.com/
   - Search "RELIANCE" (NSE)
   - Click "..." → Export chart data
   - Download CSV

### Option B: Use Your Broker

Most brokers (Zerodha, Upstox, Angel One, etc.) provide historical data downloads.

### Option C: Sample Data (For Testing)

The framework already created sample data at:
```
examples/data/reliance_sample.csv
```

## Step 2: Run Backtest

### Using Sample Data:
```bash
python examples/backtest_reliance_csv.py
```

### Using Your Real Data:

1. Save your CSV to `examples/data/reliance_real.csv`

2. Edit `examples/backtest_reliance_csv.py`:
   ```python
   # Change this line:
   csv_path = Path("examples/data/reliance_sample.csv")
   # To:
   csv_path = Path("examples/data/reliance_real.csv")
   ```

3. Run:
   ```bash
   python examples/backtest_reliance_csv.py
   ```

## Step 3: Try Different Strategies

Edit the file to test different parameters:

```python
# Moving Average - adjust windows
MovingAverageCrossStrategy(fast_window=10, slow_window=50)

# Mean Reversion - adjust sensitivity
MeanReversionStrategy(lookback=30, entry_z=1.5)
```

## Stock Screening: Finding Best Stocks

### Quick Scan (5 Large-Cap Stocks):

```bash
python examples/scan_stocks.py
```

This scans:
- RELIANCE.NS
- TCS.NS
- HDFCBANK.NS
- INFY.NS
- ICICIBANK.NS

### Full Scan (Top 20 Nifty50):

Edit `examples/scan_stocks.py` and uncomment the Nifty50 section.

### Custom Stock List:

Create your own scanner:

```python
from algotrader.scanner import StockScanner
from algotrader.strategy import MovingAverageCrossStrategy

# Your stocks
my_stocks = ["RELIANCE.NS", "TCS.NS", "WIPRO.NS"]

scanner = StockScanner(
    symbols=my_stocks,
    strategy=MovingAverageCrossStrategy(5, 20),
    start_date="2023-01-01",
    end_date="2024-12-25"
)

results = scanner.scan()
scanner.print_results(results)
```

## Understanding Results

### Good Strategy Signs:
- **Sharpe > 1.0**: Risk-adjusted returns are good
- **Win Rate > 50%**: More winning trades than losing
- **Profit Factor > 1.5**: Wins significantly outweigh losses
- **Max Drawdown < 20%**: Manageable risk

### Poor Strategy (Need Adjustment):
- **Sharpe < 0**: Strategy loses money
- **Win Rate < 40%**: Too many losses
- **Profit Factor < 1.0**: Loses more than wins

## Stock Selection Tips

### For Moving Average Strategies:
Look for stocks with:
- Clear trends (not range-bound)
- High liquidity (volume > 1M daily)
- Moderate volatility

**Good candidates**: RELIANCE, TCS, INFY

### For Mean Reversion:
Look for stocks with:
- Range-bound behavior
- Predictable support/resistance
- Low news impact

**Good candidates**: HDFCBANK, ITC, HINDUNILVR

### Sectors to Consider:

**Trending Sectors** (for MA Crossover):
- Technology: TCS, INFY, WIPRO
- Energy: RELIANCE, ONGC
- Auto: MARUTI, TATAMOTORS

**Stable Sectors** (for Mean Reversion):
- Banking: HDFCBANK, ICICIBANK
- FMCG: HINDUNILVR, ITC
- Pharma: SUNPHARMA, DRREDDY

## Next Steps

1. **Get 2 years of Reliance data** from your broker
2. **Run backtest** with real data
3. **Compare strategies** - which performs better?
4. **Scan other stocks** - find the best match for your strategy
5. **Optimize parameters** - try different MA windows
6. **Paper trade** - test with fake money first
7. **Start small** - real money with small position sizes

## Common Issues

**Q: Where do I get data?**
A: See `examples/HOW_TO_GET_STOCK_DATA.md` for detailed guide

**Q: Strategy shows negative returns?**
A: Normal! Try different stocks or adjust parameters

**Q: Too many trades?**
A: Increase MA windows (e.g., 10/50 instead of 5/20)

**Q: Too few trades?**
A: Decrease MA windows or reduce entry threshold

**Q: How to know which stocks work?**
A: Run the scanner! It tests your strategy on multiple stocks

## Example Workflow

```bash
# 1. Test on sample data
python examples/backtest_reliance_csv.py

# 2. Scan multiple stocks
python examples/scan_stocks.py

# 3. Download real data for top 3 stocks from scanner

# 4. Backtest with real data

# 5. Pick best performing stock/strategy combo

# 6. Paper trade for 1 month

# 7. Start live with small capital
```

## Files Created

- `examples/backtest_reliance_csv.py` - Single stock backtest
- `examples/scan_stocks.py` - Multi-stock scanner
- `examples/HOW_TO_GET_STOCK_DATA.md` - Data sourcing guide
- `examples/data/reliance_sample.csv` - Sample data

## Need Help?

Check the main README.md for detailed architecture and API docs.
