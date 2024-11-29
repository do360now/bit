import time
import numpy as np
from typing import List, Optional
from api_kraken import KrakenAPI
from indicators import (
    calculate_moving_average, 
    calculate_rsi, 
    calculate_macd, 
    calculate_potential_profit_loss, 
    is_profitable_trade
)
from portfolio import portfolio
from config import MIN_TRADE_VOLUME, API_KEY, API_SECRET, API_DOMAIN
from logger_config import logger
from termcolor import colored

class AdvancedTradingStrategy:
    def __init__(self, prices: Optional[List[float]] = None, risk_tolerance: float = 0.02):
        self.prices = prices or []
        self.kraken_api = KrakenAPI(API_KEY, API_SECRET, API_DOMAIN)
        
        # Enhanced risk management
        self.risk_tolerance = risk_tolerance
        self.last_trade_price = None
        self.trade_history = []
        
        # Adaptive parameters
        self.stop_loss_multiplier = 1.0
        self.take_profit_multiplier = 1.0
        
        # State tracking
        self.last_trade_type = None
        self.cooldown_end_time = 0
        
        # Performance tracking
        self.total_trades = 0
        self.profitable_trades = 0

    def _calculate_dynamic_thresholds(self):
        """Calculate adaptive trading thresholds based on recent price volatility."""
        if len(self.prices) < 30:
            return {
                'buy_rsi_threshold': 40,
                'sell_rsi_threshold': 60,
                'stop_loss_percent': 0.05,
                'take_profit_percent': 0.10
            }
        
        # Calculate price volatility
        price_std = np.std(self.prices[-30:])
        price_mean = np.mean(self.prices[-30:])
        volatility_ratio = price_std / price_mean
        
        # Adaptive thresholds
        thresholds = {
            'buy_rsi_threshold': max(30, 40 * (1 - volatility_ratio)),
            'sell_rsi_threshold': min(70, 60 * (1 + volatility_ratio)),
            'stop_loss_percent': max(0.03, min(0.10, volatility_ratio * 2)),
            'take_profit_percent': max(0.05, min(0.20, volatility_ratio * 3))
        }
        
        return thresholds

    def execute_strategy(self):
        # Retrieve current price
        current_price = self.kraken_api.get_btc_price()
        logger.info(f"Current BTC price: {current_price}")
        if current_price is None:
            logger.error("Failed to retrieve BTC price.")
            return

        # Maintain price history
        self.prices.append(current_price)
        self.prices = self.prices[-300:]  # Keep last 300 prices

        # Calculate indicators
        thresholds = self._calculate_dynamic_thresholds()
        logger.info(f"Dynamic thresholds: {thresholds}")

        
        # Calculate RSI
        rsi = calculate_rsi(self.prices)
        logger.info(f"RSI: {rsi}")
        if rsi is None:
            logger.error("RSI calculation failed due to insufficient data.")
            return  # Exit early if RSI cannot be calculated

        # Calculate MACD
        macd_data = calculate_macd(self.prices)
        if macd_data is None:
            logger.error("MACD calculation failed due to insufficient data.")
            return  # Exit early if MACD cannot be calculated
        else:
            macd, signal, histogram = macd_data
            logger.info(f"MACD: {macd}, Signal: {signal}, Histogram: {histogram}")

        # Now all indicators are properly initialized and valid
        self._determine_trade_action(
            current_price,
            macd,
            signal,
            rsi,
            thresholds
        )

        # Optionally, you could return some status or result
        return {
            "current_price": current_price,
            "rsi": rsi,
            "macd": macd,
            "signal": signal,
            "histogram": histogram,
            "thresholds": thresholds,
        }


    def _determine_trade_action(self, current_price, macd, signal, rsi, thresholds):
        current_time = time.time()

        # Check cooldown and existing position
        if current_time < self.cooldown_end_time:
            logger.info("In cooldown period, skipping trade action.")
            return

        # Check existing position profit/loss if applicable
        if self.last_trade_price:
            potential_profit_loss = calculate_potential_profit_loss(
                current_price, 
                self.last_trade_price
            )
            logger.info(f"Potential Profit/Loss: {potential_profit_loss}%")

            # Stop loss check
            if potential_profit_loss <= -thresholds['stop_loss_percent'] * 100:
                logger.info(colored(f"Stop loss triggered: Current Price={current_price}, Last Trade Price={self.last_trade_price}", "red"))
                self._execute_sell(current_price, "Stop Loss Triggered")
                return

            # Take profit check
            if potential_profit_loss >= thresholds['take_profit_percent'] * 100:
                logger.info(colored(f"Take profit triggered: Current Price={current_price}, Last Trade Price={self.last_trade_price}", "green"))
                self._execute_sell(current_price, "Take Profit Triggered")
                return

        if not self.last_trade_price:
            logger.info(colored(f"No trade executed. Conditions not met: MACD ({macd}) > Signal ({signal}), RSI ({rsi}) within thresholds.", "yellow"))

        # Calculate moving average
        moving_avg = calculate_moving_average(self.prices)
        logger.info(f"Moving Average: {moving_avg}")
        if moving_avg is None:
            logger.error(colored("Moving average calculation failed due to insufficient data.", "red"))
            return
        macd = float(macd)
        signal = float(signal)
        rsi = float(rsi)
        moving_avg = float(moving_avg)

        # Buy signal: More nuanced conditions
        if (macd > signal and 
            rsi < thresholds['buy_rsi_threshold'] and 
            current_price > moving_avg):
            logger.info(colored(f"Buy conditions met: MACD ({macd}) > Signal ({signal}), RSI ({rsi}) < Buy Threshold ({thresholds['buy_rsi_threshold']}), Current Price ({current_price}) > Moving Average ({moving_avg})", "green"))
            self._execute_buy(current_price)
            logger.info(colored("Buy Signal Triggered"), "green")
        else:
            logger.info(colored(f"Buy conditions not met: MACD ({macd}), Signal ({signal}), RSI ({rsi}), Current Price ({current_price}), Moving Average ({moving_avg})", "yellow"))
        
        # Sell signal: More nuanced conditions
        if (macd < signal and 
            rsi > thresholds['sell_rsi_threshold'] and 
            current_price < moving_avg):
            logger.info(colored(f"Sell conditions met: MACD ({macd}) < Signal ({signal}), RSI ({rsi}) > Sell Threshold ({thresholds['sell_rsi_threshold']}), Current Price ({current_price}) < Moving Average ({moving_avg})", "red"))
            self._execute_sell(current_price, "Technical Sell Signal")
            logger.info(colored("Sell Signal Triggered", "red"))
        else:
            logger.info(colored(f"Sell conditions not met: MACD ({macd}), Signal ({signal}), RSI ({rsi}), Current Price ({current_price}), Moving Average ({moving_avg})", "yellow"))


    def _execute_buy(self, current_price):
        """Execute buy with enhanced logging and tracking."""
        trading_amount = portfolio.portfolio['TRADING']

        # Add a limit buffer to try and buy at a lower price
        limit_price = current_price * 0.999, 1  # Set a limit order 0.1% below the current market price
        logger.info(f"Buy Signal: Target Limit Price={limit_price}, Trading Amount={trading_amount}")
        try:
            self.kraken_api.execute_trade(trading_amount, 'buy', price=limit_price)

            # Update tracking
            self.last_trade_price = limit_price
            self.last_trade_type = 'buy'
            self.total_trades += 1
            self.trade_history.append({
                'type': 'buy', 
                'price': limit_price, 
                'timestamp': time.time()
            })

            logger.info(colored(f"Buy executed successfully at Limit Price={limit_price}"), "green")

            # Set cooldown
            self.cooldown_end_time = time.time() + 300

        except Exception as e:
            logger.error(f"Buy execution failed: {e}")

    def _execute_sell(self, current_price, reason):
        """Execute sell with enhanced logging and tracking."""
        trading_amount = portfolio.portfolio['TRADING']

        # Add a limit buffer to try and sell at a higher price
        limit_price = current_price * 1.001, 1  # Set a limit order 0.1% above the current market price
        logger.info(f"Sell Signal: Target Limit Price={limit_price}, Reason={reason}, Trading Amount={trading_amount}")
        try:
            self.kraken_api.execute_trade(trading_amount, 'sell', price=limit_price)

            # Update tracking
            if self.last_trade_price:
                profit_loss = calculate_potential_profit_loss(
                    limit_price, 
                    self.last_trade_price
                )
                if profit_loss > 0:
                    self.profitable_trades += 1
                logger.info(f"Sell executed successfully at Limit Price={limit_price} with Profit/Loss={profit_loss}")

            self.last_trade_price = limit_price
            self.last_trade_type = 'sell'
            self.total_trades += 1
            self.trade_history.append({
                'type': 'sell', 
                'price': limit_price, 
                'timestamp': time.time(),
                'reason': reason
            })

            # Set cooldown
            self.cooldown_end_time = time.time() + 300

        except Exception as e:
            logger.error(f"Sell execution failed: {e}")

# Initialize strategy
trading_strategy_instance = AdvancedTradingStrategy()

def trading_strategy(prices: List[float]):
    trading_strategy_instance.prices = prices
    trading_strategy_instance.execute_strategy()