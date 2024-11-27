# Trading Application Overview

## Introduction

This application is a comprehensive trading analysis toolkit designed to assist users in analyzing financial markets and making informed trading decisions. It features a technical indicators module (`indicators.py`), a trading signals module, and a data acquisition system. The application provides tools for calculating commonly used technical indicators, generating trading signals, backtesting strategies, and interacting with data through the the exchange APIs.

## Features

The application consists of the following components:

### 1. Technical Indicators Module (`indicators.py`)
This module includes implementations of the following technical indicators:

1. **Moving Average (MA)**: Calculates the simple moving average over a specified window size to smooth out price action.
   - **Function**: `moving_average(data, window_size)`

2. **Moving Average Convergence Divergence (MACD)**: Computes the MACD line, signal line, and histogram to identify trend direction and strength.
   - **Function**: `macd(data, short_window=12, long_window=26, signal_window=9)`

3. **Relative Strength Index (RSI)**: Calculates the RSI to identify overbought or oversold conditions.
   - **Function**: `rsi(data, window=14)`

4. **Bollinger Bands**: Computes upper and lower bands to identify volatility and potential price breakouts.
   - **Function**: `bollinger_bands(data, window=20, num_std_dev=2)`

5. **Stochastic RSI**: A momentum oscillator that combines RSI with the stochastic oscillator formula to provide more sensitivity in price movements.
   - **Function**: `stochastic_rsi(data, window=14)`



## Installation

To use this application, clone the repository and ensure you have Python installed, along with the required dependencies. You can install dependencies using:

```sh
pip install -r requirements.txt
```

The primary dependencies for this application include:
- `numpy`
- `pandas`
- `matplotlib`
- `fastapi`
- `jinja2`
- `httpx`

## Usage

Here is an example of how to use the indicators provided by the module:


To run the entire trading application, execute:

```sh
python3 main.py
```

This will start the app, allowing you to start trading.

## Description of Indicators

### Moving Average (MA)
A moving average smooths out price data by calculating the average price over a defined number of periods. This helps to identify trends by filtering out short-term fluctuations.

### Moving Average Convergence Divergence (MACD)
MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a price. It is used to detect changes in the strength, direction, momentum, and duration of a trend.

### Relative Strength Index (RSI)
RSI is a momentum oscillator that measures the speed and change of price movements. It is used to identify overbought or oversold conditions in a market.

### Bollinger Bands
Bollinger Bands are a type of price envelope that consists of a moving average and two standard deviations above and below the moving average. They are used to measure market volatility.

### Stochastic RSI
Stochastic RSI applies the stochastic oscillator formula to RSI values, providing a more sensitive indicator to assess overbought or oversold conditions.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributions
Contributions are welcome! If you find a bug or have an idea for an improvement, feel free to create an issue or sub



# Kraken Rest API with Enhanced Trading Strategy and Portfolio Allocation
#
# Usage: ./krakenapi endpoint [parameters]
# Example: ./krakenapi Time
# Example: ./krakenapi OHLC pair=xbtusd interval=1440
# Example: ./krakenapi Balance
# Example: ./krakenapi TradeBalance asset=xdg
# Example: ./krakenapi OpenPositions
# Example: ./krakenapi AddOrder pair=xxbtzusd type=buy ordertype=market volume=0.003 leverage=5