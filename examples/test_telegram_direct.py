#!/usr/bin/env python3
"""Test Telegram with direct credentials using curl."""

import subprocess
import json

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

print("\n📤 Sending test message to Telegram...\n")

send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    'chat_id': CHAT_ID,
    'text': '🎉 <b>Telegram Setup Successful!</b>\n\nYour algo trading framework is ready!\n\n✅ You will receive real-time trading signals here\n📈 Notifications for BUY/SELL/EXIT signals\n⚡ Ready to start monitoring stocks',
    'parse_mode': 'HTML',
    'disable_web_page_preview': True
}

curl_command = [
    'curl',
    '-k',
    '-X', 'POST',
    send_url,
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(payload),
    '--silent'
]

result = subprocess.run(
    curl_command,
    capture_output=True,
    text=True,
    timeout=15
)

if result.returncode == 0:
    try:
        response_data = json.loads(result.stdout)
        if response_data.get('ok'):
            print("✅ Message sent successfully!")
            print(f"\n📱 Check your Telegram app!")
            
            print("\n" + "=" * 80)
            print("✅ TELEGRAM CONFIGURED!")
            print("\nCredentials:")
            print(f"  BOT_TOKEN: {BOT_TOKEN}")
            print(f"  CHAT_ID: {CHAT_ID}")
            print("\n💡 These are now configured in your live signal monitor")
            print("=" * 80)
        else:
            print(f"❌ Failed: {response_data}")
    except json.JSONDecodeError:
        print(f"❌ Invalid response: {result.stdout}")
else:
    print(f"❌ curl failed: {result.stderr}")
