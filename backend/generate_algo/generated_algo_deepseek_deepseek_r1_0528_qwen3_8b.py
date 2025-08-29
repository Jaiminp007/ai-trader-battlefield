import yfinance as yf
import numpy as np

_unique_aapl_cache = {}

def execute_trade(ticker, cash_balance, shares_held):
    global _unique_aapl_cache

    if ticker not in _unique_aapl_cache:
        try:
            # Get 10 days of daily data for short-term analysis
            _unique_aapl_cache[ticker] = yf.download(ticker, period="10d", interval="1d", progress=False)
            # If download fails, set to empty
            if not _unique_aapl_cache[ticker].empty:
                # Explicitly drop NaN values that might remain in ticker data
                _unique_aapl_cache[ticker].dropna(subset=['Close'], inplace=True)
            else:
                # If data is empty, make sure we return without errors
                _unique_aapl_cache[ticker] = yf.download(ticker, period="5d", interval="1d", progress=False)
        except Exception as e:
            # Fallback if data retrieval fails
            return "HOLD"

    df = _unique_aapl_cache.get(ticker)
    if df is None or df.empty or 'Close' not in df.columns or df['Close'].isna().any():
        return "HOLD"

    close_prices = df['Close'].values.flatten()
    if len(close_prices) < 20:
        return "HOLD"

    # Safety check for non-NaN prices
    if np.isnan(float(close_prices[-1])):
        return "HOLD"

    # Calculate short-term moving average (7 days) with np.mean which is safe
    short_window = 7
    long_window = 20
    if len(close_prices) < short_window or len(close_prices) < long_window:
        return "HOLD"

    # Use np.nanmean to handle any rare edge cases
    short_ma = np.nanmean(close_prices[-short_window:])
    long_ma = np.nanmean(close_prices[-long_window:])

    # Calculate standard deviation for volatility-based secondary check
    vol_std = np.nanstd(close_prices[-long_window:])
    current_price = float(close_prices[-1])

    # Validate calculations
    if np.isnan(short_ma) or np.isnan(long_ma) or np.isnan(vol_std) or np.isnan(current_price):
        return "HOLD"

    # Prevent division by zero in probability calculation
    if vol_std == 0:
        vol_std = 0.01  # Small noise substitution

    # Primary crossover strategy
    if short_ma > long_ma:
        # Calculate probability-based confirmation factor
        momentum_strength = (short_ma / long_ma)
        if momentum_strength > 1.005:
            return "BUY"

    # Intra-day volatility-based trade signals (3% threshold)
    if close_prices[-1] / close_prices[-2] > 1.003 and vol_std / current_price > 0.01:
        return "BUY"

    if short_ma < long_ma and short_ma / long_ma < 0.995:
        return "SELL"

    # Risk-adjusted Cauchy criterion with outlier handling
    try:
        # Use a small set for standard deviation calculation to avoid overfitting
        recent_o
    except Exception:
        return "HOLD"

    return "HOLD"