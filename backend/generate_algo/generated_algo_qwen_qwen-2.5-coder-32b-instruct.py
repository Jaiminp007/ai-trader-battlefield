import yfinance as yf
import numpy as np

_v8069bf_cache = {}

def execute_trade(ticker, cash_balance, shares_held):
    global _v8069bf_cache

    # Get real market data
    if ticker not in _v8069bf_cache:
        _v8069bf_cache[ticker] = yf.download(ticker, period="30d", interval="15m", progress=False)

    df = _v8069bf_cache.get(ticker)
    if df is None or len(df) < 100:
        return "HOLD"

    # Use REAL close prices with proper array handling
    v8069bf_close_prices = df['Close'].values.flatten()  # ALWAYS use .flatten()
    if len(v8069bf_close_prices) == 0:
        return "HOLD"
    
    v8069bf_current_price = float(v8069bf_close_prices[-1])

    # Example: Simple moving average with proper validation
    v8069bf_window_fast = 20
    v8069bf_window_slow = 50
    if len(v8069bf_close_prices) < v8069bf_window_slow:
        return "HOLD"
    
    # Calculate moving averages safely
    v8069bf_ma_fast = np.mean(v8069bf_close_prices[-v8069bf_window_fast:])
    v8069bf_ma_slow = np.mean(v8069bf_close_prices[-v8069bf_window_slow:])
    
    # Safe comparison with NaN check
    if np.isnan(v8069bf_ma_fast) or np.isnan(v8069bf_ma_slow) or np.isnan(v8069bf_current_price):
        return "HOLD"
    
    # Check for crossover
    v8069bf_cross_up = v8069bf_ma_fast > v8069bf_ma_slow and v8069bf_close_prices[-2] - v8069bf_ma_slow < 0
    v8069bf_cross_down = v8069bf_ma_fast < v8069bf_ma_slow and v8069bf_close_prices[-2] - v8069bf_ma_slow > 0
    
    # Check for divergence
    v8069bf_price_diff = v8069bf_current_price - v8069bf_ma_slow
    v8069bf_divergence_threshold = 0.015 * v8069bf_ma_slow
    
    v8069bf_buy_condition = v8069bf_cross_up and v8069bf_price_diff > v8069bf_divergence_threshold
    v8069bf_sell_condition = v8069bf_cross_down and v8069bf_price_diff < -v8069bf_divergence_threshold
    
    if v8069bf_buy_condition:
        return "BUY"
    elif v8069bf_sell_condition:
        return "SELL"
    else:
        return "HOLD"