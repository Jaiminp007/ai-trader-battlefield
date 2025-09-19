import yfinance as yf
import numpy as np

_v3db4d6_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _v3db4d6_cache
    if ticker not in _v3db4d6_cache:
        _v3db4d6_cache[ticker] = yf.download(ticker,
                                            period="45d",
                                            interval="30m",
                                            progress=False)
    df = _v3db4d6_cache.get(ticker)
    if df is None or df.empty:
        return "HOLD"
    close_prices = df['Close'].values.flatten()
    vol_prices = df['Volume'].values.flatten()
    needed_window = 45
    if len(close_prices) < needed_window or len(vol_prices) < needed_window:
        return "HOLD"

    # Calculate indicators
    # Fast MA
    if len(close_prices) < 7:
        return "HOLD"
    v3db4d6_fast_ma = np.mean(close_prices[-7:])
    # Slow MA
    if len(close_prices) < 30:
        return "HOLD"
    v3db4d6_slow_ma = np.mean(close_prices[-30:])
    # Bollinger Bands
    if len(close_prices) < 18:
        return "HOLD"
    bb_mean = np.mean(close_prices[-18:])
    bb_std = np.std(close_prices[-18:])
    if np.isnan(bb_std) or bb_std <= 0:
        return "HOLD"
    v3db4d6_upper_band = bb_mean + 2 * bb_std
    v3db4d6_lower_band = bb_mean - 2 * bb_std
    # Volume confirm
    if len(vol_prices) < 45:
        return "HOLD"
    v3db4d6_avg_vol = np.mean(vol_prices[-45:])
    if v3db4d6_avg_vol <= 0:
        return "HOLD"
    v3db4d6_curr_vol = vol_prices[-1]
    if np.isnan(v3db4d6_curr_vol) or np.isnan(v3db4d6_avg_vol):
        return "HOLD"
    v3db4d6_vol_ratio = v3db4d6_curr_vol / v3db4d6_avg_vol
    if np.isnan(v3db4d6_vol_ratio):
        return "HOLD"

    # Probabilistic scoring
    v3db4d6_score = 0
    if v3db4d6_fast_ma > v3db4d6_slow_ma:
        v3db4d6_score += 1
    else:
        v3db4d6_score -= 1
    if close_prices[-1] > v3db4d6_upper_band:
        v3db4d6_score += 1
    elif close_prices[-1] < v3db4d6_lower_band:
        v3db4d6_score -= 1
    if v3db4d6_vol_ratio > 1.5:
        v3db4d6_score += 1
    else:
        if close_prices[-1] < v3db4d6_slow_ma:
            v3db4d6_score -= 1

    if v3db4d6_score >= 2:
        return "BUY"
    if v3db4d6_score <= -2:
        return "SELL"
    return "HOLD"