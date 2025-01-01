import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from datetime import datetime, timedelta

# Import functions from the module
from indicators import (
    fetch_latest_news,
    calculate_sentiment,
    calculate_moving_average,
    calculate_rsi,
    calculate_macd,
    calculate_potential_profit_loss,
    is_profitable_trade
)

class TestBitcoinAnalysis(unittest.TestCase):

    @patch("indicators.requests.get")
    def test_fetch_latest_news(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {"title": "Bitcoin hits new high", "description": "Bitcoin reaches $50,000", "url": "http://example.com/1"},
                {"title": "Bitcoin adoption grows", "description": "More companies are accepting Bitcoin", "url": "http://example.com/2"}
            ]
        }
        mock_get.return_value = mock_response

        articles = fetch_latest_news(top_n=2)

        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], "Bitcoin hits new high")

    def test_calculate_sentiment(self):
        articles = [
            {"title": "Bitcoin is amazing", "description": "Prices are soaring"},
            {"title": "Bitcoin crash", "description": "Prices are falling sharply"}
        ]

        sentiment = calculate_sentiment(articles)
        self.assertIsInstance(sentiment, float)

    def test_calculate_moving_average(self):
        prices = [10, 20, 30, 40, 50, 60, 70]
        result = calculate_moving_average(prices, window=3)
        self.assertAlmostEqual(result, 60.0)

    def test_calculate_rsi(self):
        prices = [50, 52, 54, 53, 55, 58, 60, 62, 61, 63, 64, 65, 66, 68, 70]
        rsi = calculate_rsi(prices, window=14)
        self.assertIsNotNone(rsi)
        self.assertTrue(0 <= rsi <= 100)

    def test_calculate_macd(self):
        prices = list(range(1, 30))
        macd, signal = calculate_macd(prices)
        self.assertIsInstance(macd, float)
        self.assertIsInstance(signal, float)

    def test_calculate_potential_profit_loss(self):
        current_price = 120.0
        previous_price = 100.0
        result = calculate_potential_profit_loss(current_price, previous_price)
        self.assertEqual(result, 20.0)

    def test_is_profitable_trade(self):
        potential_profit_loss = 0.5  # 0.5% profit
        self.assertTrue(is_profitable_trade(potential_profit_loss, transaction_fee_percentage=0.26))

        potential_profit_loss = 0.2  # 0.2% profit
        self.assertFalse(is_profitable_trade(potential_profit_loss, transaction_fee_percentage=0.26))

if __name__ == "__main__":
    unittest.main()
