from dataclasses import dataclass, field
from typing import Dict
from config import ALLOCATIONS, TOTAL_BTC
from logger_config import logger

@dataclass
class Portfolio:
    total_btc: float = TOTAL_BTC
    allocations: Dict[str, float] = field(default_factory=lambda: ALLOCATIONS)
    portfolio: Dict[str, float] = field(init=False)

    def __post_init__(self):
        self._initialize_portfolio()

    def _initialize_portfolio(self):
        self.portfolio = {
            category: self.total_btc * weight 
            for category, weight in self.allocations.items()
        }

    def rebalance(self):
        """Adjust portfolio allocation based on current total balance."""
        self.total_btc = sum(self.portfolio.values())
        for category, weight in self.allocations.items():
            self.portfolio[category] = self.total_btc * weight
        
        logger.info(f"Portfolio rebalanced: {self.portfolio}")
        logger.info(f"Total BTC balance: {self.total_btc}")
      

    def update_balance(self, category: str, amount: float):
        """Update balance of a specific portfolio category."""
        self.portfolio[category] += amount
        self.rebalance()

# Singleton portfolio instance
portfolio = Portfolio()

def rebalance_portfolio():
    portfolio.rebalance()