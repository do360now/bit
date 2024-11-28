import sys
import time
from typing import List

from trading import trading_strategy
from portfolio import rebalance_portfolio
from api_kraken import KrakenAPI
from logger_config import logger
from config import API_KEY, API_SECRET, API_DOMAIN

class PortfolioManager:
    def __init__(self, api_key: str, api_secret: str, api_domain: str):
        self.kraken_api = KrakenAPI(api_key, api_secret, api_domain)
        self.historical_prices: List[float] = []

    def initialize(self):
        logger.info("Fetching historical BTC data...")
        historical_prices = self.kraken_api.get_historical_prices()
        logger.info("Historical BTC data fetched.")
        self.historical_prices = historical_prices or []
        logger.info(f"Loaded {len(self.historical_prices)} historical prices.")

    def run(self):
        while True:
            try:
                rebalance_portfolio()
                trading_strategy(self.historical_prices)
                logger.info("Waiting for next trading cycle...")
                time.sleep(300)  # 5-minute cycle
            except Exception as e:
                logger.error(f"Portfolio management error: {e}")
                time.sleep(60)  # Error recovery wait

def main():
    try:
        portfolio_manager = PortfolioManager(API_KEY, API_SECRET, API_DOMAIN)
        portfolio_manager.initialize()
        portfolio_manager.run()
    except KeyboardInterrupt:
        logger.info("Trading bot stopped.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()