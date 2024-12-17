from config import ALLOCATIONS, TOTAL_XRP
from logger_config import logger

# Portfolio balances
class Portfolio:
    def __init__(self, allocations: dict, total_XRP: float):
        self.allocations = allocations
        self.total_XRP = total_XRP
        self.portfolio = {
            'HODL': total_XRP * allocations['HODL'],
            'YIELD': total_XRP * allocations['YIELD'],
            'TRADING': total_XRP * allocations['TRADING'],
        }

    def rebalance(self):
        self.total_XRP = sum(self.portfolio.values())
        self.portfolio['HODL'] = self.total_XRP * self.allocations['HODL']
        self.portfolio['YIELD'] = self.total_XRP * self.allocations['YIELD']
        self.portfolio['TRADING'] = self.total_XRP * self.allocations['TRADING']
        logger.info(f"Portfolio rebalanced: {self.portfolio}")

# Initialize Portfolio
portfolio = Portfolio(ALLOCATIONS, TOTAL_XRP)

def rebalance_portfolio():
    portfolio.rebalance()