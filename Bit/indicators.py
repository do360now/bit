import numpy as np
import pandas as pd
from typing import Optional, List

# Function to calculate Moving Average
def calculate_moving_average(prices: List[float], window: int = 7) -> Optional[float]:
    if len(prices) < window:
        return None  # Not enough data points yet
    return float(np.mean(prices[-window:]))

# Function to calculate Relative Strength Index (RSI)
def calculate_rsi(prices: List[float], window: int = 14) -> Optional[float]:
    if len(prices) < window + 1:
        return None  # Not enough data points yet
    delta = np.diff(prices)
    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)
    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])
    if avg_loss == 0:
        return 100.0  # Prevent division by zero, indicates strong upward trend
    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))

# Function to calculate Moving Average Convergence Divergence (MACD)
def calculate_macd(prices: List[float], short_window: int = 12, long_window: int = 26, signal_window: int = 7) -> Optional[tuple]:
    if len(prices) < long_window:
        return None, None  # Not enough data points yet
    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
    long_ema = prices_series.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return float(macd.iloc[-1]), float(signal.iloc[-1])

# Function to calculate potential profit or loss percentage
def calculate_potential_profit_loss(current_price: float, previous_price: float) -> float:
    return ((current_price - previous_price) / previous_price) * 100.0

# Function to determine if the potential gain/loss is greater than the transaction fee
def is_profitable_trade(potential_profit_loss: float, transaction_fee_percentage: float = 0.26) -> bool:
    return potential_profit_loss > transaction_fee_percentage
