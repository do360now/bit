import unittest
from unittest.mock import MagicMock, patch
from main import portfolio_manager

class TestMain(unittest.TestCase):
    def setUp(self):
        # Mock necessary imports
        self.mock_kraken_api = patch('main.kraken_api').start()
        self.mock_logger = patch('main.logger').start()
        self.mock_rebalance_portfolio = patch('main.rebalance_portfolio').start()
        self.mock_trading_strategy = patch('main.trading_strategy').start()
        self.mock_time = patch('main.time').start()

        self.addCleanup(patch.stopall)

    @unittest.skip("Skipping test for historical prices loaded successfully")
    def test_historical_prices_loaded_successfully(self):
        # Setup
        self.mock_kraken_api.get_historical_prices.return_value = [50000, 49000, 48000]

        # Execute
        with patch('main.portfolio_manager') as mock_portfolio_manager:
            mock_portfolio_manager.side_effect = KeyboardInterrupt  # Prevent infinite loop
            try:
                portfolio_manager()
            except KeyboardInterrupt:
                pass

        # Assert
        self.mock_kraken_api.get_historical_prices.assert_called_once()
        self.mock_logger.info.assert_any_call("Loaded 3 historical prices.")

    @unittest.skip("Skipping test for historical prices fetch failure")
    def test_historical_prices_fetch_failure(self):
        # Setup
        self.mock_kraken_api.get_historical_prices.side_effect = Exception("API Error")

        # Execute
        with patch('main.portfolio_manager') as mock_portfolio_manager:
            mock_portfolio_manager.side_effect = KeyboardInterrupt  # Prevent infinite loop
            try:
                portfolio_manager()
            except KeyboardInterrupt:
                pass

        # Assert
        self.mock_kraken_api.get_historical_prices.assert_called_once()
        self.mock_logger.error.assert_any_call("Failed to fetch historical BTC data: API Error")

    @unittest.skip("Skipping test for portfolio manager execution")
    def test_portfolio_manager_execution(self):
        # Setup
        self.mock_kraken_api.get_historical_prices.return_value = [50000, 49000, 48000]
        self.mock_time.sleep.side_effect = KeyboardInterrupt  # Simulate one loop

        # Execute
        try:
            portfolio_manager()
        except KeyboardInterrupt:
            pass

        # Assert
        self.mock_rebalance_portfolio.assert_called_once()
        self.mock_trading_strategy.assert_called_once_with([50000, 49000, 48000])
        self.mock_logger.info.assert_any_call("Rebalancing portfolio...")
        self.mock_logger.info.assert_any_call("Executing trading strategy...")

    def test_error_handling_in_portfolio_manager(self):
        # Setup
        self.mock_rebalance_portfolio.side_effect = Exception("Rebalance Error")
        self.mock_time.sleep.side_effect = KeyboardInterrupt  # Simulate one loop

        # Execute
        try:
            portfolio_manager()
        except KeyboardInterrupt:
            pass

        # Assert
        self.mock_logger.error.assert_any_call("Error in portfolio manager: Rebalance Error")
        self.mock_time.sleep.assert_called_with(60)  # Sleep before retrying

if __name__ == "__main__":
    unittest.main()
