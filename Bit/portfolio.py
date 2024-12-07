from dataclasses import dataclass, field
from typing import Dict
from config import ALLOCATIONS, API_KEY, API_SECRET, API_DOMAIN
from logger_config import logger
from api_kraken import KrakenAPI


@dataclass
class Portfolio:
    """
    Represents the portfolio distribution of BTC among different categories.
    Categories and their allocations are taken from the config file.

    Attributes:
        total_btc (float): The total amount of BTC managed by the portfolio.
        allocations (Dict[str, float]): A dictionary of category-to-weight mappings.
        portfolio (Dict[str, float]): A dictionary representing the actual BTC assigned to each category.
    """

    kraken_api: KrakenAPI = field(
        default_factory=lambda: KrakenAPI(API_KEY, API_SECRET, API_DOMAIN)
    )
    allocations: Dict[str, float] = field(default_factory=lambda: ALLOCATIONS)
    portfolio: Dict[str, float] = field(init=False)

    def __post_init__(self) -> None:
        self.total_btc = self._fetch_total_btc()
        self._initialize_portfolio()

    def _fetch_total_btc(self) -> float:
        """
        Fetch the total BTC balance from Kraken, considering alternate keys.
        """
        balance = self.kraken_api.get_account_balance()
        if balance:
            # Attempt to find the correct BTC key
            btc_key = next((key for key in balance if "XBT" in key), None)
            if btc_key:
                logger.info(
                    f"Fetched BTC balance from Kraken: {balance[btc_key]} (key: {btc_key})"
                )
                return float(balance[btc_key])
        logger.warning("Failed to fetch BTC balance. Defaulting to 0.")
        return 0.0

    def _initialize_portfolio(self) -> None:
        """
        Initialize the portfolio based on the total BTC and the allocated weights.
        """
        self.portfolio = {
            category: self.total_btc * weight
            for category, weight in self.allocations.items()
        }

    def rebalance(self) -> None:
        """
        Recalculate the allocation of the portfolio based on the current total BTC.
        """
        self.total_btc = self._fetch_total_btc()
        for category, weight in self.allocations.items():
            self.portfolio[category] = self.total_btc * weight

        logger.info(f"Portfolio rebalanced: {self.portfolio}")
        logger.info(f"Total BTC balance: {self.total_btc}")

    def update_balance(self, category: str, amount: float) -> None:
        """
        Update the balance of a specific category by adding an amount of BTC.
        After updating, the portfolio is rebalanced to ensure allocations remain consistent.

        :param category: The category to update.
        :param amount: The BTC amount to add (or subtract if negative).
        """
        if category not in self.portfolio:
            logger.warning(
                f"Category {category} not found in portfolio. Skipping update."
            )
            return
        self.portfolio[category] += amount
        self.rebalance()


# Singleton portfolio instance
portfolio = Portfolio()


def rebalance_portfolio() -> None:
    """
    Convenience function to trigger portfolio rebalancing from external modules.
    """
    portfolio.rebalance()
