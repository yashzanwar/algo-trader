# How Algo Traders Scout Stocks from 2000+ Universe

## The Challenge
With 2000+ stocks on NSE, how do you find the best ones for your strategy?

## Professional 4-Stage Screening Process

### Stage 1: Universe Definition (2000 → ~500)
**Goal:** Filter out illiquid and unsuitable stocks

**Criteria:**
- ✅ **Liquidity**: Average daily value traded > ₹10 crore
  - Why: Need sufficient volume to enter/exit without slippage
  - Example: Reject penny stocks with ₹10 lakh daily volume

- ✅ **Price Range**: ₹50 - ₹5000
  - Why: Avoid penny stocks (₹5) and very expensive stocks (₹10,000+)
  - Penny stocks have manipulation risk
  - Very expensive stocks have low volume

- ✅ **Market Cap**: > ₹1000 crore
  - Why: Avoid micro-caps with high manipulation risk
  - Large/mid-caps have better liquidity

- ✅ **Data Quality**: Minimum 1-2 years of clean data
  - Why: Need sufficient history for backtesting

**Result:** ~500 tradeable stocks remain

---

### Stage 2: Technical Screening (~500 → ~100)
**Goal:** Filter by market conditions and technical setup

**Criteria:**
- ✅ **Trend Filter**: Price > 200-day Moving Average
  - Why: Only trade uptrending stocks ("trade with the trend")
  - Avoids catching falling knives

- ✅ **Volatility**: ATR 2-5% of price
  - Why: Need enough movement for profits, but not too wild
  - Too low (< 1%): Strategy can't make money after costs
  - Too high (> 8%): Risk management becomes difficult

- ✅ **Momentum**: Not in extreme zones
  - RSI between 40-70 (not overbought/oversold)
  - Price making higher highs/higher lows (uptrend confirmation)

**Result:** ~100 stocks with favorable technical setup

---

### Stage 3: Strategy Ranking (~100 → ~20)
**Goal:** Find stocks where YOUR strategy performs best

**Process:**
1. **Backtest** each of the 100 stocks with your strategy
2. **Calculate metrics** for each:
   - Sharpe Ratio (risk-adjusted returns)
   - Total Return
   - Max Drawdown
   - Win Rate
   - Number of Trades

3. **Apply filters:**
   - ✅ Sharpe Ratio > 0.8 (good risk-adjusted returns)
   - ✅ Win Rate > 45% (not losing too often)
   - ✅ Max Drawdown < 20% (controlled risk)
   - ✅ Minimum 5-10 trades (statistical significance)

4. **Rank by Sharpe Ratio** (best risk-adjusted returns at top)

**Result:** Top 20 stocks where your strategy works best

---

### Stage 4: Portfolio Construction (~20 → 5-10)
**Goal:** Build diversified portfolio

**Criteria:**
- ✅ **Sector Limits**: Maximum 2-3 stocks per sector
  - Why: Avoid concentration risk
  - Don't take 5 banking stocks - if banking sector crashes, you crash

- ✅ **Correlation**: Avoid highly correlated stocks
  - Don't take HDFC Bank + ICICI Bank + Axis Bank together
  - They move together, so no real diversification

- ✅ **Position Sizing**: Based on volatility
  - Lower volatility stock = higher position size
  - Higher volatility stock = smaller position size

- ✅ **Target Size**: 5-10 stocks typically
  - Why: Enough diversification, but not too diluted
  - More than 15 stocks = overdiversification

**Result:** Final portfolio of 5-10 high-quality, diversified stocks

---

## Real-World Example

**Starting Universe:** 2000 NSE stocks

**Stage 1 (Liquidity):** 
- Filter: Daily volume > ₹10Cr, Price ₹50-5000, MCap > ₹1000Cr
- Result: **512 stocks** remain

**Stage 2 (Technical):**
- Filter: Price > 200-day MA, ATR 2-5%
- Result: **127 stocks** remain (uptrending with good volatility)

**Stage 3 (Strategy):**
- Backtest MA Cross (10/50) on all 127 stocks
- Filter: Sharpe > 0.8, Win% > 45%, MaxDD < 20%
- Result: **18 stocks** where strategy works

**Stage 4 (Portfolio):**
- Select top 10 by Sharpe
- Limit: Max 2 per sector
- **Final Portfolio:** 10 stocks

---

## Practical Implementation

### Weekly Routine
```bash
# Run full screening every Sunday
python examples/screen_portfolio.py

# Get top 10 stocks for the week
# Replace underperformers if needed
```

### Monthly Rebalancing
- Re-run full screening
- Compare with current portfolio
- Replace stocks with Sharpe < 0.5 for 3 consecutive months

### Quarterly Review
- Refresh entire universe
- Check if strategy parameters need adjustment
- Update sector allocations

---

## Key Insights

1. **Most stocks are untr
adeable** - Out of 2000, only ~100 meet basic criteria
2. **Your strategy won't work everywhere** - Maybe only 10-20 stocks are a good fit
3. **Diversification is critical** - Never go all-in on one stock
4. **Screening is ongoing** - Markets change, re-screen regularly

---

## Common Mistakes to Avoid

❌ **Trying to trade all 2000 stocks**
- Result: Most lose money due to poor liquidity or unsuitability

❌ **Not filtering by trend**
- Result: Catching falling knives, big losses

❌ **Over-optimization**
- Tweaking strategy parameters to fit one specific stock
- Result: Curve-fitting, fails in live trading

❌ **No diversification**
- Taking all banks or all IT stocks
- Result: Sector crash wipes you out

❌ **Ignoring transaction costs**
- High-frequency strategy on low-volume stock
- Result: Costs eat all profits

---

## Your Framework's Screener

See `examples/screen_portfolio.py` for implementation:

```python
from algotrader.screener import StockScreener, ScreeningCriteria

# Configure criteria
criteria = ScreeningCriteria(
    min_avg_volume_inr=5_00_00_000,  # ₹5 crore
    price_above_ma200=True,
    min_sharpe=0.8,
    target_portfolio_size=10
)

# Run screening
screener = StockScreener(criteria)
portfolio = screener.screen(stocks_data, backtest_fn, metadata)
```

This gives you a professional, systematic approach to stock selection!
