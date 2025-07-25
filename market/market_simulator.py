from market.tick_generator import generate_tick
from market.order_book import OrderBook
import time

class MarketSimulator:
    def __init__(self, agents: list, starting_price: float = 100.0):
        self.agents = agents
        self.price = starting_price
        self.order_book = OrderBook()

        # Tracxk agent positions and cash
        self.portfolio = {
            agent.name: {
                "cash": 500,
                "stock": 10
            } for agent in agents
        }

    def run(self, steps: int = 300):
        """
        Run the market simulation for 'steps' ticks.

        Args:
            steps (int): Number of ticks to simulate.
        """
        for step in range(steps):
            print(f"\nTick {step + 1} — Current price: {self.price}")

            # 1. Generate new price
            self.price = generate_tick(self.price)

            # 2. Agents submit orders
            all_orders = []
            for agent in self.agents:
                orders = agent.on_tick(self.price)
                all_orders.extend(orders)

            # 3. Match orders
            trades = self.order_book.match_orders(all_orders)

            # 4. Update portfolios
            self._update_portfolios(trades)

            # 5. Display trades
            for trade in trades:
                print(f"Trade: {trade['buyer']} bought {trade['quantity']} from {trade['seller']} at {trade['price']}")

            time.sleep(0.1)  # Control speed of simulation

        # Final results
        print("\n--- Final Results ---")
        for name, data in self.portfolio.items():
            net_worth = data["cash"] + data["stock"] * self.price
            print(f"{name}: Cash=${data['cash']:.2f}, Stock={data['stock']} → Net=${net_worth:.2f}")

    def _update_portfolios(self, trades):
        for trade in trades:
            price = trade["price"]
            qty = trade["quantity"]
            buyer = trade["buyer"]
            seller = trade["seller"]

            # Buyer loses cash, gains stock
            self.portfolio[buyer]["cash"] -= price * qty
            self.portfolio[buyer]["stock"] += qty

            # Seller gains cash, loses stock
            self.portfolio[seller]["cash"] += price * qty
            self.portfolio[seller]["stock"] -= qty
