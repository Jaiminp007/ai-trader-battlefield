import yfinance as yf
import numpy as np

_momentum_oscillator_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _momentum_oscillator_cache

    # MEDIUM-TERM: 30 days, 15-minute interval
    # This interval and period often reveals clearer short-to-medium term trends
    # which is suitable for a momentum strategy looking for sustained price action.
    if ticker not in _momentum_oscillator_cache:
        _momentum_oscillator_cache[ticker] = yf.download(ticker, period="30d", interval="15m", progress=False)

    df_market_data = _momentum_oscillator_cache.get(ticker)
    
    # Validate data existence and length
    required_data_points = 50  # Needed for SMA, Std Dev, and enough historical context
    if df_market_data is None or len(df_market_data) < required_data_points:
        return "HOLD"

    # Extract Close prices with .flatten() and validate
    close_prices_array = df_market_data['Close'].values.flatten()
    if len(close_prices_array) < required_data_points:
        return "HOLD"
    
    current_market_price = float(close_prices_array[-1])
    if np.isnan(current_market_price):
        return "HOLD"

    # Strategy Type: MOMENTUM
    # Indicator Combination: CUSTOM METRIC (Momentum Oscillator based on price change percent vs volatility)
    # This custom momentum oscillator combines price change with current volatility.
    # It attempts to identify strong directional moves that are validated by lower than average noise.

    # Calculate short-term and long-term moving averages for baseline momentum
    short_ma_period = 10
    long_ma_period = 30

    if len(close_prices_array) < long_ma_period:
        return "HOLD"

    short_window_prices = close_prices_array[-short_ma_period:]
    long_window_prices = close_prices_array[-long_ma_period:]

    momentum_osc_short_ma = np.mean(short_window_prices)
    momentum_osc_long_ma = np.mean(long_window_prices)

    if np.isnan(momentum_osc_short_ma) or np.isnan(momentum_osc_long_ma):
        return "HOLD"

    # Momentum Factor: Price Change %
    price_change_percent = (current_market_price - close_prices_array[-2]) / close_prices_array[-2] if close_prices_array[-2] != 0 else 0
    if np.isnan(price_change_percent):
        return "HOLD"

    # Volatility Factor: Simple Moving Standard Deviation (SMSTD)
    volatility_window = 20
    if len(close_prices_array) < volatility_window:
        return "HOLD"
    
    volatility_values = np.std(close_prices_array[-volatility_window:])
    if np.isnan(volatility_values) or volatility_values == 0: # Handle division by zero
        return "HOLD"

    # Custom Momentum Oscillator: Price change relative to volatility and MA crossover strength
    # A positive oscillator value with strong MA crossover indicates buy signal.
    # A negative oscillator value with weak MA crossover indicates sell signal.
    ma_crossover_strength = (momentum_osc_short_ma - momentum_osc_long_ma) / momentum_osc_long_ma if momentum_osc_long_ma != 0 else 0
    
    # Scale price change by inverse volatility: higher price change in lower volatility is stronger signal
    # Add MA crossover strength to this.
    try:
        if volatility_values < 0.01: # Avoid excessively high scaled price change if volatility is near zero
            scaled_price_change = price_change_percent * 10 
        else:
            scaled_price_change = price_change_percent / volatility_values
    except ZeroDivisionError:
        return "HOLD" # Should be caught by volatility check, but as a safeguard
    
    custom_momentum_oscillator_value = scaled_price_change + ma_crossover_strength
    if np.isnan(custom_momentum_oscillator_value):
        return "HOLD"
    
    # Threshold Values: AGGRESSIVE (0.001-0.005)
    # The thresholds are applied to the custom momentum oscillator.
    # We choose something in the middle of aggressive range (0.003)
    buy_aggressive_threshold = 0.004
    sell_aggressive_threshold = -0.003
    
    # Portfolio Management: AGGRESSIVE
    # Trading Logic: CONDITIONAL
    # Only trade when multiple conditions align: price is above/below MAs significantly AND momentum oscillator strong
    
    # Condition 1: Short MA above Long MA for BUY, or below for SELL
    ma_crossover_buy = momentum_osc_short_ma > momentum_osc_long_ma
    ma_crossover_sell = momentum_osc_short_ma < momentum_osc_long_ma

    # Condition 2: Current price relative to short MA (momentum confirmation)
    price_above_short_ma = current_market_price > momentum_osc_short_ma * (1 + 0.001)
    price_below_short_ma = current_market_price < momentum_osc_short_ma * (1 - 0.001)

    # Decision Logic
    if custom_momentum_oscillator_value > buy_aggressive_threshold and ma_crossover_buy and price_above_short_ma:
        # Aggressive BUY: Check if we have enough cash to buy at least one share
        if cash_balance >= current_market_price * 1.001: # Add small buffer for slippage often
            return "BUY"
    elif custom_momentum_oscillator_value < sell_aggressive_threshold and ma_crossover_sell and price_below_short_ma:
        # Aggressive SELL: Check if we hold any shares
        if shares_held > 0:
            return "SELL"

    return "HOLD"