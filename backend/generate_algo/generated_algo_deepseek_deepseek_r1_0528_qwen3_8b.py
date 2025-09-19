import yfinance as yf
import numpy as np

_vf1963a_cache = {}


def execute_trade(ticker, cash_balance, shares_held):
    global _vf1963a_cache
    if ticker not in _vf1963a_cache:
        _vf1963a_cache[ticker] = yf.download(ticker, period="60d", interval="30m", progress=False)
    
    df = _vf1963a_cache[ticker]
    if df is None or len(df) == 0:
        return "HOLD"
    
    close_prices = df['Close'].values.flatten()
    
    if len(close_prices) < 50:
        return "HOLD"
    
    if any(np.isnan(close_prices)):
        return "HOLD"
    
    req_window = max(11, 20, 21) + 5
    vf1963a_close_array = close_prices
    vf1963a_close_len = len(vf1963a_close_array)
    vf1963a_lookback = max(vf1963a_close_len, req_window)
    
    if vf1963a_close_len < req_window:
        return "HOLD"
    
    # Use only the last req_window data points
    vf1963a_price_data = vf1963a_close_array[-vf1963a_lookback:]
    
    # Simple Moving Averages
    vf1963a_fast_MA = np.nanmean(vf1963a_price_data[-11:])
    vf1963a_slow_MA = np.nanmean(vf1963a_price_data[-20:])
    
    # Bollinger Bands (18 days, 2 standard deviations)
    vf1963a_bb_window = 18
    vf1963a_bb_std = 2.0
    
    if vf1963a_close_len >= vf1963a_bb_window:
        vf1963a_midband = np.mean(vf1963a_price_data[-vf1963a_bb_window:])
        vf1963a_upperband = vf1963a_midband + (vf1963a_bb_std * np.std(vf1963a_price_data[-vf1963a_bb_window:]))
        vf1963a_lowerband = vf1963a_midband - (vf1963a_bb_std * np.std(vf1963a_price_data[-vf1963a_bb_window:]))
    
    # Calculate RSI (21-day)
    vf1963a_rsi_window = 21
    vf1963a_price_changes = np.diff(vf1963a_price_data[-vf1963a_rsi_window:])
    vf1963a_gains = np.maximum(vf1963a_price_changes, 0)
    vf1963a_losses = np.abs(np.minimum(vf1963a_price_changes, 0))
    
    if vf1963a_gains.max() == 0 or any(vf1963a_losses < 0.000001):
        # No or all gains are zero -> Avoid division by zero
        vf1963a_rsi = 50  # Neutral value
    else:
        vf1963a_rsi = 100 - (100 * np.mean(vf1963a_gains) / (np.mean(vf1963a_gains) + np.mean(vf1963a_losses)))
    
    # Multi-Factor Decision Matrix
    if np.isnan(vf1963a_fast_MA) or np.isnan(vf1963a_slow_MA) or np.isnan(vf1963a_rsi) or np.isnan(vf1963a_midband) or np.isnan(vf1963a_upperband) or np.isnan(vf1963a_lowerband):
        return "HOLD"
    
    # Condition 1: Trend Direction (based on Slow and Fast MA)
    trend_factor = vf1963a_fast_MA - vf1963a_slow_MA
    if trend_factor > 0.0:
        trend_rating = 1.0  # Bullish
    elif trend_factor <= 0.0:
        trend_rating = -1.0  # Bearish
    
    # Condition 2: Price-Band Position
    current_price = vf1963a_price_data[-1]
    if current_price < vf1963a_lowerband:
        band_factor = 1.0  # Oversold
    elif current_price > vf1963a_upperband:
        band_factor = -1.0  # Overbought
    else:
        band_factor = 0.0  # Neutral
    
    # Condition 3: RSI
    if vf1963a_rsi < 30:
        rsi_factor = -1.0  # Oversold
    elif vf1963a_rsi > 70:
        rsi_factor = 1.0  # Overbought
    else:
        rsi_factor = 0.0  # Neutral
    
    # Final Signal Equation (mean reversion)
    overall_sentiment = (trend_rating + band_factor + rsi_factor) / 3.0
    
    if overall_sentiment > 0.5 and band_factor == -1.0:
        return "BUY"
    elif overall_sentiment < 0.5 and band_factor == 1.0:
        return "SELL"
    else:
        return "HOLD"