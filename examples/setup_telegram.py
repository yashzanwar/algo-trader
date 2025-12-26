#!/usr/bin/env python3
"""Get your Telegram Chat ID - Run this once to set up notifications."""

import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"

def get_chat_id():
    """Get your Telegram chat ID."""
    
    print("\n" + "=" * 80)
    print("📱 TELEGRAM SETUP - Get Your Chat ID")
    print("=" * 80)
    print("\n📋 Instructions:")
    print("  1. Open Telegram app")
    print("  2. Search for your bot (the name you gave it)")
    print("  3. Send any message to your bot (e.g., 'hello')")
    print("  4. Come back here and press Enter\n")
    
    input("Press Enter after you've sent a message to your bot...")
    
    print("\n🔍 Fetching your chat ID...\n")
    
    # Get updates from Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('ok'):
            print("❌ Error: Unable to fetch updates from Telegram")
            print(f"Response: {data}")
            return
        
        updates = data.get('result', [])
        
        if not updates:
            print("❌ No messages found!")
            print("\n💡 Make sure you:")
            print("  1. Actually sent a message to your bot")
            print("  2. Sent it to the correct bot")
            print("  3. Have internet connection")
            return
        
        # Get the latest message
        latest_update = updates[-1]
        chat_id = latest_update['message']['chat']['id']
        username = latest_update['message']['chat'].get('username', 'Unknown')
        first_name = latest_update['message']['chat'].get('first_name', 'Unknown')
        
        print("✅ Chat ID Found!\n")
        print("=" * 80)
        print(f"📱 Your Telegram Details:")
        print(f"   Chat ID:    {chat_id}")
        print(f"   Username:   @{username}")
        print(f"   Name:       {first_name}")
        print("=" * 80)
        
        print("\n✅ Setup Complete! Use this in your code:")
        print("\n" + "-" * 80)
        print(f"""
telegram_notifier = TelegramNotifier(
    bot_token='{BOT_TOKEN}',
    chat_ids=['{chat_id}']
)
""")
        print("-" * 80)
        
        # Test notification
        print("\n📤 Sending test notification...")
        test_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        test_data = {
            'chat_id': chat_id,
            'text': '🎉 <b>Telegram Notifications Activated!</b>\n\nYour algo trading signals will now be sent here.\n\n✅ Setup successful!',
            'parse_mode': 'HTML'
        }
        
        test_response = requests.post(test_url, data=test_data, timeout=10)
        
        if test_response.json().get('ok'):
            print("✅ Test notification sent! Check your Telegram app.")
        else:
            print("⚠️ Test notification failed, but chat ID is correct.")
        
        print("\n🚀 You're all set! Run live_signal_monitor.py to get trading alerts.\n")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("\n💡 Make sure you have internet connection and try again.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    get_chat_id()
