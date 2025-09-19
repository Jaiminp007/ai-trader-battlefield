import yfinance as yf
import numpy as np

_v974ed7_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _v974ed7_cache
    if ticker not in _v974ed7_cache:
        _v974ed7_cache[ticker] = yf.download(ticker, period="30d", interval="15m", progress=False)
    df = _v974ed7_cache.get(ticker)
    if df is None or len(df) < 50:
        return "HOLD"
    v974ed7_close_prices = df['Close'].values.flatten()
    v974ed7_n = len(v974ed7_close_prices)
    if v974ed7_n < 50:
        return "HOLD"
    v974ed7_current = v974ed7_close_prices[-1]
    if np.isnan(v974ed7_current):
        return "HOLD"
    v974ed7_bb_window = 12
    if v974ed7_n < v974ed7_bb_window:
        return "HOLD"
    v974ed7_sma_recent = np.mean(v974ed7_close_prices[-v974ed7_bb_window:])
    v974ed7_std_recent = np.std(v974ed7_close_prices[-v974ed7_bb_window:])
    if np.isnan(v974ed7_std_recent) or v974ed7_std_recent <= 0:
        return "HOLD"
    v974ed7_vol_lookback = 15
    if v974ed7_n < v974ed7_vol_lookback:
        return "HOLD"
    v974ed7_recent_vol_data = v974ed7_close_prices[-v974ed7_vol_lookback:]
    v974ed7_vol = np.std(v974ed7_recent_vol_data) / np.mean(v974ed7_recent_vol_data)
    if np.isnan(v974ed7_vol):
        return "HOLD"
    if v974ed7_vol > 0.03:
        v974ed7_adapt_mult = 2.5
    elif v974ed7_vol < 0.01:
        v974ed7_adapt_mult = 1.8
    else:
        v974ed7_adapt_mult = 2.2
    v974ed7_z = (v974ed7_current - v974ed7_sma_recent) / v974ed7_std_recent
    if np.isnan(v974ed7_z):
        return "HOLD"
    if v974ed7_z < -v974ed7_adapt_mult:
        v974ed7_signal = "BUY"
    elif v974ed7_z > v974ed7_adapt_mult:
        v974ed7_signal = "SELL"
    else:
        v974ed7_signal = "HOLD"
    if v974ed7_signal == "BUY" and shares_held == 0 and cash_balance > 0:
        return "BUY"
    elif v974ed7_signal == "SELL" and shares_held > 0:
        return "SELL"
    else:
        return "HOLD"