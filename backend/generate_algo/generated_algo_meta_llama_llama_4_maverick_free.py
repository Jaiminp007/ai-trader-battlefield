import yfinance as yf
import numpy as np

_apple_strategy_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _apple_strategy_cache

    if ticker not in _apple_strategy_cache:
        _apple_strategy_cache[ticker] = yf.download(ticker, period="90d", interval="1h", progress=False)

    df = _apple_strategy_cache.get(ticker)
    if df is None or len(df) < 20:
        return "HOLD"

    close_prices = df['Close'].values.flatten()
    if len(close_prices) == 0:
        return "HOLD"

    current_price = float(close_prices[-1])

    short_window = 20
    long_window = 40
    if len(close_prices) < long_window:
        return "HOLD"

    short_ma = np.mean(close_prices[-short_window:])
    long_ma = np.mean(close_prices[-long_window:])

    if np.isnan(short_ma) or np.isnan(long_ma) or np.isnan(current_price):
        return "HOLD"

    rsi_window = 14
    if len(close_prices) >= rsi_window:
        delta = np.diff(close_prices[-rsi_window:])
        gain, loss = delta.copy(), delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        avg_gain = np.mean(gain)
        avg_loss = np.abs(np.mean(loss))
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    else:
        rsi = 50

    if rsi > 70 and short_ma < long_ma:
        return "SELL"
    elif rsi < 30 and short_ma > long_ma:
        return "BUY"
    else:
        return "HOLD"