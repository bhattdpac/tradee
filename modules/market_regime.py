# This module will contain the logic for market regime detection.
import pandas as pd
import numpy as np

def _calculate_atr(high, low, close, window=14):
    """Helper function to calculate ATR."""
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    tr = pd.concat([tr1, tr2, tr3], axis=1, join='inner').max(axis=1)
    atr = tr.ewm(alpha=1/window, adjust=False).mean()
    return atr

def get_market_regime(historical_data: pd.DataFrame, short_window=50, long_window=200, atr_window=14):
    """
    Determines the market regime based on moving averages and volatility.

    :param historical_data: DataFrame with 'High', 'Low', 'Close' columns.
    :param short_window: The window for the short-term moving average.
    :param long_window: The window for the long-term moving average.
    :param atr_window: The window for the ATR calculation.
    :return: A tuple containing the regime (str) and volatility (float).
    """
    if historical_data.empty or len(historical_data) < long_window:
        return "Not Enough Data", 0.0

    # Calculate Moving Averages
    data = historical_data.copy()
    data['short_ma'] = data['Close'].rolling(window=short_window).mean()
    data['long_ma'] = data['Close'].rolling(window=long_window).mean()

    # Calculate Volatility (ATR as a percentage of close price)
    data['atr'] = _calculate_atr(data['High'], data['Low'], data['Close'], window=atr_window)
    data['atr_pct'] = (data['atr'] / data['Close']) * 100

    # Get the latest values
    last_close = data['Close'].iloc[-1]
    last_short_ma = data['short_ma'].iloc[-1]
    last_long_ma = data['long_ma'].iloc[-1]
    last_atr_pct = data['atr_pct'].iloc[-1]

    # Determine Regime
    regime = "Ranging" # Default state
    if last_short_ma > last_long_ma and last_close > last_short_ma:
        regime = "Trend Up"
    elif last_short_ma < last_long_ma and last_close < last_short_ma:
        regime = "Trend Down"

    # Refine regime with volatility
    # We can define "Volatile" as ATR percentage being high, e.g., > 3%
    if last_atr_pct > 3.0 and regime == "Ranging":
        regime = "Volatile"
        
    # A simple breakout detection could be a sharp price move above/below a recent range.
    # For now, we will stick to the primary regimes.

    return regime, round(last_atr_pct, 2)