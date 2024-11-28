import time
from api_kraken import KrakenAPI
from indicators import calculate_moving_average, calculate_rsi, calculate_macd, calculate_potential_profit_loss, is_profitable_trade
# from indicators_refactored import calculate_moving_average, calculate_rsi, calculate_macd, calculate_potential_profit_loss, is_profitable_trade
from portfolio import portfolio
from config import MIN_TRADE_VOLUME, API_KEY, API_SECRET, API_DOMAIN
from logger_config import logger
from typing import List, Optional

# Initialize Kraken API client
kraken_api = KrakenAPI(API_KEY, API_SECRET, API_DOMAIN)

# Trading strategy class to encapsulate trading logic
class TradingStrategy:
    def __init__(self, prices: Optional[List[float]] = None):
        self.prices = prices if prices else []
        self.last_buy_price = None
        self.last_sell_price = None
        self.last_trade_type = None
        self.cooldown_end_time = 0  # Track cooldown period
        self.stop_loss_percent = 0.05  # 5% stop loss
        self.take_profit_percent = 0.1  # 10% take profit

    def execute_strategy(self):
        current_price = kraken_api.get_btc_price()
        if current_price is None:
            logger.error("Failed to retrieve BTC price.")
            return

        # Append the current price to the price history
        self.prices.append(current_price)
        if len(self.prices) > 300:
            self.prices.pop(0)  # Keep only the latest 300 prices to save memory

        # Calculate indicators
        moving_avg = calculate_moving_average(self.prices)
        rsi = calculate_rsi(self.prices)
        macd, signal = calculate_macd(self.prices)

        logger.info(f"Current BTC Price: {current_price}, Moving Average: {moving_avg}, RSI: {rsi}, MACD: {macd}, Signal: {signal}")

        if moving_avg and rsi and macd and signal:
            self._determine_trade_action(current_price, macd, signal, rsi)

    def _determine_trade_action(self, current_price: float, macd: float, signal: float, rsi: float):
        current_time = time.time()
        if current_time < self.cooldown_end_time:
            logger.info("Cooldown period active. Skipping trade action.")
            return

        if self.last_trade_type == 'buy':
            # Check stop loss or take profit conditions
            if self.last_buy_price:
                potential_profit_loss = calculate_potential_profit_loss(current_price, self.last_buy_price)
                if potential_profit_loss <= -self.stop_loss_percent * 100:
                    logger.info(f"Stop loss triggered. Selling BTC at {current_price} due to {potential_profit_loss:.2f}% loss.")
                    self._execute_sell(current_price)
                    return
                elif potential_profit_loss >= self.take_profit_percent * 100:
                    logger.info(f"Take profit triggered. Selling BTC at {current_price} due to {potential_profit_loss:.2f}% gain.")
                    self._execute_sell(current_price)
                    return

        # Detailed analysis for trade conditions
        if macd <= signal:
            macd_reason = f"MACD ({macd}) is not greater than Signal ({signal})"
        else:
            macd_reason = "MACD is greater than Signal"

        if rsi >= 40:
            rsi_reason = f"RSI ({rsi}) is not below 40"
        else:
            rsi_reason = "RSI is below 40"

        if macd >= signal:
            sell_macd_reason = f"MACD ({macd}) is not less than Signal ({signal})"
        else:
            sell_macd_reason = "MACD is less than Signal"

        if rsi <= 60:
            sell_rsi_reason = f"RSI ({rsi}) is not above 60"
        else:
            sell_rsi_reason = "RSI is above 60"

        # Buy signal when MACD crossover and RSI < 40
        if macd > signal and rsi < 40:
            self._execute_buy(current_price)
        # Sell signal when MACD crossover below and RSI > 60
        elif macd < signal and rsi > 60:
            self._execute_sell(current_price)
        else:
            logger.info(f"No trade signal detected: MACD {macd}, Signal {signal}, RSI {rsi}. "
                        f"Buy condition: {macd_reason} and {rsi_reason}. "
                        f"Sell condition: {sell_macd_reason} and {sell_rsi_reason}.")

    def _execute_buy(self, current_price: float):
        potential_profit_loss = None
        if self.last_sell_price:
            potential_profit_loss = calculate_potential_profit_loss(current_price, self.last_sell_price)

        if self.last_trade_type != 'buy' and (potential_profit_loss is None or is_profitable_trade(potential_profit_loss)):
            logger.info(f"Buying BTC... Signal: MACD crossover above Signal, RSI < 40 (moderately oversold), Potential Profit: {potential_profit_loss if potential_profit_loss else 0:.2f}%")
            kraken_api.execute_trade(portfolio.portfolio['TRADING'], 'buy')
            self.last_buy_price = current_price
            self.last_trade_type = 'buy'
            self.cooldown_end_time = time.time() + 300  # Set a cooldown of 5 minutes

    def _execute_sell(self, current_price: float):
        potential_profit_loss = None
        if self.last_buy_price:
            potential_profit_loss = calculate_potential_profit_loss(current_price, self.last_buy_price)

        if self.last_trade_type != 'sell' and (potential_profit_loss is None or is_profitable_trade(potential_profit_loss)):
            logger.info(f"Selling BTC... Signal: MACD crossover below Signal, RSI > 60 (moderately overbought), Potential Profit: {potential_profit_loss if potential_profit_loss else 0:.2f}%")
            kraken_api.execute_trade(portfolio.portfolio['TRADING'], 'sell')
            self.last_sell_price = current_price
            self.last_trade_type = 'sell'
            self.cooldown_end_time = time.time() + 300  # Set a cooldown of 5 minutes

# Initialize TradingStrategy
trading_strategy_instance = TradingStrategy()

def trading_strategy(prices: List[float]):
    trading_strategy_instance.prices = prices
    trading_strategy_instance.execute_strategy()
