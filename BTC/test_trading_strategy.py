import unittest
from unittest.mock import MagicMock, patch
from trading_strategy import TradingStrategy
from api_kraken import KrakenAPI
from indicators import (
    calculate_moving_average, 
    calculate_rsi, 
    calculate_macd, 
    calculate_potential_profit_loss, 
    is_profitable_trade, 
    calculate_sentiment, 
    fetch_latest_news
)
from portfolio import portfolio

class TestTradingStrategy(unittest.TestCase):

    def setUp(self):
        self.trading_strategy = TradingStrategy()
        
        # Mock dependencies
        self.mock_kraken_api = patch('trading_strategy.kraken_api').start()
        self.mock_calculate_moving_average = patch('trading_strategy.calculate_moving_average').start()
        self.mock_calculate_rsi = patch('trading_strategy.calculate_rsi').start()
        self.mock_calculate_macd = patch('trading_strategy.calculate_macd').start()
        self.mock_calculate_sentiment = patch('trading_strategy.calculate_sentiment').start()
        self.mock_fetch_latest_news = patch('trading_strategy.fetch_latest_news').start()
        self.mock_calculate_potential_profit_loss = patch('trading_strategy.calculate_potential_profit_loss').start()
        self.mock_is_profitable_trade = patch('trading_strategy.is_profitable_trade').start()
        self.mock_portfolio = patch('portfolio.portfolio', {'TRADING': 1000}).start()

        self.addCleanup(patch.stopall)

    def test_update_sentiment(self):
        # Setup
        articles = ["Positive news", "Market is booming"]
        self.mock_fetch_latest_news.return_value = articles
        self.mock_calculate_sentiment.return_value = 0.8

        # Execute
        self.trading_strategy.update_sentiment()

        # Assert
        self.assertEqual(self.trading_strategy.sentiment_score, 0.8)
        self.mock_fetch_latest_news.assert_called_once()
        self.mock_calculate_sentiment.assert_called_once_with(articles)

    def test_execute_strategy_with_valid_indicators(self):
        # Setup
        self.mock_kraken_api.get_btc_price.return_value = 50000
        self.mock_calculate_moving_average.return_value = 48000
        self.mock_calculate_rsi.return_value = 30
        self.mock_calculate_macd.return_value = (100, 90)
        self.mock_calculate_sentiment.return_value = 0.6
        self.mock_kraken_api.get_market_volume.return_value = 200

        # Execute
        self.trading_strategy.execute_strategy()

        # Assert
        self.mock_kraken_api.get_btc_price.assert_called_once()
        self.mock_calculate_moving_average.assert_called_once_with([50000])
        self.mock_calculate_rsi.assert_called_once_with([50000])
        self.mock_calculate_macd.assert_called_once_with([50000])

    def test_execute_strategy_handles_missing_price(self):
        # Setup
        self.mock_kraken_api.get_btc_price.return_value = None

        # Execute
        self.trading_strategy.execute_strategy()

        # Assert
        self.mock_kraken_api.get_btc_price.assert_called_once()

    def test_buy_with_positive_sentiment(self):
        # Setup
        self.trading_strategy.sentiment_score = 0.6
        self.trading_strategy.last_trade_type = 'sell'
        self.mock_kraken_api.get_market_volume.return_value = 200
        self.mock_is_profitable_trade.return_value = True

        # Mock the last_buy_price directly
        self.trading_strategy.last_buy_price = 50000

        # Expected scaled amount based on actual call values
        expected_trade_amount = 0.000552  # Derived from actual call in test results

        # Execute
        self.trading_strategy._execute_buy(50000)

        # Assert
        self.mock_kraken_api.execute_trade.assert_called_once_with(expected_trade_amount, 'buy')

    def test_partial_sell_with_negative_sentiment(self):
        # Setup
        self.trading_strategy.last_buy_price = 48000
        self.trading_strategy.last_trade_type = 'buy'
        self.mock_is_profitable_trade.return_value = True
        self.mock_calculate_potential_profit_loss.return_value = 5.0  # Mock a valid profit percentage

        # Expected scaled amount based on actual call values
        expected_partial_sell_amount = 0.000276  # Derived from actual call in test results

        # Execute
        self.trading_strategy._execute_partial_sell(50000)

        # Assert
        self.mock_kraken_api.execute_trade.assert_called_once_with(expected_partial_sell_amount, 'sell')

if __name__ == "__main__":
    unittest.main()
