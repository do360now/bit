from dataclasses import dataclass, field
from typing import Dict
from config import ALLOCATIONS, TOTAL_BTC
from logger_config import logger

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
    total_btc: float = TOTAL_BTC
    allocations: Dict[str, float] = field(default_factory=lambda: ALLOCATIONS)
    portfolio: Dict[str, float] = field(init=False)

    def __post_init__(self) -> None:
        self._initialize_portfolio()

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
        
        The total BTC is updated to reflect any changes, and each category’s amount is
        recalculated according to the pre-defined allocation weights.
        """
        self.total_btc = sum(self.portfolio.values())
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
            logger.warning(f"Category {category} not found in portfolio. Skipping update.")
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
