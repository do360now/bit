from dataclasses import dataclass, field
from typing import Dict

from api_kraken import KrakenAPI
from config import ALLOCATIONS, API_DOMAIN, API_KEY, API_SECRET
from logger_config import logger


@dataclass
class Portfolio:
    """
    Represents the portfolio distribution of ETH among different categories.
    Categories and their allocations are taken from the config file.

    Attributes:
        total_eth (float): The total amount of ETH managed by the portfolio.
        allocations (Dict[str, float]): A dictionary of category-to-weight mappings.
        portfolio (Dict[str, float]): A dictionary representing the actual ETH assigned to each category.
    """

    kraken_api: KrakenAPI = field(
        default_factory=lambda: KrakenAPI(API_KEY, API_SECRET, API_DOMAIN)
    )
    allocations: Dict[str, float] = field(default_factory=lambda: ALLOCATIONS)
    portfolio: Dict[str, float] = field(init=False)

    def __post_init__(self) -> None:
        self.total_eth = self._fetch_total_eth()
        self._initialize_portfolio()

    def _fetch_total_eth(self) -> float:
        """
        Fetch the total ETH balance from Kraken, considering alternate keys.
        """
        balance = self.kraken_api.get_account_balance()
        if balance:
            # Attempt to find the correct ETH key
            eth_key = next((key for key in balance if "ETH.F" in key), None)
            if eth_key:
                logger.info(
                    f"Fetched ETH balance from Kraken: {balance[eth_key]} (key: {eth_key})"
                )
                return float(balance[eth_key])
        logger.warning("Failed to fetch ETH balance. Defaulting to 0.")
        return 0.0

    def _initialize_portfolio(self) -> None:
        """
        Initialize the portfolio based on the total ETH and the allocated weights.
        """
        self.portfolio = {
            category: self.total_eth * weight
            for category, weight in self.allocations.items()
        }

    def rebalance(self) -> None:
        """
        Recalculate the allocation of the portfolio based on the current total ETH.
        """
        self.total_eth = self._fetch_total_eth()
        for category, weight in self.allocations.items():
            self.portfolio[category] = self.total_eth * weight

        logger.info(f"Portfolio rebalanced: {self.portfolio}")
        logger.info(f"Total ETH balance: {self.total_eth}")

    def update_balance(self, category: str, amount: float) -> None:
        """
        Update the balance of a specific category by adding an amount of ETH.
        After updating, the portfolio is rebalanced to ensure allocations remain consistent.

        :param category: The category to update.
        :param amount: The ETH amount to add (or subtract if negative).
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
