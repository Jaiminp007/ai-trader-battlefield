
import yfinance as yf
import numpy as np

vf1963a_cache = {}

def execute_trade(ticker, cash_balance, shares_held):
    global vf1963a_cache
    
    if ticker not in vf1963a_cache:
        try:
            data = yf.download(ticker, period="60d", interval="30m", progress=False)
            vf1963a_cache[ticker] = data
        except:
            return "HOLD"
    
    df = vf1963a_cache[ticker]
    if df is None or 'Close' not in df.columns:
        return "HOLD"
    
    close_prices = np.array(df['Close']).flatten()
    if len(close_prices) < 20:
        return "HOLD"
    
    current_price = float(close_prices[-1])

    short_window = 30
    long_window = 45

    if len(close_prices) < long_window:
        return "HOLD"

    # Calculate short and long term moving averages
    short_ma = np.mean(close_prices[-short_window:])
    long_ma = np.mean(close_prices[-long_window:])
    
    if np.isnan(short_ma) or np.isnan(long_ma) or np.isnan(current_price):
        return "HOLD"
    
    # Calculate adjusted basline
    vf1963a_ma_diff = (long_ma + short_ma) / 2

    # Calculate true range for vol-weighted entries
    vf1963a_true_range = []
    for i in range(1, len(close_prices)):
        vf1963a_true_range.append(abs(close_prices[i] - close_prices[i-1]))
    vf1963a_true_range = np.array(vf1963a_true_range)
    
    if len(vf1963a_true_range) > 0 and np.sum(vf1963a_true_range) > 0:
        vf1963a_vol_factor = np.median(vf1963a_true_range)
    else:
        return "HOLD"
    
    # Calculate deviation from baseline
    vf1963a_deviation = (current_price - vf1963a_ma_diff) / vf1963a_vol_factor
    
    # Calculate momentum factor
    vf1963a_price_roc = (close_prices[-1] - close_prices[-2]) / close_prices[-2] if len(close_prices) > 1 else 0
    vf1963a_roc_ma = np.mean([close_prices[-1] - close_prices[-2], 
                             close_prices[-2] - close_prices[-3],
                             close_prices[-3] - close_prices[-4]])
    
    # Define portfolio leverage based on cash and shares
    vf1963a_cash_ratio = 1.0
    if cash_balance > 0 and shares_held > 0:
        vf1963a_cash_ratio = min(1.0, cash_balance / (current_price * shares_held))
    
    # Trading logic based on multi-factor analysis
    if vf1963a_deviation < -0.7 and vf1963a_price_roc > vf1963a_roc_ma * 1.5:
        return "BUY"
    elif vf1963a_deviation > 0.7 and vf1963a_price_roc < vf1963a_roc_ma * 0.6:
        return "SELL"
    elif abs(vf1963a_deviation) < 0.3 and abs(vf1963a_price_roc) < 0.01 and vf1963a_cash_ratio > 0.2:
        return "BUY"  # Aggressive accumulation
    elif abs(vf1963a_deviation) > 1.2 and vf1963a_cash_ratio < 0.8:
        return "SELL"  # Aggressive reduction
    else:
        return "HOLD"
