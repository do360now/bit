import sys
import time
from typing import List

from trading import trading_strategy
from portfolio import rebalance_portfolio
from api_kraken import KrakenAPI
from logger_config import logger
from config import API_KEY, API_SECRET, API_DOMAIN

class PortfolioManager:
    """
    The PortfolioManager class orchestrates fetching historical data, 
    rebalancing the portfolio, and running the trading strategy in a loop.
    """
    def __init__(self, api_key: str, api_secret: str, api_domain: str) -> None:
        """
        Initialize the PortfolioManager with API credentials.
        
        :param api_key: Kraken API key for authentication.
        :param api_secret: Kraken API secret key for signing requests.
        :param api_domain: Base URL for the Kraken API.
        """
        self.kraken_api = KrakenAPI(api_key, api_secret, api_domain)
        self.historical_prices: List[float] = []

    def initialize(self) -> None:
        """
        Fetch historical BTC prices and store them for the trading strategy.
        """
        logger.info("Fetching historical BTC data...")
        historical_prices = self.kraken_api.get_historical_prices()
        logger.info("Historical BTC data fetched.")
        self.historical_prices = historical_prices or []
        logger.info(f"Loaded {len(self.historical_prices)} historical prices.")

    def run(self) -> None:
        """
        Start the main loop:
        - Rebalance the portfolio
        - Execute the trading strategy
        - Wait for the next cycle
        """
        while True:
            try:
                # Rebalance portfolio before each trading cycle.
                rebalance_portfolio()

                # Run the trading strategy using the historical prices.
                trading_strategy(self.historical_prices)

                logger.info("Waiting for next trading cycle...")
                # Wait for the next cycle (currently set to 5 minutes).
                time.sleep(300)
            except Exception as e:
                # If something unexpected happens, log the error and try again after 1 minute.
                logger.error(f"Portfolio management error: {e}")
                time.sleep(60)

def main() -> None:
    """
    Entry point for the trading bot. Initializes the PortfolioManager, 
    fetches historical data, and begins the trading loop.
    """
    try:
        portfolio_manager = PortfolioManager(API_KEY, API_SECRET, API_DOMAIN)
        portfolio_manager.initialize()
        portfolio_manager.run()
    except KeyboardInterrupt:
        logger.info("Trading bot stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
