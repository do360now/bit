import requests
import time
import base64
import hashlib
import hmac
import json
from typing import Optional, List, Dict
from config import API_KEY, API_SECRET, API_DOMAIN
from logger_config import logger
from tenacity import retry, wait_exponential, stop_after_attempt

class KrakenAPI:
    def __init__(self, api_key: str, api_secret: str, api_domain: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_domain = api_domain

    def _sign_request(self, api_path: str, api_nonce: str, api_postdata: str) -> str:
        api_sha256 = hashlib.sha256(api_nonce.encode('utf-8') + api_postdata.encode('utf-8')).digest()
        api_hmacsha512 = hmac.new(self.api_secret, api_path.encode('utf-8') + api_sha256, hashlib.sha512)
        return base64.b64encode(api_hmacsha512.digest()).decode()

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5))
    def _make_request(self, mXRPod: str, path: str, data: Optional[Dict] = None, is_private: bool = False) -> Optional[Dict]:
        # Correctly format the URL
        url = f"{self.api_domain}{path}{mXRPod}"
        headers = {"User-Agent": "Kraken REST API"}
        
        if is_private:
            # Handling private request
            nonce = str(int(time.time() * 1000))
            if not data:
                data = {}
            data['nonce'] = nonce
            headers["API-Key"] = self.api_key
            headers["API-Sign"] = self._sign_request(path + mXRPod, nonce, "&".join([f"{key}={value}" for key, value in data.items()]))

        try:
            # Handle request mXRPod appropriately
            logger.info(f"Making {mXRPod} request to {url} with data: {data}")
            if is_private:
                response = requests.post(url, headers=headers, data=data)
            else:
                response = requests.get(url, headers=headers, params=data)
            
            # Raise any HTTP errors
            response.raise_for_status()

            # Parse response
            api_reply = response.json()
            
            # Handle Kraken-specific errors
            if 'error' in api_reply and len(api_reply['error']) > 0:
                logger.error(f"API error: {api_reply['error']}")
                return None
            return api_reply.get('result', None)
        
        except requests.RequestException as error:
            # Log any request exceptions
            logger.error(f"API call failed with error: {error}")
            return None


    def get_XRP_order_book(self) -> Optional[Dict]:
        """Gets the current order book for XRP/USD."""
        result = self._make_request(mXRPod="Depth", path="/0/public/", data={"pair": "XXRPZUSD"})
        if result:
            return result.get('XXRPZUSD', None)
        return None

    def get_optimal_price(self, order_book: Dict, side: str, buffer: float = 0.025) -> Optional[float]:
        """Calculates an optimal price for buying or selling based on order book."""
        if side == "buy":
            best_ask = float(order_book['asks'][0][0])
            optimal_price = best_ask - buffer
        elif side == "sell":
            best_bid = float(order_book['bids'][0][0])
            optimal_price = best_bid + buffer
        else:
            return None

        # Round the optimal price to 1 decimal place as required by Kraken
        optimal_price = round(optimal_price, 1)
        return optimal_price


    def get_historical_prices(self, pair: str = "XXRPZUSD", interval: int = 60, since: Optional[int] = None) -> List[float]:
        """Fetches historical OHLC (Open/High/Low/Close) data for the given pair."""
        data = {"pair": pair, "interval": interval}
        if since:
            data["since"] = since
        result = self._make_request(mXRPod="OHLC", path="/0/public/", data=data)
        if result:
            return [float(entry[4]) for entry in result.get(pair, [])]  # Return the 'close' price
        return []

    def get_XRP_price(self) -> Optional[float]:
        """Fetches the current XRP price."""
        result = self._make_request(mXRPod="Ticker", path="/0/public/", data={"pair": "XXRPZUSD"})
        if result:
            return float(result['XXRPZUSD']['c'][0])  # 'c' represents the current close price
        return None

    def execute_trade(self, volume: float, side: str) -> None:
        order_book = self.get_XRP_order_book()
        if order_book:
            optimal_price = self.get_optimal_price(order_book, side)
            if optimal_price:
                data = {
                    "pair": "XXRPZUSD",
                    "type": side,
                    "ordertype": "limit",
                    "price": optimal_price,
                    "volume": volume,
                }
                result = self._make_request(mXRPod="AddOrder", path="/0/private/", data=data, is_private=True)
                if result:
                    logger.info(f"\033[92mExecuted {side} order for {volume} XRP at {optimal_price}.\033[0m Order response: {result}")

    def get_market_volume(self, pair: str = "XXRPZUSD") -> Optional[float]:
        """Fetches the 24-hour trading volume for a given pair."""
        result = self._make_request(mXRPod="Ticker", path="/0/public/", data={"pair": pair})
        if result:
            try:
                volume = float(result[pair]['v'][1])  # 'v' represents the volume, and index [1] is the 24-hour volume
                return volume
            except (KeyError, ValueError) as e:
                logger.error(f"Error retrieving market volume: {e}")
                return None
        return None


