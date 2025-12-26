# Position Management via Telegram Bot

## Overview
The live monitoring script now supports position tracking via Telegram bot commands! This allows you to:
- Confirm when you've bought stocks
- Track your positions with live P&L
- Get EXIT signals only for stocks you own
- Get BUY signals only for stocks you don't own

## How It Works

### 1. When You Get a BUY Signal
```
🔔 📈 TRADING SIGNAL ALERT
Signal Type: BUY
Symbol:      RELIANCE
Price:       ₹2850.00
Strategy:    moving_average_cross
Reason:      Golden Cross: 10-MA crossed above 50-MA
```

### 2. After You Buy (manually in your broker app)
Send this command in Telegram:
```
/bought RELIANCE 10 2850
```

Bot responds:
```
✅ Position Added

Symbol: RELIANCE
Quantity: 10
Entry Price: ₹2850.00
Total Value: ₹28500.00

🔔 Now monitoring for EXIT signals
```

### 3. Monitor Your Positions
```
/positions
```

Shows:
```
📊 Active Positions

RELIANCE
  Qty: 10 @ ₹2850.00
  Value: ₹28500.00
  Entry: 2025-12-26 14:30

Total Value: ₹28500.00
```

### 4. Check Live P&L
```
/status
```

Shows:
```
📊 Portfolio Status

RELIANCE
  Entry: ₹2850.00 → Current: ₹2920.00
  📈 P&L: ₹700.00 (+2.46%)

Overall
  Invested: ₹28500.00
  Current: ₹29200.00
  📈 P&L: ₹700.00 (+2.46%)
```

### 5. When EXIT Signal Triggers
```
🔔 ↔️ TRADING SIGNAL ALERT
Signal Type: EXIT
Symbol:      RELIANCE
Price:       ₹2920.00
Reason:      Position closed - MAs converged
```

### 6. After You Sell
```
/sold RELIANCE
```

Bot responds:
```
✅ Position Closed

Symbol: RELIANCE
Quantity: 10
Entry Price: ₹2850.00

📈 P&L Summary
Exit Price: ₹2920.00
P&L: ₹700.00 (+2.46%)

🔔 Now monitoring for BUY signals
```

## All Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/bought SYMBOL QTY PRICE` | Add position after buying | `/bought RELIANCE 10 2850` |
| `/sold SYMBOL` | Remove position after selling | `/sold RELIANCE` |
| `/positions` | List all active positions | `/positions` |
| `/status` | Show live P&L for all positions | `/status` |
| `/help` | Show help message | `/help` |

## Features

### Position-Aware Signals
- **No Position**: You get BUY signals only
- **Has Position**: You get EXIT signals only
- **Never**: You won't get duplicate BUY signals for stocks you already own

### Automatic Tracking
- Positions saved to `positions.json`
- Survives script restarts
- Can average up/down by buying more of same stock

### Live P&L
- Real-time profit/loss calculation
- Both absolute (₹) and percentage (%)
- Portfolio-level summary

## Running the Script

```bash
python3 examples/live_monitor_angel.py
```

The script will:
1. Load any existing positions from `positions.json`
2. Connect to Angel One API
3. Start monitoring stocks
4. Process Telegram commands every 2 minutes

## Testing

Send `/help` to your bot to verify it's working:
- Open Telegram
- Find your bot (search for bot name)
- Send: `/help`
- You should get the help message

## Notes

- Commands are processed every 2 minutes (same as check interval)
- Price fetcher uses live Angel One data for accurate P&L
- Positions persist across script restarts
- Only authorized chat IDs can use commands (configured in script)
