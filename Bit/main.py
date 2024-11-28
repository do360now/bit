import time
from trading import trading_strategy
# from trading_refactored import trading_strategy
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

  
# Example usage
if __name__ == "__main__":
    logger.info("Fetching historical BTC data...")
    historical_prices = kraken_api.get_historical_prices()  # Should now work as expected
    logger.info(f"Fetched historical prices: {historical_prices[:5]}")  # Log the first 5 historical prices for verification

    # Example buy and sell orders
    volume_to_trade = 0.1  # Adjust as needed
    kraken_api.execute_trade(volume=volume_to_trade, side="buy")
    kraken_api.execute_trade(volume=volume_to_trade, side="sell")
