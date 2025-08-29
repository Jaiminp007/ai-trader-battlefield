analysisWe need to produce a Python function execute_trade with specified constraints and uniqueness.

- Strategy type: choose one, e.g., Technical Indicators: use RSI? Or something unique.

- Data period: choose one, e.g., MEDIUM-TERM: 15-30 days. We'll use period="30d", interval="15m" maybe.

But must set period/interval consistent with chosen data period. Example options: 5d/1m, 30d/15m, 60d/30m, 90d/1h. For medium-term 15-30 days, 30d/15m fits. So period="30d", interval="15m".

Indicator combination: choose SINGLE INDICATOR, or DUAL etc. Let's choose DUAL Crossover: two moving averages or oscillators.

Threshold values: choose CONSERVATIVE or AGGRESSIVE. We want aggressive 30-50% of time. We can set thresholds fairly tight. For example, use 10-minute moving average vs 30-minute? Actually with 15-minute data, we can use 20 and 50 period moving averages cross.

But because of data period 30 days, 15 min bars ~ 96 bars per day (?), data length 30 days * (24h*4)? But if markets open 16h, but okay.

We need to use .flatten() on df['Close'].values. Use moving averages via np.mean.

Trading logic: CONDITIONAL: trade when multiple conditions align. We want aggressive, maybe use only two conditions but not too restrictive.

But rule: respond with BUY, SELL, or HOLD only string. Return "HOLD" otherwise.

We must use unique variable names.

Also must handle division by zero and NaN. Probably simple since no division though.

Check array length before computing.

We also can calculate relative strength index (RSI) with formula: RSI = 100 - (100/(1+RS)) where RS = avg gain / avg loss. Could compute over last 14 periods. But we don't have enough data? 14 periods of 15min is 210 min ~ 3.5 hours; fine.

Consider using RSI for decision: if RSI < 30, BUY; if > 70, SELL. But that would cause high frequency? Might be okay.

We also do DUAL Crossover of EMA 10 and EMA 30. But we can derive two EWMAs from close prices.

But data may be insufficient. Limit to at least 30 for EMA 30.

Let's define:
- period=30d, interval=15m; this will generate many rows.

Ok.

Implement:

global _mz_cache

On function call, if ticker not in cache, download.

Check len(df)>=30 else HOLD.

close_prices = df['Close'].values.flatten()

Compute 10-period and 30-period exponential weighted moving average using numpy ewm. But EWM method not available in numpy. Use simple moving average: mean of last 10 and 30.

Compute last close price.

Compute 10-day? Actually periods refer to number of bars, not days. We'll use 10 and 30 bars.

Check lengths.

Compute current_price.

Calculate sma10 = np.mean(close_prices[-10:]) if len>=10 else return HOLD.

sma30 = np.mean(close_prices[-30:]) if len>=30 else HOLD.

If current_price > sma10 and current_price > sma30: SMA cross? Actually crossing logic: if previous price snippet? We can use last two points:

prev_close = close_prices[-2]

prev_sma10 = np.mean(close_prices[-11:-1])  # last 10 excluding most recent? Actually need previous 10.

But easy: Use condition: if current price > sma10 and prev_close <= prev_sma10 -> buy.

Similarly sell when current < sma10 and prev_close >= prev_sma10.

Also integrate RSI: compute RSI over last 14 periods. If RSI < 30 maybe buy; if >70 sell. Combine with SMA condition to be more aggressive: if either condition triggers, buy/sell accordingly. But that might produce more trades.

Implementation:

def rsi(prices, period=14):
    deltas = np.diff(prices)
    if len(deltas) < period:
        return np.nan
    up = deltas.clip(min=0)
    down = -deltas.clip(max=0)
    roll_up = np.mean(up[-period:])
    roll_down = np.mean(down[-period:])
    if roll_down == 0:
        return 100.0
    rs = roll_up / roll_down
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val

We need to check division by zero.

Compute rsi_val for last 14.

Trading logic priorities: if RSI < 30 or (prev_close <= prev_sma10 and current > sma10) => BUY.

If RSI > 70 or (prev_close >= prev_sma10 and current < sma10) => SELL.

Else HOLD.

Ensure no division by zero: already handled.

Need to check len(close_prices) >= 30 for sma30. Also >= 14 for RSI. For SMA crossing need previous 10 for prev_sma10: need len>=12 maybe. But we can compute prev_sma10 as mean of close_prices[-12:-2] (exclude last 2). Then need len >=12.

We'll enforce that.

Compute if len<-12: return HOLD.

Implementation.

Also treat NaN prices: check if any nan in last close? If np.isnan(current_price) return HOLD.

Also check for any nans in close_prices, maybe skip? We can set mask.

Ok.

Unique variable names: _my_unique_cache, _price_history, _current_price, _sma_short, _sma_long, _prev_close, ...

Return only string.

Double-check no comments; output raw code only.

Also ensure use global _my_unique_cache.

Thus code:

import yfinance as yf
import numpy as np

_my_unique_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _my_unique_cache
    if ticker not in _my_unique_cache:
        _my_unique_cache[ticker] = yf.download(ticker, period="30d", interval="15m", progress=False)
    df = _my_unique_cache.get(ticker)
    if df is None or len(df) < 12:
        return "HOLD"
    close_prices = df['Close'].values.flatten()
    if len(close_prices) < 12:
        return "HOLD"
    if np.isnan(close_prices).any():
        return "HOLD"
    _current_price = float(close_prices[-1])
    if np.isnan(_current_price):
        return "HOLD"
    _sma_short = np.mean(close_prices[-10:])
    _sma_long = np.mean(close_prices[-30:]) if len(close_prices) >= 30 else np.nan
    if np.isnan(_sma_long):
        return "HOLD"
    _prev_close = float(close_prices[-2])
    _prev_sma_short = np.mean(close_prices[-12:-2])
    if np.isnan(_prev_sma_short):
        return "HOLD"
    # RSI
    def _calc_rsi(prs, period=14):
        if len(prs) < period + 1:
            return np.nan
        deltas = np.diff(prs)
        ups = np.clip(deltas, a_min=0, a_max=None)
        downs = -np.clip(deltas, a_min=None, a_max=0)
        avg_up = np.mean(ups[-period:])
        avg_down = np.mean(downs[-period:])
        if avg_down == 0:
            return 100.0
        rs = avg_up / avg_down
        rsi_val = 100.0 - (100.0 / (1.0 + rs))
        return rsi_val
    _rsi_val = _calc_rsi(close_prices, 14)
    if np.isnan(_rsi_val):
        return "HOLD"
    if _rsi_val < 30.0 or (_prev_close <= _prev_sma_short and _current_price > _sma_short):
        return "BUY"
    if _rsi_val > 70.0 or (_prev_close >= _prev_sma_short and _current_price < _sma_short):
        return "SELL"
    return "HOLD"

Return raw code. Ensure no / etc. And no markdown.

Let's incorporate all.assistantfinalimport yfinance as yf
import numpy as np

_my_unique_cache = {}

def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:
    global _my_unique_cache
    if ticker not in _my_unique_cache:
        _my_unique_cache[ticker] = yf.download(ticker, period="30d", interval="15m", progress=False)
    df = _my_unique_cache.get(ticker)
    if df is None or len(df) < 12:
        return "HOLD"
    close_prices = df['Close'].values.flatten()
    if len(close_prices) < 12:
        return "HOLD"
    if np.isnan(close_prices).any():
        return "HOLD"
    _current_price = float(close_prices[-1])
    if np.isnan(_current_price):
        return "HOLD"
    _sma_short = np.mean(close_prices[-10:])
    if len(close_prices) < 30:
        return "HOLD"
    _sma_long = np.mean(close_prices[-30:])
    if np.isnan(_sma_long):
        return "HOLD"
    _prev_close = float(close_prices[-2])
    if len(close_prices) < 12:
        return "HOLD"
    _prev_sma_short = np.mean(close_prices[-12:-2])
    if np.isnan(_prev_sma_short):
        return "HOLD"
    def _calc_rsi(prs, period=14):
        if len(prs) < period + 1:
            return np.nan
        deltas = np.diff(prs)
        ups = np.clip(deltas, a_min=0, a_max=None)
        downs = -np.clip(deltas, a_min=None, a_max=0)
        avg_up = np.mean(ups[-period:])
        avg_down = np.mean(downs[-period:])
        if avg_down == 0:
            return 100.0
        rs = avg_up / avg_down
        rsi_val = 100.0 - (100.0 / (1.0 + rs))
        return rsi_val
    _rsi_val = _calc_rsi(close_prices, 14)
    if np.isnan(_rsi_val):
        return "HOLD"
    if _rsi_val < 30.0 or (_prev_close <= _prev_sma_short and _current_price > _sma_short):
        return "BUY"
    if _rsi_val > 70.0 or (_prev_close >= _prev_sma_short and _current_price < _sma_short):
        return "SELL"
    return "HOLD"