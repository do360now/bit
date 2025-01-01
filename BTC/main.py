import time
from trading_strategy import trading_strategy
from portfolio import rebalance_portfolio
from api_kraken import KrakenAPI
from logger_config import logger
from config import API_KEY, API_SECRET, API_DOMAIN

# Initialize Kraken API client
kraken_api = KrakenAPI(API_KEY, API_SECRET, API_DOMAIN)

# Load initial historical data
logger.info("Fetching historical BTC data...")

try:
    historical_prices = kraken_api.get_historical_prices()
    prices = historical_prices if historical_prices else []
    if not prices:
        logger.warning("No historical prices fetched, starting with an empty dataset.")
    else:
        logger.info(f"Loaded {len(prices)} historical prices.")
except Exception as e:
    logger.error(f"Failed to fetch historical BTC data: {e}")
    prices = []

def portfolio_manager():
    while True:
        try:
            # Rebalance the portfolio
            logger.info("Rebalancing portfolio...")
            rebalance_portfolio()

            # Execute the trading strategy
            logger.info("Executing trading strategy...")
            trading_strategy(prices)

            # Wait for the next cycle
            logger.info("Waiting for the next trading cycle...")
            time.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Error in portfolio manager: {e}")
            time.sleep(60)  # Wait before retrying in case of an error

if __name__ == "__main__":
    portfolio_manager()

  

