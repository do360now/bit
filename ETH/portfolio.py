from config import ALLOCATIONS, TOTAL_ETH
from logger_config import logger

# Portfolio balances
class Portfolio:
    def __init__(self, allocations: dict, total_ETH: float):
        self.allocations = allocations
        self.total_ETH = total_ETH
        self.portfolio = {
            'HODL': total_ETH * allocations['HODL'],
            'YIELD': total_ETH * allocations['YIELD'],
            'TRADING': total_ETH * allocations['TRADING'],
        }

    def rebalance(self):
        self.total_ETH = sum(self.portfolio.values())
        self.portfolio['HODL'] = self.total_ETH * self.allocations['HODL']
        self.portfolio['YIELD'] = self.total_ETH * self.allocations['YIELD']
        self.portfolio['TRADING'] = self.total_ETH * self.allocations['TRADING']
        logger.info(f"Portfolio rebalanced: {self.portfolio}")

# Initialize Portfolio
portfolio = Portfolio(ALLOCATIONS, TOTAL_ETH)

def rebalance_portfolio():
    portfolio.rebalance()