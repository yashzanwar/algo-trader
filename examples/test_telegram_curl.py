#!/usr/bin/env python3
"""Test Telegram with your credentials using curl."""

import subprocess
import json

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = None  # Will get from bot messages

print("\n🔍 Getting your Chat ID...\n")

# First, get updates to find chat ID
print("📱 Please send any message to your bot in Telegram")
print("   (Go to Telegram and message your bot now)")
input("\n✅ Press Enter after you've sent a message to the bot...")

# Get updates using curl
get_updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

curl_command = [
    'curl',
    '-k',
    '-X', 'GET',
    get_updates_url,
    '--silent'
]

print("\n🔍 Fetching messages...")

result = subprocess.run(
    curl_command,
    capture_output=True,
    text=True,
    timeout=15
)

if result.returncode == 0:
    try:
        response_data = json.loads(result.stdout)
        if response_data.get('ok') and response_data.get('result'):
            updates = response_data['result']
            if updates:
                # Get the most recent message
                latest_update = updates[-1]
                CHAT_ID = str(latest_update['message']['chat']['id'])
                print(f"✅ Found your Chat ID: {CHAT_ID}")
                
                # Now send a test message
                print("\n📤 Sending test message...")
                
                send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    'chat_id': CHAT_ID,
                    'text': '🎉 <b>Telegram Setup Successful!</b>\n\nYour algo trading framework can now send you notifications.\n\n✅ Ready to receive trading signals!',
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }
                
                send_curl = [
                    'curl',
                    '-k',
                    '-X', 'POST',
                    send_url,
                    '-H', 'Content-Type: application/json',
                    '-d', json.dumps(payload),
                    '--silent'
                ]
                
                send_result = subprocess.run(
                    send_curl,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if send_result.returncode == 0:
                    send_data = json.loads(send_result.stdout)
                    if send_data.get('ok'):
                        print("✅ Test message sent successfully!")
                        print(f"\n📱 Check your Telegram app!")
                        
                        print("\n" + "=" * 80)
                        print("✅ Telegram is configured and working!")
                        print("\nYour credentials:")
                        print(f"  BOT_TOKEN: {BOT_TOKEN}")
                        print(f"  CHAT_ID: {CHAT_ID}")
                        print("\n💡 Update live_signal_monitor.py with these credentials")
                        print("=" * 80)
                    else:
                        print(f"❌ Failed to send: {send_data}")
                else:
                    print(f"❌ curl failed: {send_result.stderr}")
            else:
                print("❌ No messages found. Please send a message to your bot first.")
        else:
            print(f"❌ API error: {response_data}")
    except json.JSONDecodeError:
        print(f"❌ Invalid response: {result.stdout}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print(f"❌ curl failed: {result.stderr}")
