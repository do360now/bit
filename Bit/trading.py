import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
from termcolor import colored

from api_kraken import KrakenAPI
from config import (
    API_DOMAIN,
    API_KEY,
    API_SECRET,
    CURRENT_PORTFOLIO_SNAPSHOT,
    MIN_TRADE_VOLUME,
)
from indicators import (
    calculate_macd,  # Removed is_profitable_trade since it wasn't used
    calculate_moving_average,
    calculate_potential_profit_loss,
    calculate_rsi,
)
from logger_config import logger
from portfolio import portfolio


@dataclass
class StrategyResult:
    """Dataclass to hold the result of the strategy execution."""

    current_price: float
    rsi: float
    macd: float
    signal: float
    histogram: float
    thresholds: Dict[str, float]


class AdvancedTradingStrategy:
    def __init__(self, prices=None, risk_tolerance=0.02):
        # ... existing code ...
        self.eth_baseline = CURRENT_PORTFOLIO_SNAPSHOT["ETH"]["amount_eth_total"]
        self.kraken_api = KrakenAPI(API_KEY, API_SECRET, API_DOMAIN)
        self.current_eth = None  # Will be set externally or via a new method

        # State tracking
        self.last_trade_type = None
        self.cooldown_end_time = 0  # Make sure this is here!

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
        self.profitable_trades = 0  # Ensure this is defined!

        self.prices = prices if prices is not None else []

    def update_current_eth_holdings(self, current_eth: float):
        self.current_eth = current_eth

    def _calculate_dynamic_thresholds(self) -> Dict[str, float]:
        """
        Calculate adaptive trading thresholds based on recent price volatility.

        :return: A dictionary containing buy_rsi_threshold, sell_rsi_threshold,
                 stop_loss_percent, and take_profit_percent.
        """
        logger.debug("Calculating dynamic thresholds based on price volatility.")
        if len(self.prices) < 30:
            return {
                "buy_rsi_threshold": 50,
                "sell_rsi_threshold": 75,
                "stop_loss_percent": 0.10,
                "take_profit_percent": 0.10,
            }

        # Calculate price volatility
        recent_prices = self.prices[-30:]
        price_std = np.std(recent_prices)
        price_mean = np.mean(recent_prices) if np.mean(recent_prices) != 0 else 1.0
        volatility_ratio = price_std / price_mean

        # Adaptive thresholds
        thresholds = {
            "buy_rsi_threshold": max(50, 40 * (1 - volatility_ratio)),
            "sell_rsi_threshold": min(80, 60 * (1 + volatility_ratio)),
            "stop_loss_percent": max(0.05, min(0.10, volatility_ratio * 2)),
            "take_profit_percent": max(0.10, min(0.30, volatility_ratio * 3)),
        }

        return thresholds

    def execute_strategy(self) -> Optional[StrategyResult]:
        """
        Execute the trading strategy:
        1. Retrieve current price.
        2. Update historical prices.
        3. Calculate trading indicators (RSI, MACD, etc.).
        4. Determine buy/sell/hold action.

        :return: StrategyResult object containing current metrics if successful, else None.
        """
        logger.debug("Executing trading strategy.")
        # Retrieve current price
        current_price = self.kraken_api.get_eth_price()
        if current_price is None:
            logger.error("Failed to retrieve ETH price.")
            return None

        logger.info(f"Current ETH price: {current_price} USD")

        # Maintain price history
        self.prices.append(current_price)
        self.prices = self.prices[-300:]  # Keep last 300 prices

        # Calculate indicators and thresholds
        thresholds = self._calculate_dynamic_thresholds()
        logger.info(f"Dynamic thresholds: {thresholds}")

        # Calculate RSI
        rsi = calculate_rsi(self.prices)
        if rsi is None:
            logger.error("RSI calculation failed due to insufficient data.")
            return None
        logger.info(f"RSI: {rsi}")

        # Calculate MACD
        macd_data = calculate_macd(self.prices)
        if macd_data is None:
            logger.error("MACD calculation failed due to insufficient data.")
            return None
        macd, signal, histogram = macd_data
        logger.info(f"MACD: {macd}, Signal: {signal}, Histogram: {histogram}")

        # Determine trade action
        self._determine_trade_action(current_price, macd, signal, rsi, thresholds)

        # Return structured result
        return StrategyResult(
            current_price=current_price,
            rsi=rsi,
            macd=macd,
            signal=signal,
            histogram=histogram,
            thresholds=thresholds,
        )

    def _determine_trade_action(
        self,
        current_price: float,
        macd: float,
        signal: float,
        rsi: float,
        thresholds: Dict[str, float],
    ) -> None:
        """
        Determine and execute the appropriate trade action based on
        current indicators and thresholds.

        :param current_price: The current ETH price.
        :param macd: MACD value.
        :param signal: MACD signal line value.
        :param rsi: Current RSI value.
        :param thresholds: Threshold parameters dict.
        """
        logger.debug("Determining trade action based on indicators.")
        current_time = time.time()

        # Check cooldown period
        if current_time < self.cooldown_end_time:
            logger.info("In cooldown period, skipping trade action.")
            return

        # If there's an open position (indicated by last_trade_price), evaluate stop loss / take profit
        if self.last_trade_price is not None:
            potential_profit_loss = calculate_potential_profit_loss(
                current_price, self.last_trade_price
            )
            logger.info(f"Potential Profit/Loss: {potential_profit_loss}%")

            # Stop loss check
            if potential_profit_loss <= -thresholds["stop_loss_percent"] * 100:
                logger.info(
                    colored(
                        f"Stop loss triggered: Current Price={current_price}, Last Trade Price={self.last_trade_price}",
                        "red",
                    )
                )
                self._execute_sell(current_price, "Stop Loss Triggered")
                return

            # Take profit check
            if potential_profit_loss >= thresholds["take_profit_percent"] * 100:
                logger.info(
                    colored(
                        f"Take profit triggered: Current Price={current_price}, Last Trade Price={self.last_trade_price}",
                        "green",
                    )
                )
                self._execute_sell(current_price, "Take Profit Triggered")
                return

        # If no position yet, just log the conditions
        if self.last_trade_price is None:
            logger.info(
                colored(
                    f"No existing position. Checking for potential buy/sell signals.",
                    "yellow",
                )
            )

        # Calculate moving average
        moving_avg = calculate_moving_average(self.prices)
        if moving_avg is None:
            logger.error(
                colored(
                    "Moving average calculation failed due to insufficient data.", "red"
                )
            )
            return

        logger.info(f"Moving Average: {moving_avg}")

        # Buy signal conditions
        if (
            float(macd) > float(signal)
            and float(rsi) < thresholds["buy_rsi_threshold"]
            and current_price > float(moving_avg)
        ):
            logger.info(
                colored(
                    f"Buy conditions met: MACD ({macd}) > Signal ({signal}), "
                    f"RSI ({rsi}) < Buy Threshold ({thresholds['buy_rsi_threshold']}), "
                    f"Current Price ({current_price}) > Moving Average ({moving_avg})",
                    "green",
                )
            )
            self._execute_buy(current_price)
        else:
            logger.debug(
                f"Buy conditions not met: MACD ({macd}), Signal ({signal}), RSI ({rsi}), "
                f"Current Price ({current_price}), Moving Average ({moving_avg})"
            )

        # Sell signal conditions
        if (
            float(macd) < float(signal)
            and float(rsi) > thresholds["sell_rsi_threshold"]
            and current_price < float(moving_avg)
        ):
            logger.info(
                colored(
                    f"Sell conditions met: MACD ({macd}) < Signal ({signal}), "
                    f"RSI ({rsi}) > Sell Threshold ({thresholds['sell_rsi_threshold']}), "
                    f"Current Price ({current_price}) < Moving Average ({moving_avg})",
                    "red",
                )
            )
            self._execute_sell(current_price, "Technical Sell Signal")
        else:
            logger.debug(
                f"Sell conditions not met: MACD ({macd}), Signal ({signal}), RSI ({rsi}), "
                f"Current Price ({current_price}), Moving Average ({moving_avg})"
            )

    def _execute_buy(self, current_price: float) -> None:
        """
        Execute a buy order with enhanced logging and tracking.
        :param current_price: The current market price to base the limit order on.
        """
        logger.debug("Preparing to execute buy order.")
        trading_amount = portfolio.portfolio["TRADING"]

        # Set a limit order slightly below the current price
        limit_price = round(current_price * 0.999, 1)
        logger.info(
            f"Buy Signal: Target Limit Price={limit_price}, Trading Amount={trading_amount}"
        )
        try:
            if trading_amount > MIN_TRADE_VOLUME:
                self.kraken_api.execute_trade(trading_amount, "buy", price=limit_price)
                self.last_trade_price = limit_price
                self.last_trade_type = "buy"
                self.total_trades += 1
                self.trade_history.append(
                    {"type": "buy", "price": limit_price, "timestamp": time.time()}
                )

                logger.info(
                    colored(
                        f"Buy executed successfully at Limit Price={limit_price}",
                        "green",
                    )
                )
                self.cooldown_end_time = time.time() + 3600  # 1 hour cooldown
                return trading_amount
            else:
                logger.error("Insufficient funds for buying.")
        except Exception as e:
            logger.error(f"Buy execution failed: {e}")

    def _execute_sell(self, current_price: float, reason: str) -> None:
        """
        Execute a sell order with enhanced logging and tracking.
        :param current_price: The current market price to base the limit order on.
        :param reason: A string indicating why the sell was executed (e.g., "Stop Loss Triggered").
        """
        logger.debug("Preparing to execute sell order.")
        trading_amount = portfolio.portfolio["TRADING"]

        # Set a limit order slightly above the current price
        limit_price = round(current_price * 1.001, 1)
        logger.info(
            colored(
                f"Sell Signal: Target Limit Price={limit_price}, Reason={reason}, Trading Amount={trading_amount}",
                "red",
            )
        )
        try:
            if trading_amount > MIN_TRADE_VOLUME:
                self.kraken_api.execute_trade(trading_amount, "sell", price=limit_price)

                if self.last_trade_price is not None:
                    profit_loss = calculate_potential_profit_loss(
                        limit_price, self.last_trade_price
                    )
                    if profit_loss > 0:
                        self.profitable_trades += 1
                    logger.info(
                        f"Sell executed successfully at Limit Price={limit_price} with Profit/Loss={profit_loss}"
                    )

                self.last_trade_price = limit_price
                self.last_trade_type = "sell"
                self.total_trades += 1
                self.trade_history.append(
                    {
                        "type": "sell",
                        "price": limit_price,
                        "timestamp": time.time(),
                        "reason": reason,
                    }
                )

                self.cooldown_end_time = time.time() + 3600  # 1 hour cooldown
            else:
                logger.error("Insufficient funds for selling.")
        except Exception as e:
            logger.error(f"Sell execution failed: {e}")


# Initialize strategy
TRADING_STRATEGY_INSTANCE = AdvancedTradingStrategy()


def trading_strategy(prices: List[float]) -> Optional[StrategyResult]:
    """
    Public interface to run the trading strategy with given prices.
    :param prices: A list of historical prices to seed the strategy.
    :return: An optional StrategyResult object from the strategy execution.
    """
    logger.debug("Running trading_strategy function.")
    TRADING_STRATEGY_INSTANCE.prices = prices
    return TRADING_STRATEGY_INSTANCE.execute_strategy()
