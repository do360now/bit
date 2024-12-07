import sys
import time
import signal
import json
from typing import List

from trading import trading_strategy, trading_strategy_instance
from portfolio import rebalance_portfolio
from api_kraken import KrakenAPI
from logger_config import logger
from config import (
    CURRENT_PORTFOLIO_SNAPSHOT,
    API_KEY,
    API_SECRET,
    API_DOMAIN,
    SLEEP_DURATION,
)


class PortfolioManager:
    def __init__(self, api_key: str, api_secret: str, api_domain: str):
        self.kraken_api = KrakenAPI(api_key, api_secret, api_domain)
        self.historical_prices: List[float] = []
        self.btc_deviation_from_baseline = None
        self.current_btc = None

    def get_asset_key(self, asset_name: str) -> str:
        """Fetch the asset key dynamically from the Kraken API."""
        asset_data = self.kraken_api.get_assets()
        for key, details in asset_data.items():
            if details["altname"] == asset_name:
                return key
        raise ValueError(f"Asset key for {asset_name} not found.")

    def load_historical_prices(self):
        """Load historical prices from a cache or fetch from API."""
        cache_file = "historical_prices.json"
        try:
            with open(cache_file, "r") as f:
                self.historical_prices = json.load(f)
            logger.info(f"Loaded {len(self.historical_prices)} prices from cache.")
        except FileNotFoundError:
            logger.info("Fetching historical BTC data...")
            self.historical_prices = self.kraken_api.get_historical_prices() or []
            logger.info("Historical BTC data fetched.")
            with open(cache_file, "w") as f:
                json.dump(self.historical_prices, f)
            logger.info(f"Fetched and cached {len(self.historical_prices)} prices.")

    def initialize(self):
        """Initialize the portfolio manager."""
        self.load_historical_prices()

        # Fetch current account balance and compare to baseline
        account_balance = self.kraken_api.get_account_balance()
        logger.info(f"Account balance: {account_balance}")
        if account_balance:
            try:
                btc_key = "XBT.F"
                logger.info(f"BTC key: {btc_key}")
                if btc_key in account_balance:
                    self.current_btc = float(account_balance[btc_key])
                    baseline_btc = CURRENT_PORTFOLIO_SNAPSHOT["BTC"]["amount_btc_total"]

                    deviation = (self.current_btc - baseline_btc) / baseline_btc * 100.0
                    logger.info(
                        f"Current BTC: {self.current_btc:.5f} BTC vs. Baseline: {baseline_btc:.5f} BTC"
                    )
                    logger.info(f"Deviation from baseline: {deviation:.2f}%")

                    self.btc_deviation_from_baseline = deviation
                else:
                    logger.warning(
                        f"BTC balance not found in account data for key {btc_key}."
                    )
            except Exception as e:
                logger.error(f"Error processing account balance: {e}")
        else:
            logger.warning("Could not retrieve account balance.")

    def run(self, test_cycles: int = None) -> None:
        """Start the main loop for rebalancing and trading."""
        cycle_count = 0
        while test_cycles is None or cycle_count < test_cycles:
            try:
                # Rebalance portfolio before each trading cycle.
                rebalance_portfolio()

                # Update trading strategy parameters.
                if self.current_btc is not None and hasattr(
                    trading_strategy_instance, "update_current_btc_holdings"
                ):
                    trading_strategy_instance.update_current_btc_holdings(
                        self.current_btc
                    )

                if self.btc_deviation_from_baseline is not None and hasattr(
                    trading_strategy_instance, "update_btc_deviation"
                ):
                    trading_strategy_instance.update_btc_deviation(
                        self.btc_deviation_from_baseline
                    )

                # Run the trading strategy.
                trading_strategy(self.historical_prices)

                logger.info("Waiting for next trading cycle...")
                time.sleep(SLEEP_DURATION)
                cycle_count += 1
            except Exception as e:
                logger.error(f"Error during cycle {cycle_count}: {e}")
                time.sleep(60)


def handle_signal(sig, frame):
    """Handle termination signals for graceful shutdown."""
    logger.info("Received termination signal. Stopping the bot...")
    sys.exit(0)


def main() -> None:
    """Entry point for the trading bot."""
    try:
        # Set up signal handlers for graceful shutdown.
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        # Initialize and run the portfolio manager.
        portfolio_manager = PortfolioManager(API_KEY, API_SECRET, API_DOMAIN)
        portfolio_manager.initialize()
        portfolio_manager.run()
    except KeyboardInterrupt:
        logger.info("Trading bot stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
