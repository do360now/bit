import time
from api_kraken import KrakenAPI
from indicators import calculate_moving_average, calculate_rsi, calculate_macd, calculate_potential_profit_loss, is_profitable_trade, calculate_sentiment, fetch_latest_news
from portfolio import portfolio
from config import MIN_TRADE_VOLUME, API_KEY, API_SECRET, API_DOMAIN
from logger_config import logger
from typing import List, Optional
from termcolor import colored

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
        self.stop_loss_percent = 0.03  # 3% stop loss
        self.take_profit_percent = 0.15  # 15% take profit
        self.sentiment_score = 0.0  # Initialize sentiment score

    def update_sentiment(self):
        articles = fetch_latest_news()
        self.sentiment_score = calculate_sentiment(articles)
        logger.info(f"Updated sentiment score: {self.sentiment_score}")

    def execute_strategy(self):
        # Update sentiment score before executing the strategy
        self.update_sentiment()

        current_price = kraken_api.get_ETH_price()
        if current_price is None:
            logger.error("Failed to retrieve ETH price.")
            return

        # Append the current price to the price history
        self.prices.append(current_price)
        if len(self.prices) > 300:
            self.prices.pop(0)  # Keep only the latest 300 prices to save memory

        # Calculate indicators
        moving_avg = calculate_moving_average(self.prices)
        rsi = calculate_rsi(self.prices)
        macd, signal = calculate_macd(self.prices)

        logger.info(f"Current ETH Price: {current_price}, Moving Average: {moving_avg}, RSI: {rsi}, MACD: {macd}, Signal: {signal}, Sentiment Score: {self.sentiment_score}")

        if moving_avg and rsi and macd and signal:
            self._determine_trade_action(current_price, macd, signal, rsi)

    
    def _determine_trade_action(self, current_price: float, macd: float, signal: float, rsi: float):
        # Integrate sentiment into the trade decision
        if self.sentiment_score > 0.5:
            logger.info("Strong positive sentiment detected. Considering more aggressive buying opportunity...")
            # Adjust thresholds to be more aggressive for buying
            adjusted_rsi_threshold = 65  # Allow RSI up to 65 for strong sentiment
            if macd > signal * 0.9 and rsi < adjusted_rsi_threshold:  # Allow a slight MACD-Signal crossover lag
                logger.info(f"MACD ({macd}) > 0.9 * Signal ({signal}) and RSI ({rsi}) < {adjusted_rsi_threshold} with strong positive sentiment. Executing buy.")
                self._execute_buy(current_price)
            else:
                logger.info(colored(f"Conditions not met for buying despite strong positive sentiment: MACD {macd}, Signal {signal}, RSI {rsi}.", 'yellow'))

        elif 0.1 < self.sentiment_score <= 0.5:
            logger.info("Moderate positive sentiment detected. Considering buying opportunity...")
            # Use normal conditions for moderate positive sentiment
            if macd > signal and rsi < 60:
                logger.info(f"MACD ({macd}) > Signal ({signal}) and RSI ({rsi}) < 60 with moderate positive sentiment. Executing buy.")
                self._execute_buy(current_price)
            else:
                logger.info(colored(f"Conditions not met for buying despite moderate positive sentiment: MACD {macd}, Signal {signal}, RSI {rsi}.", 'yellow'))

        elif self.sentiment_score < -0.5:
            logger.info("Strong negative sentiment detected. Considering more aggressive selling opportunity...")
            # Adjust thresholds to be more aggressive for selling
            adjusted_rsi_threshold = 50  # Allow selling even if RSI is above 50 when sentiment is strongly negative
            if macd < signal * 1.1 and rsi > adjusted_rsi_threshold:  # Allow MACD-Signal crossover lag for faster sell
                logger.info(f"MACD ({macd}) < 1.1 * Signal ({signal}) and RSI ({rsi}) > {adjusted_rsi_threshold} with strong negative sentiment. Executing sell.")
                self._execute_sell(current_price)
            else:
                logger.info(colored(f"Conditions not met for selling despite strong negative sentiment: MACD {macd}, Signal {signal}, RSI {rsi}.", 'yellow'))

        elif -0.5 <= self.sentiment_score < -0.1:
            logger.info("Moderate negative sentiment detected. Considering selling opportunity...")
            # Use normal conditions for moderate negative sentiment
            if macd < signal and rsi > 45:
                logger.info(f"MACD ({macd}) < Signal ({signal}) and RSI ({rsi}) > 45 with moderate negative sentiment. Executing sell.")
                self._execute_sell(current_price)
            else:
                logger.info(colored(f"Conditions not met for selling despite moderate negative sentiment: MACD {macd}, Signal {signal}, RSI {rsi}.", 'yellow'))

        else:
            logger.info("Neutral sentiment detected. Proceeding with regular MACD and RSI checks.")
            # Buy signal when MACD crossover and RSI < 40
            if macd > signal and rsi < 40:
                logger.info(f"MACD ({macd}) > Signal ({signal}) and RSI ({rsi}) < 40. Executing buy.")
                self._execute_buy(current_price)
            # Sell signal when MACD crossover below and RSI > 60
            elif macd < signal and rsi > 60:
                logger.info(f"MACD ({macd}) < Signal ({signal}) and RSI ({rsi}) > 60. Executing partial sell.")
                self._execute_partial_sell(current_price)
            else:
                logger.info(colored(f"No trade signal detected: MACD {macd}, Signal {signal}, RSI {rsi}. Conditions for buying: MACD > Signal and RSI < 40. Conditions for selling: MACD < Signal and RSI > 60.", 'yellow'))


    def _execute_buy(self, current_price: float):
        potential_profit_loss = None
        if self.last_sell_price:
            potential_profit_loss = calculate_potential_profit_loss(current_price, self.last_sell_price)

        # Check market volume or trends to ensure buying during upward momentum
        market_volume = kraken_api.get_market_volume()
        if market_volume and market_volume < 100:
            logger.info(f"Market volume ({market_volume}) is too low for a confident buy. Skipping buy action.")
            return

        if self.last_trade_type != 'buy' and (potential_profit_loss is None or is_profitable_trade(potential_profit_loss)):
            logger.info(colored(f"Buying ETH... Signal: MACD crossover above SignalRSI < 40 (moderately oversold), Potential Profit: {potential_profit_loss if potential_profit_loss else 0:.2f}%, Market Volume: {market_volume}", 'green'))
            kraken_api.execute_trade(portfolio.portfolio['TRADING'], 'buy')
            self.last_buy_price = current_price
            self.last_trade_type = 'buy'

    def _execute_partial_sell(self, current_price: float):
        potential_profit_loss = None
        if self.last_buy_price:
            potential_profit_loss = calculate_potential_profit_loss(current_price, self.last_buy_price)

        if self.last_trade_type != 'sell' and (potential_profit_loss is None or is_profitable_trade(potential_profit_loss)):
            logger.info(colored(f"Partially selling ETH...Signal: MACD crossover below SignalRSI > 60 (moderately overbought), Potential Profit: {potential_profit_loss if potential_profit_loss else 0:.2f}%", 'yellow'))
            # Execute a partial sell - selling 50% of the current trading amount
            kraken_api.execute_trade(portfolio.portfolio['TRADING'] / 2, 'sell')
            self.last_sell_price = current_price
            self.last_trade_type = 'sell'

# Initialize TradingStrategy
trading_strategy_instance = TradingStrategy()

def trading_strategy(prices: List[float]):
    trading_strategy_instance.prices = prices
    trading_strategy_instance.execute_strategy()
