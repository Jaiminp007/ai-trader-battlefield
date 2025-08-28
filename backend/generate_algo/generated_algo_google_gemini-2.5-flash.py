import yfinance as yf
import numpy as np

_v3e4fba_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _v3e4fba_cache

    if ticker not in _v3e4fba_cache:
        _v3e4fba_cache[ticker] = yf.download(ticker, period="5d", interval="1m", progress=False)

    v3e4fba_df_data = _v3e4fba_cache.get(ticker)
    if v3e4fba_df_data is None or v3e4fba_df_data.empty or len(v3e4fba_df_data) < 20:
        return "HOLD"

    v3e4fba_close_prices = v3e4fba_df_data['Close'].values.flatten()
    if len(v3e4fba_close_prices) == 0:
        return "HOLD"
    
    v3e4fba_current_price = float(v3e4fba_close_prices[-1])

    v3e4fba_short_window = 5
    v3e4fba_long_window = 15

    if len(v3e4fba_close_prices) < v3e4fba_long_window:
        return "HOLD"

    v3e4fba_short_ma_values = v3e4fba_close_prices[-v3e4fba_short_window:]
    v3e4fba_long_ma_values = v3e4fba_close_prices[-v3e4fba_long_window:]
    
    if np.any(np.isnan(v3e4fba_short_ma_values)) or np.any(np.isnan(v3e4fba_long_ma_values)):
        return "HOLD"

    v3e4fba_short_ma = np.mean(v3e4fba_short_ma_values)
    v3e4fba_long_ma = np.mean(v3e4fba_long_ma_values)

    if np.isnan(v3e4fba_short_ma) or np.isnan(v3e4fba_long_ma) or np.isnan(v3e4fba_current_price):
        return "HOLD"

    # Conservative threshold
    v3e