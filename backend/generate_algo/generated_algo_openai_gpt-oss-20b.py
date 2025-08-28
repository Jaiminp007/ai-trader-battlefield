import yfinance as yf
import numpy as np

_vaa1ee6_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _vaa1ee6_cache
    if ticker not in _vaa1ee6_cache:
        _vaa1ee6_cache[ticker] = yf.download(ticker, period="30d", interval="15m", progress=False)
    vaa1ee6_df = _vaa1ee6_cache.get(ticker)
    if vaa1ee6_df is None or len(vaa1ee6_df) < 25:
        return "HOLD"
    vaa1ee6_close_prices = vaa1ee6_df['Close'].values.flatten()
    if len(vaa1ee6_close_prices) == 0 or np.any(np.isnan(vaa1ee6_close_prices)):
        return "HOLD"
    if len(vaa1ee6_close_prices) < 20:
        return "HOLD"
    vaa1ee6_sma_window = 20
    vaa1ee6_sma = np.mean(vaa1ee6_close_prices[-vaa1ee6_sma_window:])
    if np.isnan(vaa1ee6_sma):
        return "HOLD"
    vaa1ee6_current_price = float(vaa1ee6_close_prices[-1])
    vaa1ee6_prev_price = float(vaa1ee6_close_prices[-2]) if len(vaa1ee6_close_prices) >= 2 else vaa1ee6_current_price
    vaa1ee6_threshold = 0.025
    vaa1ee6_diff = vaa1ee6_current_price - vaa1ee6_sma
    if vaa1ee6_diff >= vaa1ee6_threshold and vaa1ee6_prev_price <= vaa1ee6_sma:
        if cash_balance > 0:
            return "BUY"
    elif vaa1ee6_diff <= -vaa1ee6_threshold and vaa1ee6_prev_price >= vaa1ee6_sma:
        if shares_held > 0:
            return "SELL"
    return "HOLD"