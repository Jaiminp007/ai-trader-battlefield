import yfinance as yf
import numpy as np

_va8d48d_cache = {}

def execute_trade(ticker, cash_balance, shares_held):
    global _va8d48d_cache
    if ticker not in _va8d48d_cache:
        _va8d48d_cache[ticker] = yf.download(ticker, period="45d", interval="30m", progress=False)
    df = _va8d48d_cache.get(ticker)
    if df is None or len(df) < 50:
        return "HOLD"
    close_prices = df['Close'].values.flatten()
    if len(close_prices) < 50:
        return "HOLD"
    va8d48d_prices = close_prices[-50:]
    if np.isnan(va8d48d_prices).any():
        return "HOLD"
    va8d48d_fast_ma = np.mean(va8d48d_prices[-9:])
    va8d48d_slow_ma = np.mean(va8d48d_prices[-45:])
    if np.isnan(va8d48d_fast_ma) or np.isnan(va8d48d_slow_ma):
        return "HOLD"
    va8d48d_returns = np.diff(va8d48d_prices) / va8d48d_prices[:-1]
    if len(va8d48d_returns) < 30:
        return "HOLD"
    va8d48d_vol = np.std(va8d48d_returns[-30:])
    if va8d48d_vol <= 0 or np.isnan(va8d48d_vol):
        return "HOLD"
    va8d48d_delta = va8d48d_prices[-1] - va8d48d_prices[-2]
    va8d48d_vol_ratio = abs(va8d48d_delta) / va8d48d_vol
    va8d48d_ma_ratio = (va8d48d_fast_ma - va8d48d_slow_ma) / va8d48d_slow_ma
    va8d48d_rsi_prices = va8d48d_prices[-22:]
    if len(va8d48d_rsi_prices) < 21:
        return "HOLD"
    va8d48d_gains = np.maximum(0, np.diff(va8d48d_rsi_prices))
    va8d48d_losses = np.maximum(0, -np.diff(va8d48d_rsi_prices))
    if len(va8d48d_gains) < 21 or len(va8d48d_losses) < 21:
        return "HOLD"
    va8d48d_avg_gain = np.mean(va8d48d_gains[-21:])
    va8d48d_avg_loss = np.mean(va8d48d_losses[-21:])
    if va8d48d_avg_loss <= 0:
        va8d48d_rsi = 100
    else:
        va8d48d_rs = va8d48d_avg_gain / va8d48d_avg_loss
        va8d48d_rsi = 100 - (100 / (1 + va8d48d_rs))
    if np.isnan(va8d48d_rsi):
        return "HOLD"
    va8d48d_bb_mid = np.mean(va8d48d_prices[-12:])
    va8d48d_bb_std = np.std(va8d48d_prices[-12:])
    if va8d48d_bb_std <= 0:
        return "HOLD"
    va8d48d_bb_upper = va8d48d_bb_mid + 2 * va8d48d_bb_std
    va8d48d_bb_lower = va8d48d_bb_mid - 2 * va8d48d_bb_std
    va8d48d_bb_position = (va8d48d_prices[-1] - va8d48d_bb_lower) / (va8d48d_bb_upper - va8d48d_bb_lower)
    if np.isnan(va8d48d_bb_position):
        return "HOLD"
    va8d48d_vol_threshold = 1.5 * va8d48d_vol
    va8d48d_signal = 0
    if va8d48d_vol_ratio > va8d48d_vol_threshold:
        if va8d48d_delta > 0:
            va8d48d_signal += 1
        else:
            va8d48d_signal -= 1
    if va8d48d_ma_ratio > 0.01:
        va8d48d_signal += 1
    elif va8d48d_ma_ratio < -0.01:
        va8d48d_signal -= 1
    if va8d48d_rsi > 70:
        va8d48d_signal -= 1
    elif va8d48d_rsi < 30:
        va8d48d_signal += 1
    if va8d48d_bb_position > 0.8:
        va8d48d_signal -= 1
    elif va8d48d_bb_position < 0.2:
        va8d48d_signal += 1
    if va8d48d_signal > 1 and cash_balance > va8d48d_prices[-1]:
        return "BUY"
    elif va8d48d_signal < -1 and shares_held > 0:
        return "SELL"
    else:
        return "HOLD"