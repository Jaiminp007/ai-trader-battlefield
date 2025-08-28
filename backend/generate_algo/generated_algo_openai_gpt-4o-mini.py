import yfinance as yf
import numpy as np

_vca3b80_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _vca3b80_cache

    if ticker not in _vca3b80_cache:
        _vca3b80_cache[ticker] = yf.download(ticker, period="60d", interval="30m", progress=False)

    vca3b80_data = _vca3b80_cache.get(ticker)
    if vca3b80_data is None or len(vca3b80_data) < 30:
        return "HOLD"

    vca3b80_close_prices = vca3b80_data['Close'].values.flatten()
    if len(vca3b80_close_prices) == 0:
        return "HOLD"

    current_price = float(vca3b80_close_prices[-1])
    
    if len(vca3b80_close_prices) < 5:
        return "HOLD"

    vca3b80_average_price = np.mean(vca3b80_close_prices[-5:])
    if np.isnan(vca3b80_average_price):
        return "HOLD"

    if current_price < vca3b80_average_price * (1 - 0.03) and cash_balance >= current_price:
        return "BUY"
    elif current_price > vca3b80_average_price * (1 + 0.03) and shares_held > 0:
        return "SELL"

    return "HOLD"