import requests
import time
import base64
import hashlib
import hmac
from typing import Optional, List, Dict, Any
from config import API_KEY, API_SECRET, API_DOMAIN
from logger_config import logger
from tenacity import retry, wait_exponential, stop_after_attempt


class KrakenAPI:
    def __init__(self, api_key: str, api_secret: str, api_domain: str) -> None:
        """
        Initialize the KrakenAPI client.

        :param api_key: Your Kraken API key.
        :param api_secret: Your Kraken API secret key, base64-encoded.
        :param api_domain: The base API URL for Kraken (e.g. 'https://api.kraken.com')
        """
        self.api_key = api_key
        self.api_secret = base64.b64decode(api_secret)
        self.api_domain = api_domain

    def _sign_request(self, api_path: str, api_nonce: str, api_postdata: str) -> str:
        """
        Sign the request using the provided nonce and postdata.

        :param api_path: API path including version and endpoint (e.g. '/0/private/')
        :param api_nonce: A unique nonce value (typically a timestamp).
        :param api_postdata: The POST body data as a query string.
        :return: Base64-encoded signature.
        """
        api_sha256 = hashlib.sha256(
            api_nonce.encode("utf-8") + api_postdata.encode("utf-8")
        ).digest()
        api_hmacsha512 = hmac.new(
            self.api_secret, api_path.encode("utf-8") + api_sha256, hashlib.sha512
        )
        return base64.b64encode(api_hmacsha512.digest()).decode()

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5))
    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        is_private: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Kraken API, handling signing and retries for private endpoints.

        :param method: The method name to append to the API path (e.g. 'Ticker', 'OHLC').
        :param path: The API path (e.g. '/0/public/', '/0/private/').
        :param data: Optional dictionary of parameters to send with the request.
        :param is_private: Whether this request is to a private endpoint requiring authentication.
        :return: The 'result' field of the API response as a dict, or None if errors occur.
        """
        url = f"{self.api_domain}{path}{method}"
        headers = {"User-Agent": "Kraken REST API"}
        post_data = ""

        if data:
            post_data = "&".join([f"{key}={value}" for key, value in data.items()])

        if is_private:
            nonce = str(int(time.time() * 1000))
            # Append nonce to post_data
            post_data += f"&nonce={nonce}"
            headers["API-Key"] = self.api_key
            headers["API-Sign"] = self._sign_request(path + method, nonce, post_data)

        try:
            if is_private:
                response = requests.post(
                    url, headers=headers, data=post_data, timeout=10
                )
            else:
                # For public endpoints, use GET with params
                # Note: Using POST for all requests is also possible, but GET is fine here.
                # Adjust if Kraken endpoints specifically require POST.
                response = requests.get(url, headers=headers, params=data, timeout=10)
            response.raise_for_status()
            api_reply = response.json()

            # Check for errors returned by the API
            if "error" in api_reply and api_reply["error"]:
                logger.error(f"API error: {api_reply['error']}")
                return None

            return api_reply.get("result", None)
        except requests.RequestException as error:
            logger.error(f"API call failed ({error})")
            return None

    def get_btc_price(self) -> Optional[float]:
        """
        Retrieve the current BTC price from Kraken.

        :return: The current BTC/EUR price as a float, or None if retrieval fails.
        """
        result = self._make_request(
            method="Ticker", path="/0/public/", data={"pair": "XXBTZEUR"}
        )
        if result and "XXBTZEUR" in result and "c" in result["XXBTZEUR"]:
            try:
                return float(result["XXBTZEUR"]["c"][0])
            except (ValueError, KeyError, IndexError) as e:
                logger.error(f"Failed to parse BTC price: {e}")
                return None
        return None

    def get_historical_prices(
        self, pair: str = "XXBTZEUR", interval: int = 60, since: Optional[int] = None
    ) -> List[float]:
        """
        Fetch historical OHLC prices for a trading pair.

        :param pair: Trading pair, e.g., 'XXBTZEUR'.
        :param interval: Interval in minutes for OHLC data.
        :param since: Optional Unix timestamp to fetch data from.
        :return: A list of close prices.
        """
        data: Dict[str, Any] = {"pair": pair, "interval": interval}
        if since:
            data["since"] = since

        try:
            result = self._make_request(method="OHLC", path="/0/public/", data=data)
        except Exception as e:
            logger.error(f"Failed to fetch historical prices due to exception: {e}")
            return []

        if result and pair in result:
            try:
                return [
                    float(entry[4]) for entry in result.get(pair, []) if len(entry) > 4
                ]
            except ValueError as ve:
                logger.error(f"Error converting entry to float: {ve}")
                return []

        logger.warning(f"No data found for pair {pair} or unexpected response format.")
        return []

    def execute_trade(
        self, volume: float, side: str, price: Optional[float] = None
    ) -> None:
        """
        Execute a trade (buy or sell) on Kraken.

        :param volume: The amount of BTC to buy or sell.
        :param side: 'buy' or 'sell'.
        :param price: Optional price for a limit order. If None, a market order is placed.
        """
        data: Dict[str, Any] = {
            "pair": "XXBTZEUR",
            "type": side,
            "ordertype": "limit" if price else "market",
            "volume": volume,
        }
        if price is not None:
            data["price"] = price

        result = self._make_request(
            method="AddOrder", path="/0/private/", data=data, is_private=True
        )
        if result:
            logger.info(
                f"Executed {side} order for {volume} BTC at {price or 'market price'}. Order response: {result}"
            )

    def get_account_balance(self) -> Optional[Dict[str, float]]:
        """
        Retrieve the account balance for the authenticated Kraken account.

        :return: A dict mapping asset names to their balances, or None if the request fails.
        """
        result = self._make_request(
            method="Balance", path="/0/private/", is_private=True
        )
        # The returned balance keys are often prefixed (e.g., 'XXBT'), so consider parsing as needed.
        if result is None:
            logger.error("Failed to retrieve account balance.")
        return result

    def get_open_orders(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve currently open orders.

        :return: A dict of open orders keyed by their order IDs, or None if none are found.
        """
        result = self._make_request(
            method="OpenOrders", path="/0/private/", is_private=True
        )
        if result:
            return result.get("open", None)
        return None

    def get_assets(self):
        """Fetch the asset data from Kraken's API."""
        url = f"{self.api_domain}/0/public/Assets"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "error" in data and data["error"]:
                raise ValueError(f"Kraken API error: {data['error']}")
            return data.get("result", {})
        except requests.RequestException as e:
            raise ConnectionError(f"Error fetching assets: {e}")


# Initialize the API client
kraken_api = KrakenAPI(API_KEY, API_SECRET, API_DOMAIN)


if __name__ == "__main__":
    # Example usage, can be removed or commented out in production
    btc_price = kraken_api.get_btc_price()
    if btc_price:
        logger.info(f"Current BTC price: {btc_price}")
