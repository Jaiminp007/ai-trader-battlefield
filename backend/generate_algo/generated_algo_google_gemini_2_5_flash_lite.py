import yfinance as yf
import numpy as np

_v284bad_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _v284bad_cache
    if ticker not in _v284bad_cache:
        df = yf.download(ticker, period="90d", interval="1h", progress=False)
        if not df.empty:
            _v284bad_cache[ticker] = df
        else:
            return "HOLD"
    
    df = _v284bad_cache.get(ticker)
    
    v284bad_fast_ma = 7
    v284bad_slow_ma = 30
    v284bad_vol_lookback = 30

    if df is None or len(df) < max(v284bad_slow_ma, v284bad_vol_lookback):
        return "HOLD"

    close_prices = df['Close'].values.flatten()
    volumes = df['Volume'].values.flatten()

    if len(close_prices) < max(v284bad_slow_ma, v284bad_vol_lookback):
        return "HOLD"

    v284bad_fast_ma_vals = np.full(len(close_prices), np.nan)
    v284bad_slow_ma_vals = np.full(len(close_prices), np.nan)
    v284bad_vol_avg = np.full(len(close_prices), np.nan)

    for i in range(len(close_prices)):
        if i >= v284bad_fast_ma - 1:
            v284bad_fast_ma_vals[i] = np.mean(close_prices[i - v284bad_fast_ma + 1 : i + 1])
        if i >= v284bad_slow_ma - 1:
            v284bad_slow_ma_vals[i] = np.mean(close_prices[i - v284bad_slow_ma + 1 : i + 1])
        if i >= v284bad_vol_lookback - 1:
            v284bad_vol_avg[i] = np.mean(volumes[i - v284bad_vol_lookback + 1 : i + 1])

    if len(v284bad_fast_ma_vals) < v284bad_slow_ma or np.isnan(v284bad_fast_ma_vals[-1]) or np.isnan(v284bad_slow_ma_vals[-1]) or np.isnan(v284bad_vol_avg[-1]):
        return "HOLD"

    v284bad_last_close = close_prices[-1]
    v284bad_last_fast_ma = v284bad_fast_ma_vals[-1]
    v284bad_last_slow_ma = v284bad_slow_ma_vals[-1]
    v284bad_last_vol_avg = v284bad_vol_avg[-1]
    v284bad_last_volume = volumes[-1]

    if np.isnan(v284bad_last_close) or np.isnan(v284bad_last_fast_ma) or np.isnan(v284bad_last_slow_ma) or np.isnan(v284bad_last_vol_avg) or np.isnan(v284bad_last_volume):
        return "HOLD"
    
    v284bad_buy_signal = False
    v284bad_sell_signal = False

    # Dual Crossover Logic
    if v284bad_last_fast_ma > v284bad_last_slow_ma and v284bad_fast_ma_vals[-2] <= v284bad_slow_ma_vals[-2]:
        v284bad_buy_signal = True
    
    if v284bad_last_fast_ma < v284bad_last_slow_ma and v284bad_fast_ma_vals[-2] >= v284bad_slow_ma_vals[-2]:
        v284bad_sell_signal = True

    # Conservative Thresholding and Volume Confirmation
    v284bad_price_change_ratio = (v284bad_last_close - v284bad_last_slow_ma) / v284bad_last_slow_ma if v284bad_last_slow_ma else 0
    v284bad_volume_threshold = 1.2

    if v284bad_buy_signal:
        if v284bad_price_change_ratio > 0.01 and v284bad_last_volume > v284bad_last_vol_avg * v284bad_volume_threshold:
            return "BUY"
        else:
            return "HOLD"

    if v284bad_sell_signal:
        if v284bad_price_change_ratio < -0.01 and v284bad_last_volume > v284bad_last_vol_avg * v284bad_volume_threshold:
            return "SELL"
        else:
            return "HOLD"

    return "HOLD"