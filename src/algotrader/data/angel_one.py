"""Angel One SmartAPI data source integration using curl."""

from datetime import datetime, timedelta
import pandas as pd
from typing import Optional
import logging

from algotrader.data.source import DataSource
from algotrader.data.angel_curl import AngelOneCurl

logger = logging.getLogger(__name__)


class AngelOneDataSource(DataSource):
    """
    Angel One SmartAPI data source for live and historical market data.
    Uses curl to bypass SSL certificate issues.
    
    Features:
    - Real-time market data (live prices)
    - Historical data for backtesting
    - FREE with Angel One account
    - Works on corporate networks (uses curl)
    """
    
    def __init__(
        self,
        api_key: str,
        client_id: str,
        password: str,
        totp_secret: Optional[str] = None
    ):
        """
        Initialize Angel One data source.
        
        Args:
            api_key: Your Angel One API key
            client_id: Your Angel One client ID (login ID)
            password: Your Angel One password/MPIN
            totp_secret: TOTP secret (QR value) for auto-generating codes
        """
        self.client = AngelOneCurl(api_key, client_id, password, totp_secret)
        self._token_cache = {}  # Cache instrument tokens
        
        logger.info(f"AngelOne connected for client: {client_id}")
    
    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate Angel One data - already validated by curl client."""
        return df
    
    def load(
        self,
        symbol: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        interval: str = "ONE_DAY"
    ) -> pd.DataFrame:
        """
        Load historical data from Angel One.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS' or just 'RELIANCE')
            from_date: Start date (default: 2 years ago)
            to_date: End date (default: today)
            interval: Candle interval (ONE_DAY, ONE_MINUTE, FIVE_MINUTE, etc.)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Clean symbol (remove .NS suffix if present)
            clean_symbol = symbol.replace('.NS', '').replace('-EQ', '')
            
            # Default date range: 2 years
            if from_date is None:
                from_date = datetime.now() - timedelta(days=730)
            if to_date is None:
                to_date = datetime.now()
            
            # Get instrument token (with caching)
            token = self._get_token(clean_symbol)
            
            if not token:
                raise Exception(f"Symbol not found: {symbol}")
            
            # Fetch historical data
            response = self.client.get_candle_data(
                exchange='NSE',
                symbol_token=token,
                interval=interval,
                from_date=from_date,
                to_date=to_date
            )
            
            if not response.get('status'):
                raise Exception(f"Failed to fetch data: {response.get('message')}")
            
            # Convert to DataFrame
            candles = response['data']
            df = pd.DataFrame(
                candles,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Ensure numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            logger.info(f"Loaded {len(df)} bars for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load data for {symbol}: {e}")
            raise
    
    def get_live_price(self, symbol: str) -> dict:
        """
        Get current live price for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS' or just 'RELIANCE')
        
        Returns:
            Dict with live market data
        """
        try:
            clean_symbol = symbol.replace('.NS', '').replace('-EQ', '')
            token = self._get_token(clean_symbol)
            
            if not token:
                raise Exception(f"Symbol not found: {symbol}")
            
            # Try to get LTP first
            try:
                response = self.client.get_ltp('NSE', token, clean_symbol)
                
                if response.get('status'):
                    data = response['data']
                    return {
                        'symbol': symbol,
                        'ltp': float(data.get('ltp', 0)),
                        'open': float(data.get('open', 0)),
                        'high': float(data.get('high', 0)),
                        'low': float(data.get('low', 0)),
                        'close': float(data.get('close', 0)),
                        'timestamp': datetime.now()
                    }
            except Exception as ltp_error:
                logger.warning(f"LTP failed for {symbol}, trying candle data: {ltp_error}")
            
            # Fallback: Get latest 1-day candle (today's OHLC)
            today = datetime.now()
            yesterday = today - timedelta(days=2)
            
            response = self.client.get_candle_data(
                exchange='NSE',
                symbol_token=token,
                interval='ONE_DAY',
                from_date=yesterday,
                to_date=today
            )
            
            if response.get('status') and response.get('data'):
                latest_candle = response['data'][-1]  # Last candle
                return {
                    'symbol': symbol,
                    'ltp': float(latest_candle[4]),  # Close price
                    'open': float(latest_candle[1]),
                    'high': float(latest_candle[2]),
                    'low': float(latest_candle[3]),
                    'close': float(latest_candle[4]),
                    'timestamp': datetime.now()
                }
            else:
                raise Exception(f"Failed to get quote: {response.get('message')}")
                
        except Exception as e:
            logger.error(f"Failed to get live price for {symbol}: {e}")
            raise
    
    def _get_token(self, symbol: str) -> Optional[str]:
        """Get instrument token with caching."""
        if symbol in self._token_cache:
            return self._token_cache[symbol]
        
        token = self.client.search_scrip('NSE', symbol)
        if token:
            self._token_cache[symbol] = token
        
        return token
