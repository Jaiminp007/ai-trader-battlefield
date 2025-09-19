import yfinance as yf
import numpy as np

_v061a48_cache = {}

def execute_trade(ticker, cash_balance, shares_held):
    global _v061a48_cache
    if ticker not in _v061a48_cache:
        _v061a48_cache[ticker] = yf.download(ticker, period="30d", interval="15m", progress=False)
    df = _v061a48_cache.get(ticker)
    if df is None or len(df) < 20:
        return "HOLD"
    v061a48_close_prices = df['Close'].values.flatten()
    if len(v061a48_close_prices) < 20:
        return "HOLD"
    v061a48_ma_slow = np.convolve(v061a48_close_prices, np.ones(20)/20, mode='valid')
    v061a48_ma_fast = np.convolve(v061a48_close_prices, np.ones(11)/11, mode='valid')
    if len(v061a48_ma_slow) < 1 or len(v061a48_ma_fast) < 1:
        return "HOLD"
    v061a48_ma_slow_latest = v061a48_ma_slow[-1]
    v061a48_ma_fast_latest = v061a48_ma_fast[-1]
    v061a48_close_latest = v061a48_close_prices[-1]
    v061a48_std_dev = np.std(v061a48_close_prices[-20:])
    if v061a48_std_dev == 0:
        return "HOLD"
    v061a48_upper_band = v061a48_ma_slow_latest + 2 * v061a48_std_dev
    v061a48_lower_band = v061a48_ma_slow_latest - 2 * v061a48_std_dev
    if np.isnan(v061a48_upper_band) or np.isnan(v061a48_lower_band):
        return "HOLD"
    if v061a48_close_latest > v061a48_upper_band and v061a48_ma_fast_latest > v061a48_ma_slow_latest:
        return "SELL"
    if v061a48_close_latest < v061a48_lower_band and v061a48_ma_fast_latest < v061a48_ma_slow_latest:
        return "BUY"
    return "HOLD"