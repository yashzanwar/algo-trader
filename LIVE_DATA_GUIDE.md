# Live Data Sources for Algo Trading

## 🎯 Quick Comparison

| Source | Cost | Real-time | Best For |
|--------|------|-----------|----------|
| **yfinance** | Free | ❌ (15-min delay) | Backtesting, Learning |
| **Alpha Vantage** | Free (limited) | ✅ | Small watchlists |
| **Zerodha Kite** | ₹2000/month | ✅ WebSocket | Professional trading |
| **Upstox** | Free (account needed) | ✅ WebSocket | Real trading |
| **Angel One** | Free (account needed) | ✅ WebSocket | Real trading |

---

## 🚀 Recommended Path

### **For Learning/Testing (Now):**
- Use `yfinance` with historical data
- Run backtests and optimize strategies
- Paper trade with simulated live monitoring

### **For Real Trading (When Ready):**
1. Open trading account (Zerodha/Upstox/Angel One)
2. Get API access (usually free with account)
3. Switch data source in framework
4. Start with small capital

---

## 📊 Setup Instructions

### Option 1: yfinance Real-Time (Current - Delayed)

```python
import yfinance as yf

# Get latest price (15-min delay)
ticker = yf.Ticker("RELIANCE.NS")
data = ticker.history(period="1d", interval="1m")
latest_price = data['Close'].iloc[-1]
```

**Pros:** Already working, no setup
**Cons:** Not true real-time, rate limited

---

### Option 2: Alpha Vantage (Free Real-Time)

**Step 1:** Get API Key
- Visit: https://www.alphavantage.co/support/#api-key
- Get free API key (25 calls/day)

**Step 2:** Install library
```bash
pip install alpha-vantage
```

**Step 3:** Use in framework
```python
from alpha_vantage.timeseries import TimeSeries

ts = TimeSeries(key='YOUR_API_KEY')
data, meta = ts.get_intraday('RELIANCE.NS', interval='1min')
```

**Pros:** Free, real-time
**Cons:** Limited calls (25/day), not enough for serious trading

---

### Option 3: Zerodha Kite Connect (Paid - Best)

**Step 1:** Prerequisites
- Zerodha trading account
- Subscribe to Kite Connect (₹2000/month)
- Complete developer onboarding

**Step 2:** Install KiteConnect
```bash
pip install kiteconnect
```

**Step 3:** Setup
```python
from kiteconnect import KiteConnect

kite = KiteConnect(api_key="your_api_key")

# Get access token (one-time login)
print(kite.login_url())

# Set access token
kite.set_access_token("your_access_token")

# Get live price
quote = kite.quote("NSE:RELIANCE")
price = quote['NSE:RELIANCE']['last_price']
```

**Step 4:** WebSocket for Real-Time
```python
from kiteconnect import KiteTicker

kws = KiteTicker("your_api_key", "your_access_token")

def on_ticks(ws, ticks):
    for tick in ticks:
        print(f"{tick['instrument_token']}: ₹{tick['last_price']}")

def on_connect(ws, response):
    ws.subscribe([738561])  # RELIANCE token
    ws.set_mode(ws.MODE_FULL, [738561])

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()
```

**Pros:** Professional-grade, WebSocket, order execution, reliable
**Cons:** ₹2000/month

---

### Option 4: Upstox API (Free - Best for Beginners)

**Step 1:** Prerequisites
- Upstox trading account
- Enable API access (free)

**Step 2:** Install
```bash
pip install upstox-python
```

**Step 3:** Setup
```python
from upstox_api.api import Upstox

u = Upstox('your_api_key', 'your_api_secret')
u.set_redirect_uri('your_redirect_uri')
u.set_api_secret('your_api_secret')

# Login and get session
print(u.get_login_url())

# After login, get access token
u.set_code('your_auth_code')
access_token = u.get_master_contract('NSE')

# Get live data
u.get_live_feed(u.get_instrument_by_symbol('NSE_EQ', 'RELIANCE'))
```

**Pros:** FREE, real-time WebSocket, good for retail traders
**Cons:** Need Upstox account

---

### Option 5: Angel One SmartAPI (Free)

**Step 1:** Prerequisites
- Angel One trading account
- Enable SmartAPI (free)

**Step 2:** Install
```bash
pip install smartapi-python
```

**Step 3:** Setup
```python
from SmartApi import SmartConnect

api = SmartConnect(api_key="your_api_key")
data = api.generateSession("CLIENT_ID", "PASSWORD")

# Get live data
api.ltpData("NSE", "RELIANCE-EQ", "2885")
```

**Pros:** Free, decent API
**Cons:** Documentation not as good as Zerodha

---

## 🎯 My Recommendation for You

### **Phase 1: Now (Free)**
1. Continue with **yfinance** for backtesting
2. Perfect your strategy
3. Test with historical data
4. Use `live_signal_monitor.py` with CSV data

### **Phase 2: Paper Trading (Free)**
1. Open **Upstox** or **Angel One** account (no cost)
2. Enable API access (free)
3. Get real-time data feed
4. Run strategy in "monitor only" mode (no actual trading)

### **Phase 3: Real Trading (Paid)**
1. If profitable in paper trading, upgrade to **Zerodha Kite Connect**
2. Start with ₹10,000-50,000 capital
3. Run 1-2 strategies max
4. Monitor for 1 month

---

## 🔧 Integrating Live Data into Your Framework

Create a new data source class:

```python
# src/algotrader/data/live.py
from algotrader.data.base import DataSource

class KiteDataSource(DataSource):
    def __init__(self, api_key: str, access_token: str):
        from kiteconnect import KiteConnect
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
    
    def load(self, symbol: str, interval: str = '1minute'):
        # Get historical data
        data = self.kite.historical_data(
            instrument_token=self._get_token(symbol),
            from_date='2024-01-01',
            to_date='2025-12-26',
            interval=interval
        )
        return self._to_dataframe(data)
    
    def get_live_price(self, symbol: str):
        quote = self.kite.quote(f"NSE:{symbol}")
        return quote[f'NSE:{symbol}']['last_price']
```

---

## 💡 Next Steps

1. **Test Current Setup:**
   ```bash
   python examples/live_signal_monitor.py
   ```

2. **Choose Your Path:**
   - Learning? → Stay with yfinance + CSV
   - Ready to trade? → Open Upstox/Angel account
   - Professional? → Get Zerodha Kite Connect

3. **Start Small:**
   - Monitor 5-10 stocks max
   - Use paper trading first
   - Test for 1 month minimum

---

## 📞 Support Links

- **Zerodha Kite:** https://kite.trade/docs/connect/v3/
- **Upstox API:** https://upstox.com/developer/api-documentation
- **Angel One:** https://smartapi.angelbroking.com/docs
- **Alpha Vantage:** https://www.alphavantage.co/documentation/

---

**Ready to go live?** Pick an option above and I'll help you integrate it! 🚀
