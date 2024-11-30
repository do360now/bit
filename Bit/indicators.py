import numpy as np
import pandas as pd
from typing import List, Optional, Tuple

def calculate_moving_average(prices: List[float], window: int = 7, mode: str = 'simple') -> Optional[float]:
    if len(prices) < window:
        return None
    
    if mode == 'simple':
        return float(np.mean(prices[-window:]))
    elif mode == 'exponential':
        return float(pd.Series(prices).ewm(span=window, adjust=False).mean().iloc[-1])
    else:
        raise ValueError(f"Unsupported moving average mode: {mode}")

def calculate_rsi(prices: List[float], window: int = 14, smoothing: bool = True) -> Optional[float]:
    if len(prices) < window + 1:
        return None

    delta = np.diff(prices)
    gains = np.maximum(delta, 0)
    losses = np.abs(np.minimum(delta, 0))

    avg_gain = pd.Series(gains).rolling(window=window).mean() if smoothing else np.mean(gains[-window:])
    avg_loss = pd.Series(losses).rolling(window=window).mean() if smoothing else np.mean(losses[-window:])

    # Ensure avg_gain and avg_loss are scalars before use
    avg_gain = float(avg_gain.iloc[-1]) if isinstance(avg_gain, pd.Series) else avg_gain
    avg_loss = float(avg_loss.iloc[-1]) if isinstance(avg_loss, pd.Series) else avg_loss

    rs = avg_gain / avg_loss if avg_loss != 0 else 1
    return float(100.0 - (100.0 / (1.0 + rs)))


def calculate_macd(
    prices: List[float], 
    short_window: int = 12, 
    long_window: int = 26, 
    signal_window: int = 9
) -> Optional[Tuple[float, float, float]]:
    if len(prices) < long_window:
        return None
    
    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
    long_ema = prices_series.ewm(span=long_window, adjust=False).mean()
    
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    histogram = macd - signal_line
    
    return (
        float(macd.iloc[-1]), 
        float(signal_line.iloc[-1]), 
        float(histogram.iloc[-1])
    )

def calculate_bollinger_bands(prices: List[float], window: int = 20, num_std: float = 2.0) -> Optional[dict]:
    if len(prices) < window:
        return None
    
    prices_series = pd.Series(prices)
    rolling_mean = prices_series.rolling(window=window).mean()
    rolling_std = prices_series.rolling(window=window).std()
    
    return {
        'middle_band': float(rolling_mean.iloc[-1]),
        'upper_band': float(rolling_mean.iloc[-1] + num_std * rolling_std.iloc[-1]),
        'lower_band': float(rolling_mean.iloc[-1] - num_std * rolling_std.iloc[-1])
    }

def calculate_potential_profit_loss(current_price: float, previous_price: float) -> float:
    return ((current_price - previous_price) / previous_price) * 100.0

def is_profitable_trade(potential_profit_loss: float, transaction_fee_percentage: float = 0.0026) -> bool:
    total_fees = transaction_fee_percentage * 2  # Considering both buy and sell fees
    return potential_profit_loss > total_fees
