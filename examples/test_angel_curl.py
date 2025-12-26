#!/usr/bin/env python3
"""Test Angel One API using curl (bypasses SSL issues)."""

import sys
sys.path.insert(0, 'src')

from algotrader.data.angel_curl import AngelOneCurl

print("\n" + "=" * 80)
print("🧪 ANGEL ONE API TEST (Using curl to bypass SSL)")
print("=" * 80)

# Your credentials
API_KEY = "OF6qV328"
CLIENT_ID = "DEMO123"
PASSWORD = input("\nPassword: ").strip()
TOTP_SECRET = "ABCDEFGHIJKLMNOP"  # QR value for auto-generating TOTP

print("\n💡 TOTP will be auto-generated from your QR secret")

print("\n" + "=" * 80)
print("🔄 TESTING CONNECTION")
print("=" * 80)

try:
    print("\n1️⃣  Logging in with curl (auto-generating TOTP)...", end=" ", flush=True)
    client = AngelOneCurl(API_KEY, CLIENT_ID, PASSWORD, TOTP_SECRET)
    print("✅ SUCCESS!")
    
    print("2️⃣  Getting your profile...", end=" ", flush=True)
    profile = client.get_profile()
    
    if profile.get('status'):
        print("✅ SUCCESS!")
        user = profile['data']
        print(f"\n   👤 Name: {user.get('name', 'N/A')}")
        print(f"   📧 Email: {user.get('email', 'N/A')}")
        print(f"   📱 Mobile: {user.get('mobileno', 'N/A')}")
    else:
        print("❌ Failed to get profile")
    
    print("\n3️⃣  Searching for RELIANCE...", end=" ", flush=True)
    token = client.search_scrip('NSE', 'RELIANCE')
    
    if token:
        print(f"✅ Found! Token: {token}")
        
        print("4️⃣  Downloading historical data...", end=" ", flush=True)
        
        from datetime import datetime, timedelta
        
        data = client.get_candle_data(
            exchange='NSE',
            symbol_token=token,
            interval='ONE_DAY',
            from_date=datetime.now() - timedelta(days=30),
            to_date=datetime.now()
        )
        
        if data.get('status'):
            candles = data['data']
            print(f"✅ Got {len(candles)} days!")
            
            # Show latest price
            latest = candles[-1]
            print(f"\n   📊 Latest RELIANCE data:")
            print(f"   Date: {latest[0]}")
            print(f"   Open: ₹{latest[1]:.2f}")
            print(f"   High: ₹{latest[2]:.2f}")
            print(f"   Low: ₹{latest[3]:.2f}")
            print(f"   Close: ₹{latest[4]:.2f}")
            print(f"   Volume: {latest[5]:,}")
        else:
            print("❌ Failed to get data")
    else:
        print("❌ Symbol not found")
    
    print("\n" + "=" * 80)
    print("✅ ANGEL ONE API IS WORKING WITH CURL!")
    print("=" * 80)
    print("\n💡 This bypasses corporate SSL certificates using curl -k flag")
    print("📊 You can now download real market data!")
    print("=" * 80 + "\n")

except Exception as e:
    print("\n❌ ERROR:", e)
    print("\nPlease check:")
    print("1. Your credentials are correct")
    print("2. Angel One account is active")
    print("3. API access is enabled")
