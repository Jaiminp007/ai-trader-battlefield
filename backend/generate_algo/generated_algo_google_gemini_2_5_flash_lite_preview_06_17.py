import yfinance as yf
import numpy as np

_unique_strategy_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _unique_strategy_cache

    DATA_PERIOD = "60d"
    INTERVAL = "1h"
    SHORT_WINDOW = 10
    LONG_WINDOW = 30
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    VOLUME_THRESHOLD_PERCENTILE = 75
    PRICE_CHANGE_THRESHOLD = 0.01

    if ticker not in _unique_strategy_cache:
        _unique_strategy_cache[ticker] = {}

    # Fetch data if not in cache or if cache is outdated
    if "data" not in _unique_strategy_cache[ticker] or _unique_strategy_cache[ticker]["period"] != DATA_PERIOD or _unique_strategy_cache[ticker]["interval"] != INTERVAL:
        historical_data = yf.download(ticker, period=DATA_PERIOD, interval=INTERVAL, progress=False)
        if historical_data.empty:
            return "HOLD"
        _unique_strategy_cache[ticker]["data"] = historical_data
        _unique_strategy_cache[ticker]["period"] = DATA_PERIOD
        _unique_strategy_cache[ticker]["interval"] = INTERVAL
    else:
        historical_data = _unique_strategy_cache[ticker]["data"]

    all_close_prices = historical_data['Close'].values.flatten()
    all_volumes = historical_data['Volume'].values.flatten()

    if len(all_close_prices) < max(LONG_WINDOW, RSI_PERIOD) or len(all_volumes) < LONG_WINDOW:
        return "HOLD"

    current_price = float(all_close_prices[-1])
    
    # --- Momentum Strategy (Dual Crossover) ---
    if len(all_close_prices) >= LONG_WINDOW:
        short_ma = np.mean(all_close_prices[-SHORT_WINDOW:])
        long_ma = np.mean(all_close_prices[-LONG_WINDOW:])

        if np.isnan(short_ma) or np.isnan(long_ma) or np.isnan(current_price):
            return "HOLD"

        # Momentum signal: Crossover
        if short_ma > long_ma and short_ma * 1.005 < current_price: # Price is rising and short MA crossed above long MA
            momentum_signal = 1 # Bullish
        elif short_ma < long_ma and short_ma * 0.995 > current_price: # Price is falling and short MA crossed below long MA
            momentum_signal = -1 # Bearish
        else:
            momentum_signal = 0

    else: # Not enough data for momentum, default to HOLD
        momentum_signal = 0

    # --- Volatility Strategy (RSI) ---
    if len(all_close_prices) >= RSI_PERIOD:
        delta = np.diff(all_close_prices)
        gain = delta.copy()
        loss = delta.copy()
        gain[loss >= 0] = 0
        loss[gain > 0] = 0

        avg_gain = np.mean(gain[:RSI_PERIOD])
        avg_loss = np.mean(abs(loss[:RSI_PERIOD]))

        # Prevent division by zero
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))

        if np.isnan(rsi):
            rsi_signal = 0
        elif rsi < RSI_OVERSOLD:
            rsi_signal = 1 # Bullish (oversold)
        elif rsi > RSI_OVERBOUGHT:
            rsi_signal = -1 # Bearish (overbought)
        else:
            rsi_signal = 0
    else: # Not enough data for RSI, default to HOLD
        rsi_signal = 0

    # --- Volume Confirmation ---
    recent_volumes = all_volumes[-SHORT_WINDOW:]
    if len(recent_volumes) > 0:
        average_short_term_volume = np.mean(recent_volumes)
        volume_percentile = np.percentile(all_volumes, VOLUME_THRESHOLD_PERCENTILE)
        
        if np.isnan(average_short_term_volume) or np.isnan(volume_percentile):
            volume_confirmation = 0
        elif average_short_term_volume > volume_percentile:
            volume_confirmation = 1 # High volume
        else:
            volume_confirmation = 0
    else:
        volume_confirmation = 0

    # --- Trading Logic (Conditional) ---
    # Aggressive approach: aim for 30-50% buy/sell
    
    # BUY condition: Bullish momentum, oversold RSI, and high volume confirmation
    if momentum_signal == 1 and rsi_signal == 1 and volume_confirmation == 1:
        return "BUY"
    # SELL condition: Bearish momentum, overbought RSI, and high volume confirmation
    elif momentum_signal == -1 and rsi_signal == -1 and volume_confirmation == 1:
        return "SELL"
    # BUY condition: Strong bullish momentum and oversold RSI (even without high volume)
    elif momentum_signal == 1 and rsi_signal == 1:
        return "BUY"
    # SELL condition: Strong bearish momentum and overbought RSI (even without high volume)
    elif momentum_signal == -1 and rsi_signal == -1:
        return "SELL"
    # HOLD condition: No strong signals or conflicting signals
    else:
        return "HOLD"