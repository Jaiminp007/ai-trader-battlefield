import yfinance as yf
import numpy as np

_v3e4fba_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _v3e4fba_cache

    v3e4fba_FAST_MA = 11
    v3e4fba_SLOW_MA = 45
    v3e4fba_RSI_WINDOW = 7
    v3e4fba_BB_WINDOW = 20
    v3e4fba_VOL_LOOKBACK = 30
    v3e4fba_USE_RSI = True
    v3e4fba_USE_BBANDS = True
    v3e4fba_USE_VOLUME_CONFIRM = True

    v3e4fba_min_data_points = max(v3e4fba_SLOW_MA, v3e4fba_BB_WINDOW, v3e4fba_VOL_LOOKBACK, v3e4fba_RSI_WINDOW) + 1 # +1 for diff/period

    if ticker not in _v3e4fba_cache:
        # SHORT-TERM using yf.download(..., period="5d", interval="1m")
        _v3e4fba_cache[ticker] = yf.download(ticker, period="5d", interval="1m", progress=False)
    
    v3e4fba_df = _v3e4fba_cache.get(ticker)

    if v3e4fba_df is None or v3e4fba_df.empty:
        return "HOLD"
    
    v3e4fba_close_prices = v3e4fba_df['Close'].values.flatten()
    v3e4fba_volumes = v3e4fba_df['Volume'].values.flatten()
    
    if len(v3e4fba_close_prices) < v3e4fba_min_data_points:
        return "HOLD"

    # Calculate SMAs
    v3e4fba_sma_fast = np.nanmean(v3e4fba_close_prices[-v3e4fba_FAST_MA:])
    v3e4fba_sma_slow = np.nanmean(v3e4fba_close_prices[-v3e4fba_SLOW_MA:])

    if np.isnan(v3e4fba_sma_fast) or np.isnan(v3e4fba_sma_slow):
        return "HOLD"

    v3e4fba_current_price = v3e4fba_close_prices[-1]

    # Momentum/Trend: Dual Crossover
    # Conservative threshold: waiting for a clear crossover and enough room
    v3e4fba_crossover_buy_signal = (v3e4fba_sma_fast > v3e4fba_sma_slow * 1.005) # Fast MA is 0.5% above Slow MA
    v3e4fba_crossover_sell_signal = (v3e4fba_sma_fast < v3e4fba_sma_slow * 0.995) # Fast MA is 0.5% below Slow MA

    # RSI
    v3e4fba_rsi_signal = 0 # 0 for neutral, 1 for buy, -1 for sell
    if v3e4fba_USE_RSI:
        if len(v3e4fba_close_prices) >= v3e4fba_RSI_WINDOW + 1:
            v3e4fba_deltas = np.diff(v3e4fba_close_prices[-v3e4fba_RSI_WINDOW-1:])
            v3e4fba_gains = v3e4fba_deltas[v3e4fba_deltas > 0]
            v3e4fba_losses = -v3e4fba_deltas[v3e4fba_deltas < 0]

            v3e4fba_avg_gain = np.nanmean(v3e4fba_gains) if len(v3e4fba_gains) > 0 else 0
            v3e4fba_avg_loss = np.nanmean(v3e4fba_losses) if len(v3e4fba_losses) > 0 else 0

            if v3e4fba_avg_loss == 0:
                v3e4fba_rs = 100 if v3e4fba_avg_gain > 0 else 0
            else:
                v3e4fba_rs = v3e4fba_avg_gain / v3e4fba_avg_loss
            
            v3e4fba_rsi = 100 - (100 / (1 + v3e4fba_rs)) if not np.isnan(v3e4fba_rs) else np.nan

            if np.isnan(v3e4fba_rsi):
                return "HOLD"

            if v3e4fba_rsi < 30 : # Conservative Overbought/Oversold thresholds
                v3e4fba_rsi_signal = 1
            elif v3e4fba_rsi > 70:
                v3e4fba_rsi_signal = -1
        else:
            return "HOLD"

    # Bollinger Bands (Volatility)
    v3e4fba_bb_signal = 0 # 0 for neutral, 1 for buy, -1 for sell
    if v3e4fba_USE_BBANDS:
        if len(v3e4fba_close_prices) >= v3e4fba_BB_WINDOW:
            v3e4fba_rolling_std = np.std(v3e4fba_close_prices[-v3e4fba_BB_WINDOW:])
            v3e4fba_middle_band = np.nanmean(v3e4fba_close_prices[-v3e4fba_BB_WINDOW:])

            if np.isnan(v3e4fba_rolling_std) or np.isnan(v3e4fba_middle_band) or v3e4fba_rolling_std == 0:
                return "HOLD"

            v3e4fba_upper_band = v3e4fba_middle_band + (2 * v3e4fba_rolling_std)
            v3e4fba_lower_band = v3e4fba_middle_band - (2 * v3e4fba_rolling_std)

            # Conservative: Price touching or crossing bands aggressively
            if v3e4fba_current_price < v3e4fba_lower_band * 0.99: # 1% below lower band
                v3e4fba_bb_signal = 1
            elif v3e4fba_current_price > v3e4fba_upper_band * 1.01: # 1% above upper band
                v3e4fba_bb_signal = -1
        else:
            return "HOLD"

    # Volume Confirmation
    v3e4fba_volume_confirm_signal = 0 # 0 for neutral, 1 for positive, -1 for negative
    if v3e4fba_USE_VOLUME_CONFIRM:
        if len(v3e4fba_volumes) >= v3e4fba_VOL_LOOKBACK:
            v3e4fba_avg_volume = np.nanmean(v3e4fba_volumes[-v3e4fba_VOL_LOOKBACK:-1]) # Exclude current volume
            v3e4fba_current_volume = v3e4fba_volumes[-1]

            if np.isnan(v3e4fba_avg_volume) or v3e4fba_avg_volume <= 0:
                return "HOLD"

            if v3e4fba_current_volume > v3e4fba_avg_volume * 1.5: # 50% higher than average
                v3e4fba_volume_confirm_signal = 1
            elif v3e4fba_current_volume < v3e4fba_avg_volume * 0.5: # 50% lower than average
                v3e4fba_volume_confirm_signal = -1
        else:
            return "HOLD"


    # Decision Logic (Conservative)
    v3e4fba_buy_score = 0
    v3e4fba_sell_score = 0

    if v3e4fba_crossover_buy_signal:
        v3e4fba_buy_score += 1
    if v3e4fba_crossover_sell_signal:
        v3e4fba_sell_score += 1

    if v3e4fba_USE_RSI:
        if v3e4fba_rsi_signal == 1:
            v3e4fba_buy_score += 1
        elif v3e4fba_rsi_signal == -1:
            v3e4fba_sell_score += 1
    
    if v3e4fba_USE_BBANDS:
        if v3e4fba_bb_signal == 1:
            v3e4fba_buy_score += 1
        elif v3e4fba_bb_signal == -1:
            v3e4fba_sell_score += 1

    # Volume filter: only confirm strong signals with high volume
    if v3e4fba_USE_VOLUME_CONFIRM:
        if v3e4fba_buy_score > 0 and v3e4fba_volume_confirm_signal != 1:
            v3e4fba_buy_score = 0  # Reduce buy score if volume is not confirming
        if v3e4fba_sell_score > 0 and v3e4fba_volume_confirm_signal != -1:
            v3e4fba_sell_score = 0 # Reduce sell score if volume is not confirming

    if v3e4fba_buy_score >= 2 and cash_balance > v3e4fba_current_price * 1: # Requires at least 2 strong signals and enough cash
        return "BUY"
    elif v3e4fba_sell_score >= 2 and shares_held > 0: # Requires at least 2 strong signals and shares to sell
        return "SELL"
    else:
        return "HOLD"