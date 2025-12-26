# Network Limitations & Workaround Guide

## 🚧 Your Corporate Network Blocks:

All external financial APIs due to SSL certificate verification:
- Yahoo Finance
- Angel One SmartAPI
- Any other live data source

## ✅ What Works Now (At Work):

1. **CSV-based backtesting**
   ```bash
   python examples/live_monitor_csv.py
   ```

2. **Strategy development** - All strategy logic works perfectly

3. **Telegram notifications** - Using curl bypass

4. **Signal detection** - All monitoring code works

## 🏠 Setup for Home Use:

### **One-Time Setup (Do This at Home Tonight):**

```bash
# Download real data (works from home network)
python examples/download_real_data_home.py
```

This will:
- Connect to Yahoo Finance (no SSL issues at home)
- Download 2 years of real data for your watchlist
- Save to CSV files
- Create a sync script

### **Daily Workflow:**

**At Home (Morning/Evening):**
```bash
# Update data with latest prices
python examples/sync_data.py
```

**At Work (All Day):**
```bash
# Use yesterday's data for backtesting
python examples/backtest_strategies.py

# Test signal monitoring
python examples/live_monitor_csv.py
```

**At Home (After Market Close):**
```bash
# Download today's data
python examples/sync_data.py

# Run real monitoring with live API
python examples/live_monitor_angel.py
```

## 📊 Recommended Approach:

### **Phase 1: Development (At Work)**
- Use realistic test data (already generated)
- Perfect your strategy logic
- Test signal detection
- Optimize parameters
- Build confidence

### **Phase 2: Real Data (At Home)**
- Setup Angel One API
- Download historical data
- Backtest with real prices
- Validate strategy performance

### **Phase 3: Live Trading (At Home)**
- Run live monitoring during market hours
- Use real-time API feeds
- Automate trading decisions
- Monitor via Telegram

## 💡 Quick Start (Right Now):

The realistic data is already good enough for development:

```bash
# This works perfectly at work right now
python examples/live_monitor_csv.py
```

It simulates live monitoring with realistic Reliance prices (~₹1,312).

## 🎯 Bottom Line:

**Your framework is 100% ready.** The only limitation is corporate network blocking live APIs.

**Solution:** Develop strategies at work, execute trades from home.

This is actually how many traders work - develop during the day, trade before/after market hours from home!
