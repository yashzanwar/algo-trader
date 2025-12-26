"""Notification channels for trading signals."""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from typing import Protocol

from algotrader.core import get_logger

logger = get_logger(__name__)


class Notifier(ABC):
    """Abstract base class for signal notifiers."""
    
    @abstractmethod
    def send(self, event) -> bool:
        """Send notification for a signal event.
        
        Args:
            event: SignalEvent to notify
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass


class ConsoleNotifier(Notifier):
    """Print notifications to console with color formatting."""
    
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    def send(self, event) -> bool:
        """Print colored notification to console."""
        # Choose color based on signal type
        if event.signal_type == 'BUY':
            color = self.GREEN
            emoji = '🔔 📈'
        elif event.signal_type == 'SELL':
            color = self.RED
            emoji = '🔔 📉'
        else:
            color = self.YELLOW
            emoji = '🔔 ↔️'
        
        print("\n" + "=" * 80)
        print(f"{color}{self.BOLD}{emoji} TRADING SIGNAL ALERT{self.RESET}")
        print("=" * 80)
        print(f"{color}Signal Type:{self.RESET} {self.BOLD}{event.signal_type}{self.RESET}")
        print(f"Symbol:      {event.symbol}")
        print(f"Price:       ₹{event.price:.2f}")
        print(f"Strategy:    {event.strategy}")
        print(f"Reason:      {event.reason}")
        print(f"Time:        {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(f"\n{self.BOLD}Action Required:{self.RESET}")
        if event.signal_type == 'BUY':
            print(f"  1. Open your broker app (Zerodha/Upstox)")
            print(f"  2. Review current market conditions")
            print(f"  3. Place BUY order for {event.symbol} around ₹{event.price:.2f}")
        elif event.signal_type == 'SELL':
            print(f"  1. Open your broker app")
            print(f"  2. Place SELL order for {event.symbol} around ₹{event.price:.2f}")
        else:
            print(f"  1. Consider closing position in {event.symbol}")
        print("=" * 80 + "\n")
        
        return True


class EmailNotifier(Notifier):
    """Send email notifications via SMTP.
    
    Args:
        smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
        smtp_port: SMTP port (typically 587 for TLS)
        sender_email: Sender email address
        sender_password: Email password or app-specific password
        recipient_emails: List of recipient email addresses
    """
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_emails: list[str]
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_emails = recipient_emails
        
        logger.info(f"EmailNotifier configured: {sender_email} -> {len(recipient_emails)} recipients")
    
    def send(self, event) -> bool:
        """Send email alert."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔔 {event.signal_type} Signal: {event.symbol} @ ₹{event.price:.2f}"
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)
            
            # Email body
            text = str(event)
            html = f"""
            <html>
              <body>
                <h2 style="color: {'green' if event.signal_type == 'BUY' else 'red'};">
                  {event.signal_type} Signal Alert
                </h2>
                <table border="1" cellpadding="5">
                  <tr><td><b>Symbol</b></td><td>{event.symbol}</td></tr>
                  <tr><td><b>Price</b></td><td>₹{event.price:.2f}</td></tr>
                  <tr><td><b>Strategy</b></td><td>{event.strategy}</td></tr>
                  <tr><td><b>Reason</b></td><td>{event.reason}</td></tr>
                  <tr><td><b>Time</b></td><td>{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                </table>
                <p><b>Action:</b> Review and execute via your broker app.</p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {len(self.recipient_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False


class TelegramNotifier(Notifier):
    """Send Telegram notifications with bot command support.
    
    Setup:
    1. Create bot via @BotFather on Telegram
    2. Get bot token
    3. Get your chat ID (send message to bot, check https://api.telegram.org/bot<TOKEN>/getUpdates)
    
    Args:
        bot_token: Telegram bot token from BotFather
        chat_ids: List of Telegram chat IDs to notify
        position_manager: Optional PositionManager for tracking positions
    """
    
    def __init__(self, bot_token: str, chat_ids: list[str], position_manager=None):
        self.bot_token = bot_token
        self.chat_ids = chat_ids
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.position_manager = position_manager
        self.last_update_id = 0
        
        logger.info(f"TelegramNotifier configured: {len(chat_ids)} chats")
    
    def send(self, event) -> bool:
        """Send Telegram message using curl subprocess."""
        try:
            import subprocess
            import json
            
            # Format message
            emoji = "📈" if event.signal_type == 'BUY' else "📉" if event.signal_type == 'SELL' else "↔️"
            message = (
                f"{emoji} <b>{event.signal_type} SIGNAL</b>\n\n"
                f"<b>Symbol:</b> {event.symbol}\n"
                f"<b>Price:</b> ₹{event.price:.2f}\n"
                f"<b>Strategy:</b> {event.strategy}\n"
                f"<b>Reason:</b> {event.reason}\n"
                f"<b>Time:</b> {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"⚡ <i>Review and execute via your broker</i>"
            )
            
            # Send to all chat IDs using curl
            for chat_id in self.chat_ids:
                url = f"{self.api_url}/sendMessage"
                
                # Prepare JSON payload
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }
                
                # Use curl with -k to bypass SSL verification
                curl_command = [
                    'curl',
                    '-k',  # Disable SSL verification
                    '-X', 'POST',
                    url,
                    '-H', 'Content-Type: application/json',
                    '-d', json.dumps(payload),
                    '--silent',  # Don't show progress
                    '--max-time', '10'  # Timeout after 10 seconds
                ]
                
                result = subprocess.run(
                    curl_command,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode != 0:
                    logger.error(f"curl failed for chat {chat_id}: {result.stderr}")
                    return False
                
                # Check if Telegram API returned success
                try:
                    response_data = json.loads(result.stdout)
                    if not response_data.get('ok'):
                        logger.error(f"Telegram API error: {response_data}")
                        return False
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON response: {result.stdout}")
                    return False
            
            logger.info(f"Telegram sent to {len(self.chat_ids)} chats via curl")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Telegram send timeout")
            return False
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False    
    def send_message(self, chat_id: str, message: str) -> bool:
        """Send a plain text message to a chat."""
        try:
            import subprocess
            import json
            
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            curl_command = [
                'curl', '-k', '-X', 'POST', url,
                '-H', 'Content-Type: application/json',
                '-d', json.dumps(payload),
                '--silent', '--max-time', '10'
            ]
            
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout)
                    return response_data.get('ok', False)
                except json.JSONDecodeError:
                    return False
            return False
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def process_commands(self, price_fetcher=None):
        """
        Process incoming bot commands from Telegram.
        
        Commands:
        - /bought SYMBOL QUANTITY PRICE - Add a position
        - /sold SYMBOL - Remove a position
        - /positions - List all positions
        - /status - Show overall status
        - /help - Show help
        
        Args:
            price_fetcher: Function to get current price for a symbol (optional)
        """
        if not self.position_manager:
            return
        
        try:
            import subprocess
            import json
            
            url = f"{self.api_url}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 0}
            
            curl_command = [
                'curl', '-k', '-X', 'GET',
                f"{url}?offset={params['offset']}&timeout={params['timeout']}",
                '--silent', '--max-time', '5'
            ]
            
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.debug(f"Curl failed: {result.stderr}")
                return
            
            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.debug(f"JSON decode error: {e}")
                return
            
            if not response.get('ok'):
                logger.warning(f"Telegram API error: {response.get('description', 'Unknown')}")
                return
            
            updates = response.get('result', [])
            
            if updates:
                logger.info(f"Processing {len(updates)} Telegram command(s)")
            
            for update in updates:
                self.last_update_id = update['update_id']
                
                if 'message' not in update:
                    continue
                
                message = update['message']
                chat_id = str(message['chat']['id'])
                text = message.get('text', '').strip()
                
                # Only process commands from authorized chat IDs
                if chat_id not in self.chat_ids:
                    logger.warning(f"Unauthorized chat ID: {chat_id}")
                    continue
                
                logger.info(f"Processing command: {text} from chat {chat_id}")
                
                # Process commands
                if text.startswith('/bought'):
                    self._handle_bought_command(chat_id, text, price_fetcher)
                elif text.startswith('/sold'):
                    self._handle_sold_command(chat_id, text, price_fetcher)
                elif text.startswith('/positions'):
                    self._handle_positions_command(chat_id)
                elif text.startswith('/status'):
                    self._handle_status_command(chat_id, price_fetcher)
                elif text.startswith('/help'):
                    self._handle_help_command(chat_id)
        
        except subprocess.TimeoutExpired:
            logger.error("Telegram getUpdates timeout")
        except Exception as e:
            logger.error(f"Error processing commands: {e}", exc_info=True)
    
    def _handle_bought_command(self, chat_id: str, text: str, price_fetcher):
        """Handle /bought SYMBOL QUANTITY PRICE command."""
        try:
            parts = text.split()
            if len(parts) < 4:
                self.send_message(chat_id, 
                    "❌ Usage: /bought SYMBOL QUANTITY PRICE\n"
                    "Example: /bought RELIANCE 10 2850"
                )
                return
            
            symbol = parts[1].upper()
            quantity = float(parts[2])
            price = float(parts[3])
            
            position = self.position_manager.add_position(symbol, quantity, price)
            
            message = (
                f"✅ <b>Position Added</b>\n\n"
                f"Symbol: {symbol}\n"
                f"Quantity: {quantity}\n"
                f"Entry Price: ₹{price:.2f}\n"
                f"Total Value: ₹{quantity * price:.2f}\n"
                f"Time: {position.entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"🔔 Now monitoring for EXIT signals"
            )
            self.send_message(chat_id, message)
            
        except ValueError:
            self.send_message(chat_id, "❌ Invalid format. Use numbers for QUANTITY and PRICE")
        except Exception as e:
            self.send_message(chat_id, f"❌ Error: {str(e)}")
    
    def _handle_sold_command(self, chat_id: str, text: str, price_fetcher):
        """Handle /sold SYMBOL command."""
        try:
            parts = text.split()
            if len(parts) < 2:
                self.send_message(chat_id, 
                    "❌ Usage: /sold SYMBOL\n"
                    "Example: /sold RELIANCE"
                )
                return
            
            symbol = parts[1].upper()
            position = self.position_manager.get_position(symbol)
            
            if not position:
                self.send_message(chat_id, f"❌ No position found for {symbol}")
                return
            
            # Calculate P&L if price fetcher available
            pnl_text = ""
            if price_fetcher:
                try:
                    current_price = price_fetcher(symbol)
                    pnl_data = position.current_pnl(current_price)
                    pnl_emoji = "📈" if pnl_data['pnl'] > 0 else "📉"
                    pnl_text = (
                        f"\n\n{pnl_emoji} <b>P&L Summary</b>\n"
                        f"Exit Price: ₹{current_price:.2f}\n"
                        f"P&L: ₹{pnl_data['pnl']:.2f} ({pnl_data['pnl_pct']:+.2f}%)"
                    )
                except:
                    pass
            
            self.position_manager.remove_position(symbol)
            
            message = (
                f"✅ <b>Position Closed</b>\n\n"
                f"Symbol: {symbol}\n"
                f"Quantity: {position.quantity}\n"
                f"Entry Price: ₹{position.entry_price:.2f}"
                f"{pnl_text}\n\n"
                f"🔔 Now monitoring for BUY signals"
            )
            self.send_message(chat_id, message)
            
        except Exception as e:
            self.send_message(chat_id, f"❌ Error: {str(e)}")
    
    def _handle_positions_command(self, chat_id: str):
        """Handle /positions command."""
        positions = self.position_manager.list_positions()
        
        if not positions:
            self.send_message(chat_id, "📊 No active positions")
            return
        
        message = "📊 <b>Active Positions</b>\n\n"
        total_value = 0
        
        for pos in positions:
            value = pos.quantity * pos.entry_price
            total_value += value
            message += (
                f"<b>{pos.symbol}</b>\n"
                f"  Qty: {pos.quantity} @ ₹{pos.entry_price:.2f}\n"
                f"  Value: ₹{value:.2f}\n"
                f"  Entry: {pos.entry_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            )
        
        message += f"<b>Total Value:</b> ₹{total_value:.2f}"
        self.send_message(chat_id, message)
    
    def _handle_status_command(self, chat_id: str, price_fetcher):
        """Handle /status command with live P&L."""
        positions = self.position_manager.list_positions()
        
        if not positions:
            self.send_message(chat_id, "📊 No active positions")
            return
        
        message = "📊 <b>Portfolio Status</b>\n\n"
        total_invested = 0
        total_current = 0
        
        for pos in positions:
            invested = pos.quantity * pos.entry_price
            total_invested += invested
            
            # Try to get current price
            current_price = pos.entry_price
            if price_fetcher:
                try:
                    current_price = price_fetcher(pos.symbol)
                except:
                    pass
            
            pnl_data = pos.current_pnl(current_price)
            current_value = pos.quantity * current_price
            total_current += current_value
            
            pnl_emoji = "📈" if pnl_data['pnl'] > 0 else "📉" if pnl_data['pnl'] < 0 else "➖"
            
            message += (
                f"<b>{pos.symbol}</b>\n"
                f"  Entry: ₹{pos.entry_price:.2f} → Current: ₹{current_price:.2f}\n"
                f"  {pnl_emoji} P&L: ₹{pnl_data['pnl']:.2f} ({pnl_data['pnl_pct']:+.2f}%)\n\n"
            )
        
        overall_pnl = total_current - total_invested
        overall_pnl_pct = (overall_pnl / total_invested * 100) if total_invested > 0 else 0
        overall_emoji = "📈" if overall_pnl > 0 else "📉" if overall_pnl < 0 else "➖"
        
        message += (
            f"<b>Overall</b>\n"
            f"  Invested: ₹{total_invested:.2f}\n"
            f"  Current: ₹{total_current:.2f}\n"
            f"  {overall_emoji} P&L: ₹{overall_pnl:.2f} ({overall_pnl_pct:+.2f}%)"
        )
        
        self.send_message(chat_id, message)
    
    def _handle_help_command(self, chat_id: str):
        """Handle /help command."""
        message = (
            "<b>📱 Bot Commands</b>\n\n"
            "<b>/bought SYMBOL QTY PRICE</b>\n"
            "  Add a position you've bought\n"
            "  Example: /bought RELIANCE 10 2850\n\n"
            "<b>/sold SYMBOL</b>\n"
            "  Close a position you've sold\n"
            "  Example: /sold RELIANCE\n\n"
            "<b>/positions</b>\n"
            "  List all active positions\n\n"
            "<b>/status</b>\n"
            "  Show portfolio status with live P&L\n\n"
            "<b>/help</b>\n"
            "  Show this help message\n\n"
            "💡 The bot will monitor your positions and send EXIT signals when it's time to sell!"
        )
        self.send_message(chat_id, message)

class DesktopNotifier(Notifier):
    """Send desktop notifications (macOS/Linux/Windows)."""
    
    def send(self, event) -> bool:
        """Send desktop notification."""
        try:
            # Try macOS notification
            if os.system('which osascript > /dev/null 2>&1') == 0:
                title = f"{event.signal_type} Signal: {event.symbol}"
                message = f"₹{event.price:.2f} - {event.reason}"
                sound = "default"
                
                script = f'''
                    osascript -e 'display notification "{message}" with title "{title}" sound name "{sound}"'
                '''
                os.system(script)
                logger.info("Desktop notification sent (macOS)")
                return True
            
            # Try Linux notify-send
            elif os.system('which notify-send > /dev/null 2>&1') == 0:
                title = f"{event.signal_type} Signal: {event.symbol}"
                message = f"₹{event.price:.2f} - {event.reason}"
                os.system(f'notify-send "{title}" "{message}"')
                logger.info("Desktop notification sent (Linux)")
                return True
            
            # Fallback to console
            else:
                logger.warning("Desktop notifications not supported, using console")
                return ConsoleNotifier().send(event)
                
        except Exception as e:
            logger.error(f"Desktop notification failed: {e}")
            return False


class MultiNotifier(Notifier):
    """Send notifications through multiple channels.
    
    Args:
        notifiers: List of notifier instances
    """
    
    def __init__(self, notifiers: list[Notifier]):
        self.notifiers = notifiers
        logger.info(f"MultiNotifier configured with {len(notifiers)} channels")
    
    def send(self, event) -> bool:
        """Send through all notifiers."""
        results = []
        for notifier in self.notifiers:
            try:
                success = notifier.send(event)
                results.append(success)
            except Exception as e:
                logger.error(f"{notifier.__class__.__name__} failed: {e}")
                results.append(False)
        
        return any(results)  # Success if at least one notifier worked
