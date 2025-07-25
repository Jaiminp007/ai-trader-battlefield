import random

"""Each tick (e.g. each second), this generates a new price by adding a random number between -1 and +1 to the previous price.
 You could later replace this with real stock data from Yahoo Finance or another source."""

def generate_tick(prev_price: float) -> float:
    delta = random.uniform(-1.0, 1.0)  # small fluctuation
    new_price = round(prev_price + delta, 2)
    return max(new_price, 0.1)  # Price can't go negative
