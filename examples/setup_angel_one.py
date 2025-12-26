#!/usr/bin/env python3
"""
Interactive setup for Angel One SmartAPI.

This script will:
1. Ask for your Angel One credentials
2. Test the connection
3. Download sample data to verify it works
4. Save credentials securely
"""

import getpass
from pathlib import Path

print("\n" + "=" * 80)
print("🔧 ANGEL ONE SMARTAPI SETUP")
print("=" * 80)

print("\n📋 I need 3 things from you:\n")
print("1. API Key (from Angel One web app → API section)")
print("2. Client ID (your Angel One login ID, e.g., A12345678)")
print("3. Password (your Angel One password/MPIN)")

print("\n" + "-" * 80)
print("⚠️  DON'T HAVE THESE YET?")
print("-" * 80)
print("1. Login to: https://smartapi.angelbroking.com/")
print("2. Go to 'My Profile' → 'My API Key'")
print("3. Click 'Create API Key'")
print("4. Copy the API Key")
print("\nThen come back here and run this script again.")
print("=" * 80)

proceed = input("\n✅ Do you have your API credentials ready? (yes/no): ").strip().lower()

if proceed not in ['yes', 'y']:
    print("\n👋 No problem! Get your credentials first, then run:")
    print("   python examples/setup_angel_one.py")
    exit(0)

print("\n" + "=" * 80)
print("📝 ENTER YOUR CREDENTIALS")
print("=" * 80)

# Get credentials
api_key = input("\n1️⃣  API Key: ").strip()
client_id = input("2️⃣  Client ID: ").strip()
password = getpass.getpass("3️⃣  Password (hidden): ").strip()

# Optional TOTP
print("\n🔐 Do you have 2FA/TOTP enabled? (if not sure, just press Enter)")
totp = input("   TOTP Token (optional): ").strip() or None

print("\n" + "=" * 80)
print("🔄 TESTING CONNECTION...")
print("=" * 80)

try:
    from SmartApi import SmartConnect
    
    print("\n1️⃣  Connecting to Angel One...", end=" ", flush=True)
    smart_api = SmartConnect(api_key=api_key)
    print("✅")
    
    print("2️⃣  Logging in...", end=" ", flush=True)
    data = smart_api.generateSession(client_id, password, totp)
    
    if not data['status']:
        print("❌")
        print(f"\n⚠️  Login failed: {data.get('message', 'Unknown error')}")
        print("\nPlease check your credentials and try again.")
        exit(1)
    
    print("✅")
    
    print("3️⃣  Getting user profile...", end=" ", flush=True)
    profile = smart_api.getProfile(data['data']['refreshToken'])
    print("✅")
    
    if profile['status']:
        user_data = profile['data']
        print(f"\n{'=' * 80}")
        print("✅ CONNECTION SUCCESSFUL!")
        print("=" * 80)
        print(f"\n👤 Name: {user_data.get('name', 'N/A')}")
        print(f"📧 Email: {user_data.get('email', 'N/A')}")
        print(f"📱 Mobile: {user_data.get('mobileno', 'N/A')}")
        print(f"💼 Client ID: {client_id}")
    
    # Test data download
    print(f"\n{'=' * 80}")
    print("📥 TESTING DATA DOWNLOAD")
    print("=" * 80)
    
    print("\n4️⃣  Downloading sample data for RELIANCE...", end=" ", flush=True)
    
    # Search for Reliance
    result = smart_api.searchScrip("NSE", "RELIANCE")
    if result['status'] and result['data']:
        token = result['data'][0]['symboltoken']
        
        from datetime import datetime, timedelta
        
        params = {
            "exchange": "NSE",
            "symboltoken": token,
            "interval": "ONE_DAY",
            "fromdate": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 09:00"),
            "todate": datetime.now().strftime("%Y-%m-%d 15:30")
        }
        
        candles = smart_api.getCandleData(params)
        
        if candles['status']:
            latest = candles['data'][-1]
            print("✅")
            print(f"\n   Latest RELIANCE price: ₹{latest[4]:.2f}")
            print(f"   Got {len(candles['data'])} days of data")
        else:
            print("⚠️  Could not fetch data")
    else:
        print("⚠️  Could not find RELIANCE symbol")
    
    # Save credentials to .env file
    print(f"\n{'=' * 80}")
    print("💾 SAVING CREDENTIALS")
    print("=" * 80)
    
    env_file = Path(".env")
    env_content = f"""# Angel One API Credentials
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANGEL_API_KEY={api_key}
ANGEL_CLIENT_ID={client_id}
ANGEL_PASSWORD={password}
"""
    
    if totp:
        env_content += f"ANGEL_TOTP={totp}\n"
    
    env_file.write_text(env_content)
    
    print(f"\n✅ Credentials saved to: {env_file.absolute()}")
    print("\n⚠️  IMPORTANT: Never commit .env file to git!")
    
    # Add to .gitignore
    gitignore = Path(".gitignore")
    if gitignore.exists():
        content = gitignore.read_text()
        if ".env" not in content:
            with gitignore.open("a") as f:
                f.write("\n# Environment variables\n.env\n")
            print("✅ Added .env to .gitignore")
    
    print(f"\n{'=' * 80}")
    print("🎉 SETUP COMPLETE!")
    print("=" * 80)
    print("\n✅ Angel One is configured and working!")
    print("\n📊 Next steps:")
    print("   1. Download historical data:")
    print("      python examples/download_angel_data.py")
    print("\n   2. Start live monitoring:")
    print("      python examples/live_monitor_angel.py")
    print("\n   3. Run backtests with real data!")
    print("=" * 80 + "\n")

except ImportError:
    print("❌")
    print("\n⚠️  SmartAPI library not installed!")
    print("\nRun: pip install smartapi-python")
    
except Exception as e:
    print("❌")
    print(f"\n⚠️  Error: {e}")
    print("\nPlease check your credentials and try again.")
