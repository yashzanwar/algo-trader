#!/usr/bin/env python3
"""Quick Telegram test - just run this after sending a message to your bot."""

import requests
import urllib3

# Disable SSL warnings (for corporate networks with self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "YOUR_BOT_TOKEN"

print("\n🔍 Checking for messages...\n")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url, timeout=10, verify=False)  # Disable SSL verification

print(f"Response status: {response.status_code}")
print(f"Response text: {response.text[:200]}")

if response.status_code != 200:
    print("\n❌ Telegram API is blocked by your network")
    print("💡 Your corporate firewall is blocking api.telegram.org")
    print("\n⚠️ Telegram notifications won't work on this network")
    print("\n📱 Alternative: Use Console and Desktop notifications instead")
    exit(1)

data = response.json()

print(f"Status: {data.get('ok')}")
print(f"Number of updates: {len(data.get('result', []))}")

if data.get('result'):
    for update in data['result'][-3:]:  # Show last 3 messages
        try:
            msg = update['message']
            print(f"\n📱 Message from:")
            print(f"   Chat ID: {msg['chat']['id']}")
            print(f"   Name: {msg['chat'].get('first_name', 'Unknown')}")
            print(f"   Text: {msg.get('text', 'N/A')}")
        except:
            print(f"   Update: {update}")
else:
    print("\n❌ No messages found!")
    print("\n💡 Please:")
    print("  1. Open Telegram")
    print("  2. Search for your bot")
    print("  3. Send 'hello' to the bot")
    print("  4. Run this script again")
