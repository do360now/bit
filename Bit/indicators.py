import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Dict


def calculate_moving_average(
    prices: List[float], window: int = 7, mode: str = "simple"
) -> Optional[float]:
    """
    Calculate the moving average of a list of prices.

    :param prices: A list of price values.
    :param window: The number of data points to consider for the moving average.
    :param mode: The moving average type ('simple' or 'exponential').
    :return: The moving average as a float, or None if not enough data.
    """
    if len(prices) < window:
        return None

    if mode == "simple":
        return float(np.mean(prices[-window:]))
    elif mode == "exponential":
        return float(pd.Series(prices).ewm(span=window, adjust=False).mean().iloc[-1])
    else:
        raise ValueError(f"Unsupported moving average mode: {mode}")


def calculate_rsi(
    prices: List[float], window: int = 14, smoothing: bool = True
) -> Optional[float]:
    """
    Calculate the Relative Strength Index (RSI) for a list of prices.

    :param prices: A list of price values.
    :param window: The look-back window size for RSI calculation.
    :param smoothing: Whether to apply rolling mean smoothing.
    :return: The RSI value as a float, or None if insufficient data.
    """
    if len(prices) < window + 1:
        return None

    delta = np.diff(prices)
    gains = np.maximum(delta, 0)
    losses = np.abs(np.minimum(delta, 0))

    if smoothing:
        avg_gain = pd.Series(gains).rolling(window=window).mean()
        avg_loss = pd.Series(losses).rolling(window=window).mean()
        # Extract the final scalar values from the rolling calculation
        avg_gain = float(avg_gain.iloc[-1])
        avg_loss = float(avg_loss.iloc[-1])
    else:
        avg_gain = np.mean(gains[-window:])
        avg_loss = np.mean(losses[-window:])

    # Avoid division by zero
    if avg_loss == 0:
        rs = 1.0  # If there's no loss at all, RSI approaches 100
    else:
        rs = avg_gain / avg_loss

    return float(100.0 - (100.0 / (1.0 + rs)))


def calculate_macd(
    prices: List[float],
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
) -> Optional[Tuple[float, float, float]]:
    """
    Calculate the MACD (Moving Average Convergence Divergence) indicator and return
    the MACD, signal line, and histogram.

    :param prices: A list of price values.
    :param short_window: The short EMA window for MACD calculation.
    :param long_window: The long EMA window for MACD calculation.
    :param signal_window: The signal line EMA window.
    :return: A tuple (macd, signal, histogram), or None if insufficient data.
    """
    if len(prices) < long_window:
        return None

    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
    long_ema = prices_series.ewm(span=long_window, adjust=False).mean()

    macd_values = short_ema - long_ema
    signal_line = macd_values.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_values - signal_line

    return (
        float(macd_values.iloc[-1]),
        float(signal_line.iloc[-1]),
        float(histogram.iloc[-1]),
    )


def calculate_bollinger_bands(
    prices: List[float], window: int = 20, num_std: float = 2.0
) -> Optional[Dict[str, float]]:
    """
    Calculate Bollinger Bands for a list of prices.

    :param prices: A list of price values.
    :param window: The number of data points for the rolling calculation.
    :param num_std: The number of standard deviations to determine the bands.
    :return: A dict containing 'middle_band', 'upper_band', 'lower_band', or None if insufficient data.
    """
    if len(prices) < window:
        return None

    prices_series = pd.Series(prices)
    rolling_mean = prices_series.rolling(window=window).mean()
    rolling_std = prices_series.rolling(window=window).std()

    return {
        "middle_band": float(rolling_mean.iloc[-1]),
        "upper_band": float(rolling_mean.iloc[-1] + num_std * rolling_std.iloc[-1]),
        "lower_band": float(rolling_mean.iloc[-1] - num_std * rolling_std.iloc[-1]),
    }


def calculate_potential_profit_loss(
    current_price: float, previous_price: float
) -> float:
    """
    Calculate the potential profit or loss percentage given the current and previous prices.

    :param current_price: The current market price.
    :param previous_price: The price at which the position was opened.
    :return: The potential profit/loss in percentage.
    """
    return ((current_price - previous_price) / previous_price) * 100.0


def is_profitable_trade(
    potential_profit_loss: float, transaction_fee_percentage: float = 0.0026
) -> bool:
    """
    Determine if a trade is profitable after considering transaction fees.

    :param potential_profit_loss: The profit or loss percentage before fees.
    :param transaction_fee_percentage: The trading fee percentage per transaction.
    :return: True if profitable after fees, False otherwise.
    """
    # Considering both buy and sell fees
    total_fees = transaction_fee_percentage * 2
    return potential_profit_loss > total_fees
