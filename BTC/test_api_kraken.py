import unittest
from unittest.mock import patch, MagicMock
from api_kraken import KrakenAPI

class TestKrakenAPIEnhanced(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_key"
        self.api_secret = "dGVzdF9zZWNyZXQ="  # base64 encoded "test_secret"
        self.api_domain = "https://api.kraken.com"
        self.api_kraken = KrakenAPI(self.api_key, self.api_secret, self.api_domain)

    @patch("api_kraken.requests.post")
    def test_make_private_request_error_handling(self, mock_post):
        mock_post.side_effect = Exception("Network error")
        with self.assertRaises(Exception):  # Check for RetryError or specific exception if needed
            self.api_kraken._make_request(
                method="AddOrder",
                path="/0/private/",
                data={"test": "data"},
                is_private=True
            )

       
    @patch("api_kraken.requests.get")
    def test_get_btc_order_book_invalid_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"result": {}, "error": []}

        order_book = self.api_kraken.get_btc_order_book()
        self.assertIsNone(order_book)

    @patch("api_kraken.requests.get")
    def test_get_historical_prices_invalid_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "result": {},
            "error": []
        }

        prices = self.api_kraken.get_historical_prices()
        self.assertEqual(prices, [])

    def test_get_optimal_price_invalid_side(self):
        order_book = {
            "asks": [["46000.0", "1"]],
            "bids": [["45000.0", "2"]]
        }
        optimal_price = self.api_kraken.get_optimal_price(order_book, side="hold")
        self.assertIsNone(optimal_price)

    def test_get_optimal_price_edge_case_buffer(self):
        order_book = {
            "asks": [["46000.0", "1"]],
            "bids": [["45000.0", "2"]]
        }
        optimal_price = self.api_kraken.get_optimal_price(order_book, side="buy", buffer=10000.0)
        self.assertEqual(optimal_price, 36000.0)

    @patch("api_kraken.requests.post")
    def test_execute_trade_invalid_order_book(self, mock_post):
        with patch.object(self.api_kraken, "get_btc_order_book") as mock_order_book:
            mock_order_book.return_value = None

            self.api_kraken.execute_trade(volume=1.0, side="buy")

            mock_post.assert_not_called()

    @patch("api_kraken.requests.get")
    def test_get_market_volume_key_error(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "result": {"XBTUSDT": {"v": []}},
            "error": []
        }

        volume = self.api_kraken.get_market_volume()
        self.assertIsNone(volume)

    @patch("api_kraken.requests.get")
    def test_get_market_volume_invalid_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "result": {},
            "error": []
        }

        volume = self.api_kraken.get_market_volume()
        self.assertIsNone(volume)

if __name__ == "__main__":
    unittest.main()
