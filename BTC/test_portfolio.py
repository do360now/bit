import unittest
from unittest.mock import patch, MagicMock
from portfolio import Portfolio, rebalance_portfolio

# Mocked configurations
ALLOCATIONS = {
    'HODL': 0.5,
    'YIELD': 0.3,
    'TRADING': 0.2
}
TOTAL_BTC = 1.0

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.allocations = ALLOCATIONS
        self.total_btc = TOTAL_BTC
        self.portfolio = Portfolio(self.allocations, self.total_btc)

    def test_initialization(self):
        """Test initialization of portfolio values."""
        self.assertAlmostEqual(self.portfolio.portfolio['HODL'], 0.5)
        self.assertAlmostEqual(self.portfolio.portfolio['YIELD'], 0.3)
        self.assertAlmostEqual(self.portfolio.portfolio['TRADING'], 0.2)

    def test_rebalance(self):
        """Test rebalancing of the portfolio."""
        # Simulate a change in portfolio values
        self.portfolio.portfolio['HODL'] = 0.6
        self.portfolio.portfolio['YIELD'] = 0.2
        self.portfolio.portfolio['TRADING'] = 0.2

        self.portfolio.rebalance()

        total = sum(self.portfolio.portfolio.values())
        self.assertAlmostEqual(total, self.total_btc)
        self.assertAlmostEqual(self.portfolio.portfolio['HODL'], 0.5)
        self.assertAlmostEqual(self.portfolio.portfolio['YIELD'], 0.3)
        self.assertAlmostEqual(self.portfolio.portfolio['TRADING'], 0.2)

    @patch('portfolio.logger')
    def test_rebalance_logging(self, mock_logger):
        """Test that rebalance logs the correct information."""
        self.portfolio.rebalance()
        mock_logger.info.assert_called_once_with(f"Portfolio rebalanced: {self.portfolio.portfolio}")

class TestRebalancePortfolioFunction(unittest.TestCase):
    @patch('portfolio.portfolio')
    def test_rebalance_portfolio_function(self, mock_portfolio):
        """Test the rebalance_portfolio function calls Portfolio.rebalance."""
        rebalance_portfolio()
        mock_portfolio.rebalance.assert_called_once()

if __name__ == '__main__':
    unittest.main()
