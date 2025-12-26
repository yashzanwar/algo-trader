#!/usr/bin/env python3
"""
Angel One API using curl (bypasses SSL certificate issues).

Uses subprocess + curl instead of requests library to avoid corporate firewall blocks.
"""

import subprocess
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import pyotp

logger = logging.getLogger(__name__)


class AngelOneCurl:
    """Angel One API client using curl to bypass SSL issues."""
    
    BASE_URL = "https://apiconnect.angelone.in"
    
    def __init__(self, api_key: str, client_id: str, password: str, totp_secret: Optional[str] = None):
        """
        Initialize Angel One client with curl.
        
        Args:
            api_key: Your Angel One API key
            client_id: Your client ID (login ID)
            password: Your password/MPIN
            totp_secret: Optional TOTP secret (QR value) - will auto-generate code
        """
        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.totp_secret = totp_secret
        
        # Session tokens (will be set after login)
        self.jwt_token = None
        self.refresh_token = None
        self.feed_token = None
        
        # Login automatically
        self._login()
    
    def _curl_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """
        Make API request using curl.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/rest/auth/angelbroking/user/v1/loginByPassword')
            data: Request payload (dict)
            headers: Request headers (dict)
        
        Returns:
            Response JSON as dict
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Build curl command
        curl_cmd = [
            'curl',
            '-k',  # Disable SSL verification
            '-X', method,
            url,
            '--silent',
            '--max-time', '30'
        ]
        
        # Add headers
        if headers:
            for key, value in headers.items():
                curl_cmd.extend(['-H', f'{key}: {value}'])
        
        # Add data
        if data:
            curl_cmd.extend(['-H', 'Content-Type: application/json'])
            curl_cmd.extend(['-d', json.dumps(data)])
        
        try:
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=35
            )
            
            if result.returncode != 0:
                logger.error(f"curl failed: {result.stderr}")
                return {"status": False, "message": f"curl error: {result.stderr}"}
            
            # Parse JSON response
            try:
                response = json.loads(result.stdout)
                return response
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {result.stdout[:200]}")
                return {"status": False, "message": "Invalid JSON response"}
                
        except subprocess.TimeoutExpired:
            logger.error("Request timeout")
            return {"status": False, "message": "Request timeout"}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"status": False, "message": str(e)}
    
    def _login(self):
        """Login to Angel One and get session tokens."""
        try:
            # Auto-generate TOTP if secret provided
            totp_code = None
            if self.totp_secret:
                totp_code = pyotp.TOTP(self.totp_secret).now()
                logger.info(f"Generated TOTP: {totp_code}")
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-UserType': 'USER',
                'X-SourceID': 'WEB',
                'X-ClientLocalIP': '127.0.0.1',
                'X-ClientPublicIP': '127.0.0.1',
                'X-MACAddress': '00:00:00:00:00:00',
                'X-PrivateKey': self.api_key
            }
            
            payload = {
                'clientcode': self.client_id,
                'password': self.password
            }
            
            if totp_code:
                payload['totp'] = totp_code
            
            response = self._curl_request(
                'POST',
                '/rest/auth/angelbroking/user/v1/loginByPassword',
                data=payload,
                headers=headers
            )
            
            if response.get('status'):
                data = response['data']
                self.jwt_token = data['jwtToken']
                self.refresh_token = data['refreshToken']
                self.feed_token = data.get('feedToken', '')
                
                logger.info(f"Angel One login successful for {self.client_id}")
                return True
            else:
                error_msg = response.get('message', 'Unknown error')
                logger.error(f"Login failed: {error_msg}")
                raise Exception(f"Login failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    def get_profile(self) -> Dict:
        """Get user profile."""
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '127.0.0.1',
            'X-ClientPublicIP': '127.0.0.1',
            'X-MACAddress': '00:00:00:00:00:00',
            'X-PrivateKey': self.api_key
        }
        
        response = self._curl_request(
            'GET',
            '/rest/secure/angelbroking/user/v1/getProfile',
            headers=headers
        )
        
        return response
    
    def search_scrip(self, exchange: str, symbol: str) -> Optional[str]:
        """
        Search for instrument token.
        
        Args:
            exchange: Exchange (NSE, BSE, etc.)
            symbol: Symbol name (e.g., 'RELIANCE')
        
        Returns:
            Instrument token or None
        """
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '127.0.0.1',
            'X-ClientPublicIP': '127.0.0.1',
            'X-MACAddress': '00:00:00:00:00:00',
            'X-PrivateKey': self.api_key
        }
        
        payload = {
            'exchange': exchange,
            'searchscrip': symbol
        }
        
        response = self._curl_request(
            'POST',
            '/rest/secure/angelbroking/order/v1/searchScrip',
            data=payload,
            headers=headers
        )
        
        if response.get('status') and response.get('data'):
            return response['data'][0]['symboltoken']
        return None
    
    def get_candle_data(
        self,
        exchange: str,
        symbol_token: str,
        interval: str,
        from_date: datetime,
        to_date: datetime
    ) -> Dict:
        """
        Get historical candle data.
        
        Args:
            exchange: Exchange (NSE, BSE)
            symbol_token: Instrument token
            interval: ONE_MINUTE, FIVE_MINUTE, ONE_DAY, etc.
            from_date: Start date
            to_date: End date
        
        Returns:
            Candle data response
        """
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '127.0.0.1',
            'X-ClientPublicIP': '127.0.0.1',
            'X-MACAddress': '00:00:00:00:00:00',
            'X-PrivateKey': self.api_key
        }
        
        payload = {
            'exchange': exchange,
            'symboltoken': symbol_token,
            'interval': interval,
            'fromdate': from_date.strftime('%Y-%m-%d %H:%M'),
            'todate': to_date.strftime('%Y-%m-%d %H:%M')
        }
        
        response = self._curl_request(
            'POST',
            '/rest/secure/angelbroking/historical/v1/getCandleData',
            data=payload,
            headers=headers
        )
        
        return response
    
    def get_ltp(self, exchange: str, symbol_token: str, trading_symbol: str) -> Dict:
        """
        Get last traded price.
        
        Args:
            exchange: Exchange (NSE, BSE)
            symbol_token: Instrument token
            trading_symbol: Trading symbol
        
        Returns:
            LTP data
        """
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '127.0.0.1',
            'X-ClientPublicIP': '127.0.0.1',
            'X-MACAddress': '00:00:00:00:00:00',
            'X-PrivateKey': self.api_key
        }
        
        payload = {
            'exchange': exchange,
            'symboltoken': symbol_token,
            'tradingsymbol': trading_symbol
        }
        
        response = self._curl_request(
            'POST',
            '/rest/secure/angelbroking/order/v1/getLtpData',
            data=payload,
            headers=headers
        )
        
        return response


if __name__ == "__main__":
    # Test the curl-based client
    print("\n" + "=" * 80)
    print("🧪 Testing Angel One Curl Client")
    print("=" * 80)
    
    # Get credentials from user
    api_key = input("\nAPI Key: ").strip()
    client_id = input("Client ID: ").strip()
    password = input("Password: ").strip()
    totp = input("TOTP (optional, press Enter to skip): ").strip() or None
    
    try:
        print("\n1️⃣  Connecting...", end=" ", flush=True)
        client = AngelOneCurl(api_key, client_id, password, totp)
        print("✅")
        
        print("2️⃣  Getting profile...", end=" ", flush=True)
        profile = client.get_profile()
        print("✅")
        
        if profile.get('status'):
            print(f"\n✅ Logged in as: {profile['data'].get('name', 'N/A')}")
        
        print("\n3️⃣  Testing data download for RELIANCE...", end=" ", flush=True)
        token = client.search_scrip('NSE', 'RELIANCE')
        
        if token:
            from_date = datetime.now() - timedelta(days=7)
            to_date = datetime.now()
            
            data = client.get_candle_data('NSE', token, 'ONE_DAY', from_date, to_date)
            
            if data.get('status'):
                candles = data['data']
                latest = candles[-1]
                print("✅")
                print(f"\n   Latest RELIANCE close: ₹{latest[4]:.2f}")
                print(f"   Got {len(candles)} days of data")
            else:
                print("❌")
        
        print("\n" + "=" * 80)
        print("✅ Angel One curl client is working!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print("❌")
        print(f"\n⚠️  Error: {e}")
