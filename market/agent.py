import random

class TradingAgent:
    def __init__(self, name):
        self.name = name

    def on_tick(self, price):
        """
        Decide what orders to place at each tick.
        Returns a list of orders. Each order is a dict:
        {
            "agent": self.name,
            "side": "buy" or "sell",
            "price": float,
            "quantity": int
        }
        """
        # Random decision to buy or sell
        side = random.choice(["buy", "sell"])
        # Price offset randomly from current price
        price_offset = random.uniform(-2, 2)
        order_price = round(price + price_offset, 2)
        quantity = random.randint(1, 5)

        return [{
            "agent": self.name,
            "side": side,
            "price": order_price,
            "quantity": quantity
        }]
