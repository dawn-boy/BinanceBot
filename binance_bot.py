from typing import Optional, Dict, Any
from binance.client import Client
from binance.exceptions ipmort BinanceAPIException, BinanceRequestException
from logger import logger
import json
import os
from dotenv import load_dotenv

load_dotenv()

class BinanceBot:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        try:
            self.client = Client(api_key, api_key, testnet=testnet)
            if testnet:
                self.client.API_URL = 'https://testnet.binancefuture.com'
            logger.info("BinanceBot is Initialized!")
            logger.info(f"Using {"TestNet" if testnet else "Main Account"}")

            self._test_connection()
        
        except Exception as e:
            logger.error("Falied to initialze BinanceBot: {str(e)}")
            raise

    def _test_connection(self):
        try:
            account_info = self.client.futures_account()
            logger.info("Connection to Binance Futures is Succesfull!")
            logger.info(F"Account Balance: {account_info.get("totalWalletBalance", "N/A")}")

        except Exception as e:
            logger.error("Connection test failed: {str(e)}")
            raise
        
    def _validate_symbol(self, symbol: str) -> bool:
        try:
            exchange_info = self.client.futures_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols']]
            return symbol.upper() in symbols

        except:
            logger.error("Verification of input symbol failed: {str(e)}")
            return False
    
    def _log_request(self, order_type: str, params: Dict[str, Any]):
        logger.info(f"API Request - Order type: {order_type}")
        logger.info(f"Params: {json.dumps(params, indent=2)}")

    def _log_response(self, response: Dict[str, Any]):
        logger.info(f"API Response: {json.dumps(response, indent=2)}")
    
    def place_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:

        side = side.upper()
        symbol = symbol.upper()
        if side not in ['BUY', 'SELL']:
            logger.error(f"Invalid side: {side}. Must be BUY or SELL")
            return None

        if not self._validate_symbol(symbol):
            logger.error(f"Invalid Symbol: {symbol}")
            return None

        if quantity <= 0:
            logger.error(f"Invalid quantity: {quantity}. Must be above 0.")
            return None

        params = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': quantity
        }

        try:
            self._log_request('MARKET', params)
            order = self.client.futures_create_order(**params)
            self._log_response(order)

            logger.info(f"Market order is placed.")
            logger.info(f"Order ID: {order['orderId']}")
            logger.info(f"Status: {order['status']}")

            return order

        except BinanceAPIException as e:
            logger.error(f"Binance API Error: {e.status_code} - {e.message}")
            return None
        except BinanceRequestException as e:
            logger.error(f"Binance Request Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error occured while placing market order: {str(e)}")
            return None

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, time_in_force: str = "GTC") -> Optional[Dict]:
        
        side = side.upper()
        symbol = symbol.upper()
        time_in_force = time_in_force.upper()
        if side not in ['BUY', 'SELL']:
            logger.error(f"Invalid side: {side}. Must be BUY or SELL")
            return None
        
        if not self._validate_symbol(symbol):
            logger.error(f"Invalid symbol: {symbol}")
            return None
        
        if quantity <= 0:
            logger.error(f"Invalid quantity: {quantity}. Must be above 0")
            return None
        
        if price <= 0:
            logger.error(f"Invalid price: {price}. Must be above 0")
            return None
        
        if time_in_force not in ['GTC', 'IOC', 'FOK']:
            logger.error(f"Invalid time_in_force: {time_in_force}")
            return None
        
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'quantity': quantity,
            'price': price,
            'timeInForce': time_in_force
        }
        
        try:
            self._log_request('LIMIT', params)
            order = self.client.futures_create_order(**params)
            self._log_response(order)
            
            logger.info(f"Limit order has been placed")
            logger.info(f"Order ID: {order['orderId']}")
            logger.info(f"Status: {order['status']}")
            
            return order
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Error: {e.status_code} - {e.message}")
            return None
        except BinanceRequestException as e:
            logger.error(f"Binance Request Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error placing limit order: {str(e)}")
            return None

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float,
                              stop_price: float, limit_price: float,
                              time_in_force: str = 'GTC') -> Optional[Dict]:

        side = side.upper()
        symbol = symbol.upper()
        time_in_force = time_in_force.upper()
        
        if side not in ['BUY', 'SELL']:
            logger.error(f"Invalid side: {side}")
            return None
        
        if not self._validate_symbol(symbol):
            logger.error(f"Invalid symbol: {symbol}")
            return None
        
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'STOP',
            'quantity': quantity,
            'price': limit_price,
            'stopPrice': stop_price,
            'timeInForce': time_in_force
        }
        
        try:
            self._log_request('STOP_LIMIT', params)
            order = self.client.futures_create_order(**params)
            self._log_response(order)
            
            logger.info(f"Stop-limit order placed successfully")
            logger.info(f"Order ID: {order['orderId']}")
            
            return order
            
        except Exception as e:
            logger.error(f"Error placing stop-limit order: {str(e)}")
            return None

    def get_account_balance(self) -> Optional[Dict]:
        try:
            account = self.client.futures_account()
            balance_info = {
                'totalWalletBalance': account.get('totalWalletBalance'),
                'availableBalance': account.get('availableBalance'),
                'assets': [
                    {
                        'asset': asset['asset'],
                        'balance': asset['walletBalance'],
                        'available': asset['availableBalance']
                    }
                    for asset in account.get('assets', [])
                    if float(asset['walletBalance']) > 0
                ]
            }
            logger.info("Account balance has been retrieved.")
            return balance_info
        except Exception as e:
            logger.error(f"Error getting account balance: {str(e)}")
            return None

    def get_open_orders(self, symbol: Optional[str] = None) -> Optional[list]:
            try:
                if symbol:
                    orders = self.client.futures_get_open_orders(symbol=symbol.upper())
                else:
                    orders = self.client.futures_get_open_orders()
                
                logger.info(f"Retrieved {len(orders)} open orders")
                return orders
            except Exception as e:
                logger.error(f"Error getting open orders: {str(e)}")
                return None
        
    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
            try:
                result = self.client.futures_cancel_order(
                    symbol=symbol.upper(),
                    orderId=order_id
                )
                logger.info(f"Order {order_id} cancelled successfully")
                return result
            except Exception as e:
                logger.error(f"Error cancelling order: {str(e)}")
                return None

    def get_position_info(self, symbol: Optional[str] = None) -> Optional[list]:
            try:
                positions = self.client.futures_position_information(symbol=symbol.upper() if symbol else None)
                active_positions = [p for p in positions if float(p['positionAmt']) != 0]
                logger.info(f"Retrieved {len(active_positions)} active positions")
                return active_positions
            except Exception as e:
                logger.error(f"Error getting position info: {str(e)}")
                return None

def print_menu():
    print("\n" + "="*60)
    print("BinanceBot MainMenu | by Adithya")
    print("="*60)
    print("1. Place Market Order")
    print("2. Place Limit Order")
    print("3. Place Stop-Limit Order")
    print("4. View Account Balance")
    print("5. View Open Orders")
    print("6. View Positions")
    print("7. Cancel Order")
    print("8. Exit")
    print("="*60)

def get_user_input(prompt: str, input_type: type=str):
    while True:
        try: 
            value = input(prompt)
            if input_type == float:
                return float(value)
            elif input_type == int:
                return int(value)
            else:
                return value
        except ValueError:
            print(f"Invalid input.")
