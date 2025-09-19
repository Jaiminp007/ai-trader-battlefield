import yfinance as yf
import numpy as np

_v412618_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    if ticker not in _v412618_cache:
        _v412618_cache[ticker] = yf.download(ticker, period="90d", interval="1h", progress=False)
    df = _v412618_cache.get(ticker)
    if df is None or len(df) < 50:
        return "HOLD"
    v412618_close_prices = df['Close'].values.flatten()
    if len(v412618_close_prices) < 50:
        return "HOLD"
    v412618_volume = df['Volume'].values.flatten()
    if len(v412618_volume) < 50:
        return "HOLD"
    v412618_current_price = v412618_close_prices[-1]
    v412618_current_volume = v412618_volume[-1]
    if np.isnan(v412618_current_price) or np.isnan(v412618_current_volume):
        return "HOLD"
    v412618_slow_ma = np.full(len(v412618_close_prices), np.nan)
    v412618_fast_ma = np.full(len(v412618_close_prices), np.nan)
    if len(v412618_close_prices) >= 20:
        v412618_slow_ma[19:] = np.convolve(v412618_close_prices, np.ones(20)/20, mode='valid')
    if len(v412618_close_prices) >= 7:
        v412618_fast_ma[6:] = np.convolve(v412618_close_prices, np.ones(7)/7, mode='valid')
    v412618_slow_ma_current = v412618_slow_ma[-1]
    v412618_fast_ma_current = v412618_fast_ma[-1]
    if np.isnan(v412618_slow_ma_current) or np.isnan(v412618_fast_ma_current):
        return "HOLD"
    v412618_price_deviation = (v412618_current_price - v412618_slow_ma_current) / v412618_slow_ma_current
    v412618_avg_volume = np.mean(v412618_volume[-30:]) if len(v412618_volume) >= 30 else np.mean(v412618_volume)
    if v412618_avg_volume <= 0:
        return "HOLD"
    v412618_volume_ratio = v412618_current_volume / v412618_avg_volume
    v412618_volume_confirm = v412618_volume_ratio > 1.2
    v412618_contrarian_signal = 0.0
    if v412618_price_deviation < -0.03 and v412618_fast_ma_current < v412618_slow_ma_current:
        v412618_contrarian_signal += 0.4
    elif v412618_price_deviation > 0.03 and v412618_fast_ma_current > v412618_slow_ma_current:
        v412618_contrarian_signal -= 0.4
    if v412618_price_deviation < -0.02:
        v412618_contrarian_signal += 0.2
    elif v412618_price_deviation > 0.02:
        v412618_contrarian_signal -= 0.2
    if np.isnan(v412618_contrarian_signal):
        return "HOLD"
    v412618_buy_prob = max(0, min(1, (v412618_contrarian_signal + 0.5) / 0.6))
    v412618_sell_prob = max(0, min(1, (-v412618_contrarian_signal + 0.5) / 0.6))
    if v412618_volume_confirm:
        v412618_buy_prob *= 1.3
        v412618_sell_prob *= 1.3
    v412618_buy_prob = min(1, v412618_buy_prob)
    v412618_sell_prob = min(1, v412618_sell_prob)
    if shares_held == 0 and cash_balance > 0 and v412618_buy_prob > 0.4:
        return "BUY"
    elif shares_held > 0 and v412618_sell_prob > 0.4:
        return "SELL"
    else:
        return "HOLD"