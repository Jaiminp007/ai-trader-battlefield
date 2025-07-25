class OrderBook:
    def __init__(self):
        self.trades = []  # store completed trades

    def match_orders(self, orders: list) -> list:
        """
        Matches buy/sell orders from agents.

        Args:
            orders (list): List of dicts with 'agent', 'side', 'price', and 'quantity'

        Returns:
            list: Executed trades
        """
        buys = sorted([o for o in orders if o["side"] == "buy"], key=lambda x: -x["price"])
        sells = sorted([o for o in orders if o["side"] == "sell"], key=lambda x: x["price"])
        
        trades = []

        while buys and sells and buys[0]["price"] >= sells[0]["price"]:
            buy_order = buys[0]
            sell_order = sells[0]
            
            trade_price = (buy_order["price"] + sell_order["price"]) / 2
            quantity = min(buy_order["quantity"], sell_order["quantity"])

            trades.append({
                "buyer": buy_order["agent"],
                "seller": sell_order["agent"],
                "price": round(trade_price, 2),
                "quantity": quantity
            })

            # Update or remove orders after trade
            buy_order["quantity"] -= quantity
            sell_order["quantity"] -= quantity
            if buy_order["quantity"] == 0:
                buys.pop(0)
            if sell_order["quantity"] == 0:
                sells.pop(0)

        self.trades.extend(trades)
        return trades
