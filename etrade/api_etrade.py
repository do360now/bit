import requests
import time
import json
import base64
import hmac
import hashlib
from typing import Optional, List, Dict
from config import API_KEY, API_SECRET, API_DOMAIN
from logger_config import logger
from tenacity import retry, wait_exponential, stop_after_attempt
import urllib.parse

class EtradeAPI:
    def __init__(self, api_key: str, api_secret: str, api_domain: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_domain = api_domain
        self.access_token = None
        self.access_secret = None

    def get_request_token(self) -> None:
        """
        Step 1: Obtain a request token from E*TRADE
        """
        url = f"{self.api_domain}/oauth/request_token"
        headers = self._generate_oauth_headers(url, "POST")
        response = requests.post(url, headers=headers)
        response_data = dict(urllib.parse.parse_qsl(response.text))

        if response.status_code == 200:
            self.request_token = response_data.get('oauth_token')
            self.request_token_secret = response_data.get('oauth_token_secret')
            logger.info("Request token obtained.")
        else:
            logger.error(f"Failed to obtain request token: {response.text}")

    def authorize_application(self) -> None:
        """
        Step 2: Redirect user to E*TRADE for authorization
        """
        url = f"{self.api_domain}/oauth/authorize?oauth_token={self.request_token}"
        logger.info(f"Please go to this URL to authorize: {url}")
        # The user must manually go to this URL and authorize, then provide the verifier code

    def get_access_token(self, verifier: str) -> None:
        """
        Step 3: Exchange verifier for an access token
        """
        url = f"{self.api_domain}/oauth/access_token"
        headers = self._generate_oauth_headers(url, "POST", verifier=verifier)
        response = requests.post(url, headers=headers)
        response_data = dict(urllib.parse.parse_qsl(response.text))

        if response.status_code == 200:
            self.access_token = response_data.get('oauth_token')
            self.access_secret = response_data.get('oauth_token_secret')
            logger.info("Access token obtained.")
        else:
            logger.error(f"Failed to obtain access token: {response.text}")

    def _generate_oauth_headers(self, url: str, method: str, verifier: Optional[str] = None) -> Dict[str, str]:
        nonce = str(int(time.time() * 1000))
        timestamp = str(int(time.time()))
        parameters = {
            "oauth_consumer_key": self.api_key,
            "oauth_nonce": nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": timestamp,
            "oauth_version": "1.0",
        }

        if verifier:
            parameters["oauth_verifier"] = verifier
        if hasattr(self, 'request_token'):
            parameters["oauth_token"] = self.request_token

        # Generate signature
        signature = self._sign_request(url, method, parameters)
        parameters["oauth_signature"] = signature

        # Create authorization header
        auth_header = "OAuth " + ", ".join([f'{key}="{urllib.parse.quote(str(value))}"' for key, value in parameters.items()])
        return {"Authorization": auth_header, "Content-Type": "application/x-www-form-urlencoded"}

    def _sign_request(self, url: str, method: str, params: Dict[str, str]) -> str:
        sorted_params = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted(params.items())])
        base_string = "&".join([method.upper(), urllib.parse.quote(url, safe=''), urllib.parse.quote(sorted_params, safe='')])
        signing_key = f"{self.api_secret}&{getattr(self, 'request_token_secret', '')}"
        hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
        return base64.b64encode(hashed.digest()).decode()

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5))
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        url = f"{self.api_domain}{endpoint}"
        headers = self._generate_oauth_headers(url, method)
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, data=data)
            else:
                response = requests.get(url, headers=headers, params=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            logger.error(f"API call failed ({error})")
            return None

    def get_account_balance(self) -> Optional[Dict[str, float]]:
        if not self.access_token:
            logger.error("Access token is missing. Cannot make authenticated requests.")
            return None
        result = self._make_request(endpoint="/v1/accounts/list", method="GET")
        return result

# Initialize the API client
etrade_api = EtradeAPI(API_KEY, API_SECRET, API_DOMAIN)

# Example usage
if __name__ == "__main__":
    etrade_api.get_request_token()
    etrade_api.authorize_application()
    verifier_code = input("Enter the verifier code: ")
    etrade_api.get_access_token(verifier_code)
    balance = etrade_api.get_account_balance()
    if balance:
        logger.info(f"Account balance: {balance}")
