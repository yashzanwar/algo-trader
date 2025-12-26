# Angel One SmartAPI Integration Guide

## 🎯 What You Need to Provide

### 1. **Angel One Account** (Free)
- Open demat account at: https://www.angelone.in/
- Complete KYC verification
- No charges for API access (FREE!)

### 2. **API Credentials** (Get from Angel One)
Once you have an account, get these 3 things:

#### a) **API Key**
- Login to: https://smartapi.angelbroking.com/
- Go to "My Profile" → "My API Key"
- Click "Create API Key"
- Save this API Key

#### b) **Client ID** (Your Angel One login ID)
- This is your Angel One trading account ID
- Example: `A12345678`

#### c) **Password/PIN**
- Your Angel One trading password
- MPIN for login

---

## 📋 Setup Steps

### Step 1: Install Angel One Library
```bash
pip install smartapi-python
```

### Step 2: Get Your Credentials
1. Login to Angel One web app
2. Go to API section
3. Generate API Key
4. Note down:
   - API Key (looks like: `xxxxxxxxxxx`)
   - Client ID (your login ID)
   - Password/MPIN

### Step 3: Configure Framework
Run setup script (I'll create this) and enter your credentials.

---

## 🔐 Information Required From You

Please provide these details when ready:

1. **API Key**: `___________________________`
2. **Client ID**: `___________________________`
3. **MPIN/Password**: `___________________________`

---

## ✅ What You'll Get

Once configured:
- ✅ **Real-time market data** (live prices, no delay)
- ✅ **Historical data** (for backtesting)
- ✅ **WebSocket feed** (tick-by-tick updates)
- ✅ **Order placement** (buy/sell automation)
- ✅ **Portfolio tracking** (your holdings)
- ✅ **100% FREE** (no monthly charges)

---

## 🚀 Next Steps

1. **Open Angel One account** (if you don't have one)
   - Visit: https://www.angelone.in/open-demat-account
   - Complete in 10 minutes with Aadhaar
   
2. **Get API credentials** (once account is active)
   - Login to web app
   - Go to API section
   - Generate API key
   
3. **Run setup script** (I'll create this)
   ```bash
   python examples/setup_angel_one.py
   ```

4. **Start monitoring**
   ```bash
   python examples/live_monitor_angel.py
   ```

---

## 📞 Support

- **Angel One API Docs**: https://smartapi.angelbroking.com/docs
- **Support**: https://www.angelone.in/contact-us
- **Phone**: 1800-123-4455

---

## ⚠️ Important Notes

1. **Keep credentials safe** - Never share API key publicly
2. **Use .env file** - Don't commit credentials to git
3. **Test first** - Start with paper trading before real money
4. **Rate limits** - Free tier has reasonable limits for retail trading

---

**Ready?** Let me know when you have the credentials and I'll help you configure!
