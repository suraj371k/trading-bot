import hashlib
import hmac
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

logger = setup_logger("binance_client")

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""
    pass


class NetworkError(Exception):
    """Raised when a network/connection issue occurs."""
    pass


class BinanceClient:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key or os.getenv("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET", "")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API key and secret are required. "
                "Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file."
            )

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.info("BinanceClient initialised (testnet).")

    # Internal helpers

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a HMAC-SHA256 signature to the params dict."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = BASE_URL + endpoint
        signed_params = self._sign(params)

        logger.debug("REQUEST  %s %s | params: %s", method.upper(), url, signed_params)

        try:
            response = self.session.request(method, url, data=signed_params)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise NetworkError(f"Could not connect to Binance testnet: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise NetworkError(f"Request timed out: {exc}") from exc

        logger.debug("RESPONSE %s | body: %s", response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response: %s", response.text)
            raise BinanceClientError(f"Unexpected response from server: {response.text}")

        if response.status_code != 200:
            code = data.get("code", response.status_code)
            msg = data.get("msg", response.text)
            logger.error("API error %s: %s", code, msg)
            raise BinanceClientError(f"Binance API error {code}: {msg}")

        return data

    # Public methods

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place a futures order and return the full API response."""
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC" 

        if order_type == "STOP_MARKET":
            params["stopPrice"] = stop_price
            params["closePosition"] = "false"

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s",
            side, order_type, symbol, quantity, price or stop_price or "N/A",
        )

        endpoint = "/fapi/v1/order"
        return self._request("POST", endpoint, params)

    def get_account_info(self) -> Dict[str, Any]:
        """Fetch account balance/info (useful for quick connectivity check)."""
        return self._request("GET", "/fapi/v2/account", {})