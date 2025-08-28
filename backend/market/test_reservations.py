"""
Offline tests for reservation ledger logic in MarketSimulation.
These tests run without external data sources.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Iterator

from .market_simulation import MarketSimulation, SimulationConfig
from .tick_generator import TickData


class PlanAgent:
    """Agent that emits pre-planned orders per tick."""
    def __init__(self, name: str, plan: Dict[int, List[Dict[str, Any]]]):
        self.name = name
        self.plan = plan

    def on_tick(self, price: float, current_tick: int, cash: float = 0.0, stock: int = 0) -> List[Dict[str, Any]]:
        return self.plan.get(current_tick, [])


def constant_ticks(symbol: str, price: float, n: int) -> Iterator[TickData]:
    ts = datetime.now()
    for i in range(n):
        yield TickData(
            timestamp=ts + timedelta(seconds=i),
            open_price=price,
            high=price,
            low=price,
            close=price,
            volume=1000,
            symbol=symbol,
        )


def test_buy_reservations_no_match():
    # One buyer places two large limit orders that would overspend without reservations.
    buyer = PlanAgent(
        name="Buyer",
        plan={
            0: [{"agent": "Buyer", "side": "buy", "price": 100.0, "quantity": 60}],  # reserve $6000
            1: [{"agent": "Buyer", "side": "buy", "price": 100.0, "quantity": 50}],  # should be adjusted to 40
        },
    )

    cfg = SimulationConfig(max_ticks=3, log_trades=False, log_orders=False, enable_order_book=True, initial_cash=10000.0)
    sim = MarketSimulation([buyer], cfg)

    # Run on constant ticks so no external calls
    list(sim.run(constant_ticks("TEST", 100.0, 3), max_ticks=3, log=False).items())

    reserved = sim._agent_reserved_cash.get("Buyer", 0.0)
    assert abs(reserved - 10000.0) < 1e-6, f"Expected $10000 reserved, got {reserved}"


def test_sell_reservations_no_match():
    # One seller places two large orders that would oversell without reservations.
    seller = PlanAgent(
        name="Seller",
        plan={
            0: [{"agent": "Seller", "side": "sell", "price": 105.0, "quantity": 60}],  # reserve 60 shares
            1: [{"agent": "Seller", "side": "sell", "price": 105.0, "quantity": 60}],  # should be adjusted to 40
        },
    )

    cfg = SimulationConfig(max_ticks=3, log_trades=False, log_orders=False, enable_order_book=True, initial_cash=10000.0)
    sim = MarketSimulation([seller], cfg)

    # Give seller initial stock of 100
    sim.agent_manager.portfolios["Seller"].stock = 100

    list(sim.run(constant_ticks("TEST", 100.0, 3), max_ticks=3, log=False).items())

    reserved_qty = sim._agent_reserved_stock.get("Seller", 0)
    assert reserved_qty == 100, f"Expected 100 shares reserved, got {reserved_qty}"


def test_reservations_release_on_match():
    # Buyer and Seller cross so trades execute and reservations are released.
    buyer = PlanAgent(
        name="Buyer",
        plan={
            0: [{"agent": "Buyer", "side": "buy", "price": 100.0, "quantity": 10}],
        },
    )
    seller = PlanAgent(
        name="Seller",
        plan={
            0: [{"agent": "Seller", "side": "sell", "price": 99.0, "quantity": 10}],
        },
    )

    cfg = SimulationConfig(max_ticks=1, log_trades=False, log_orders=False, enable_order_book=True, initial_cash=10000.0)
    sim = MarketSimulation([buyer, seller], cfg)
    sim.agent_manager.portfolios["Seller"].stock = 10

    list(sim.run(constant_ticks("TEST", 100.0, 1), max_ticks=1, log=False).items())

    # After full match, per-order reservations should be cleared and aggregated should be zero
    assert sim._agent_reserved_cash.get("Buyer", 0.0) == 0.0, f"Buyer reserved cash not cleared: {sim._agent_reserved_cash.get('Buyer')}"
    assert sim._agent_reserved_stock.get("Seller", 0) == 0, f"Seller reserved stock not cleared: {sim._agent_reserved_stock.get('Seller')}"


if __name__ == "__main__":
    print("Running reservation tests...")
    test_buy_reservations_no_match()
    print("✅ test_buy_reservations_no_match passed")
    test_sell_reservations_no_match()
    print("✅ test_sell_reservations_no_match passed")
    test_reservations_release_on_match()
    print("✅ test_reservations_release_on_match passed")
    print("All tests passed ✅")
