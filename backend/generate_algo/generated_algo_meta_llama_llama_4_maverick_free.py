import yfinance as yf
import numpy as np

_fb_cache = {}

def execute_trade(ticker, cash_balance, shares_held):
    global _fb_cache
    try:
        if ticker not in _fb_cache:
            _fb_cache[ticker] = yf.download(ticker, period='5d', interval='1m', progress=False)
        df = _fb_cache.get(ticker)
        if df is None or len(df) < 20:
            return 'HOLD'
        close_prices = df['Close'].values.flatten()
        if len(close_prices) < 20:
            return 'HOLD'
        cur = float(close_prices[-1])
        fast = int(5)
        slow = int(15)
        ma_fast = np.mean(close_prices[-fast:])
        ma_slow = np.mean(close_prices[-slow:])
        if np.isnan(ma_fast) or np.isnan(ma_slow):
            return 'HOLD'
        if ma_fast > ma_slow * 1.0005:
            return 'BUY'
        if ma_fast < ma_slow * 0.9995:
            return 'SELL'
        return 'HOLD'
    except Exception:
        return 'HOLD'
