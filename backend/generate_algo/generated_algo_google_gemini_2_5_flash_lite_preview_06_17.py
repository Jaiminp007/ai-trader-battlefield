import yfinance as yf
import numpy as np

_v61fce9_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _v61fce9_cache
    
    v61fce9_period = "30d"
    v61fce9_interval = "15m"
    v61fce9_fast_ma = 5
    v61fce9_slow_ma = 45
    v61fce9_vol_lookback = 30

    if ticker not in _v61fce9_cache:
        df = yf.download(ticker, period=v61fce9_period, interval=v61fce9_interval, progress=False)
        if df is None or df.empty:
            return "HOLD"
        _v61fce9_cache[ticker] = df
    else:
        df = _v61fce9_cache[ticker]
        
    if df is None or len(df) < max(v61fce9_slow_ma, v61fce9_vol_lookback):
        return "HOLD"

    close_prices = df['Close'].values.flatten()
    volumes = df['Volume'].values.flatten()

    if len(close_prices) < max(v61fce9_slow_ma, v61fce9_vol_lookback):
        return "HOLD"

    v61fce9_sma_fast = np.convolve(close_prices, np.ones(v61fce9_fast_ma)/v61fce9_fast_ma, mode='valid')
    v61fce9_sma_slow = np.convolve(close_prices, np.ones(v61fce9_slow_ma)/v61fce9_slow_ma, mode='valid')

    if len(v61fce9_sma_fast) == 0 or len(v61fce9_sma_slow) == 0:
        return "HOLD"

    v61fce9_price_change = np.diff(close_prices)
    if len(v61fce9_price_change) == 0:
        return "HOLD"
        
    v61fce9_avg_vol = np.mean(volumes[-v61fce9_vol_lookback:])
    if v61fce9_avg_vol <= 0 or np.isnan(v61fce9_avg_vol):
        return "HOLD"

    v61fce9_trend_strength = (v61fce9_sma_fast[-1] - v61fce9_sma_slow[-1]) / v61fce9_sma_slow[-1] if v61fce9_sma_slow[-1] != 0 else 0
    v61fce9_recent_volatility = np.std(v61fce9_price_change[-v61fce9_vol_lookback:])
    if np.isnan(v61fce9_recent_volatility) or v61fce9_recent_volatility <= 0:
        v61fce9_recent_volatility = 1 # avoid division by zero or NaN
        
    v61fce9_price_deviation_from_slow_ma = (close_prices[-1] - v61fce9_sma_slow[-1]) / v61fce9_sma_slow[-1] if v61fce9_sma_slow[-1] !=0 else 0
    v61fce9_relative_volume = volumes[-1] / v61fce9_avg_vol if v61fce9_avg_vol > 0 else 1

    v61fce9_buy_signal = False
    v61fce9_sell_signal = False

    if v61fce9_trend_strength > 0.005 and v61fce9_price_deviation_from_slow_ma < -0.02 and v61fce9_relative_volume > 1.2:
        v61fce9_buy_signal = True

    if v61fce9_trend_strength < -0.005 and v61fce9_price_deviation_from_slow_ma > 0.02 and v61fce9_relative_volume > 1.2:
        v61fce9_sell_signal = True

    if v61fce9_buy_signal and not v61fce9_sell_signal:
        return "BUY"
    elif v61fce9_sell_signal and not v61fce9_buy_signal:
        return "SELL"
    else:
        return "HOLD"