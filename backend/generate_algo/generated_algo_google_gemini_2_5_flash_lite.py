import yfinance as yf
import numpy as np

_aapl_market_history_cache = {}

def execute_trade(ticker, cash_balance, shares_held):
    global _aapl_market_history_cache

    if ticker != "AAPL":
        return "HOLD"

    data_period = "60d"
    data_interval = "1h"
    
    if ticker not in _aapl_market_history_cache:
        _aapl_market_history_cache[ticker] = yf.download(ticker, period=data_period, interval=data_interval, progress=False)

    df = _aapl_market_history_cache.get(ticker)

    required_length = 30 * 24 # Approximately 30 days of hourly data
    if df is None or len(df) < required_length:
        return "HOLD"

    close_prices = df['Close'].values.flatten()
    volume = df['Volume'].values.flatten()

    if len(close_prices) == 0 or len(volume) == 0:
        return "HOLD"

    current_price = float(close_prices[-1])

    # Strategy Type: TECHNICAL INDICATORS (RSI and MACD)
    # Data Period: MEDIUM-TERM (30 days seems appropriate here for hourly data)
    # Indicator Combination: DUAL CROSSOVER (inspired by RSI and MACD signals)
    # Threshold Values: AGGRESSIVE (for more frequent trading)
    # Trading Logic: CONDITIONAL
    # Portfolio Management: BALANCED

    # Calculate RSI
    rsi_window = 14
    if len(close_prices) < rsi_window + 1:
        return "HOLD"
    
    delta = np.diff(close_prices)
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    
    avg_gain = np.mean(gain[-rsi_window:])
    avg_loss = np.abs(np.mean(loss[-rsi_window:]))

    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
    
    rsi_agg_threshold_buy = 30.0
    rsi_agg_threshold_sell = 70.0

    # Calculate MACD
    ema_short_period = 12
    ema_long_period = 26
    signal_period = 9
    
    if len(close_prices) < ema_long_period:
        return "HOLD"

    def calculate_ema(prices, period):
        ema_values = np.zeros_like(prices)
        ema_values[0] = np.mean(prices[:period])
        for i in range(1, len(prices)):
            ema_values[i] = (prices[i] - ema_values[i-1]) * (2 / (period + 1)) + ema_values[i-1]
        return ema_values

    ema_short = calculate_ema(close_prices, ema_short_period)
    ema_long = calculate_ema(close_prices, ema_long_period)
    
    if len(ema_short) == 0 or len(ema_long) == 0 or len(ema_short) != len(ema_long):
        return "HOLD"

    macd_line = ema_short - ema_long
    
    if len(macd_line) < signal_period:
        return "HOLD"

    macd_signal = calculate_ema(macd_line, signal_period)
    
    if len(macd_signal) == 0 or len(macd_line) == 0 or len(macd_signal) != len(macd_line):
        return "HOLD"

    macd_histogram = macd_line - macd_signal

    macd_agg_threshold_buy = 0.01 * current_price # Aggressive threshold based on current price
    macd_agg_threshold_sell = -0.01 * current_price # Aggressive threshold based on current price
    
    # Trading Logic: CONDITIONAL
    buy_signal = False
    sell_signal = False

    # RSI buy condition: RSI below 30 (oversold)
    if rsi < rsi_agg_threshold_buy:
        # MACD buy condition: MACD line crosses above signal line AND histogram is positive
        if macd_histogram[-1] > 0 and macd_histogram[-2] < 0:
            buy_signal = True

    # RSI sell condition: RSI above 70 (overbought)
    if rsi > rsi_agg_threshold_sell:
        # MACD sell condition: MACD line crosses below signal line AND histogram is negative
        if macd_histogram[-1] < 0 and macd_histogram[-2] > 0:
            sell_signal = True
            
    # Volume confirmation (simple check for above average volume)
    avg_volume = np.mean(volume[-required_length:])
    if volume[-1] > avg_volume:
        if buy_signal:
            return "BUY"
        if sell_signal:
            return "SELL"
    else:
        # Lower conviction without high volume, revert to HOLD unless RSI is extremely strong
        if (rsi < rsi_agg_threshold_buy - 5) and (macd_histogram[-1] > 0 and macd_histogram[-2] < 0):
            return "BUY"
        if (rsi > rsi_agg_threshold_sell + 5) and (macd_histogram[-1] < 0 and macd_histogram[-2] > 0):
            return "SELL"

    return "HOLD"