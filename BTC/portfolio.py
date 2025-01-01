from config import ALLOCATIONS, TOTAL_BTC
from logger_config import logger

# Portfolio balances
class Portfolio:
    def __init__(self, allocations: dict, total_btc: float):
        self.allocations = allocations
        self.total_btc = total_btc
        self.portfolio = {
            'HODL': total_btc * allocations['HODL'],
            'YIELD': total_btc * allocations['YIELD'],
            'TRADING': total_btc * allocations['TRADING'],
        }

    def rebalance(self):
        self.total_btc = sum(self.portfolio.values())
        self.portfolio['HODL'] = self.total_btc * self.allocations['HODL']
        self.portfolio['YIELD'] = self.total_btc * self.allocations['YIELD']
        self.portfolio['TRADING'] = self.total_btc * self.allocations['TRADING']
        logger.info(f"Portfolio rebalanced: {self.portfolio}")

# Initialize Portfolio
portfolio = Portfolio(ALLOCATIONS, TOTAL_BTC)

def rebalance_portfolio():
    portfolio.rebalance()