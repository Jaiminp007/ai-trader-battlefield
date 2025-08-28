"""
Advanced Order Book Implementation for Market Simulation
Supports limit orders, market orders, order matching, and trade execution.
"""

from typing import Dict, List, Optional, Tuple, NamedTuple
from enum import Enum
import heapq
import time
from dataclasses import dataclass, field


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"


@dataclass
class Order:
    order_id: str
    agent_name: str
    side: OrderSide
    quantity: int
    price: float
    order_type: OrderType = OrderType.LIMIT
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Order quantity must be positive")
        if self.order_type == OrderType.LIMIT and self.price <= 0:
            raise ValueError("Limit order price must be positive")


class Trade(NamedTuple):
    trade_id: str
    buy_agent: str
    sell_agent: str
    quantity: int
    price: float
    timestamp: float
    buy_order_id: str
    sell_order_id: str


class OrderBook:
    def __init__(self):
        # Buy orders (bids) - max heap (highest price first)
        self.bids: List[Tuple[float, float, Order]] = []  # (-price, timestamp, order)
        # Sell orders (asks) - min heap (lowest price first)  
        self.asks: List[Tuple[float, float, Order]] = []  # (price, timestamp, order)
        
        # Order tracking
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.trade_counter = 0
        
        # Market data
        self.last_trade_price: Optional[float] = None
        self.best_bid: Optional[float] = None
        self.best_ask: Optional[float] = None
        
    def add_order(self, order: Order) -> List[Trade]:
        """Add an order to the book and execute any possible trades."""
        if order.order_id in self.orders:
            raise ValueError(f"Order {order.order_id} already exists")
            
        # Track the order (market orders will be removed after execution)
        self.orders[order.order_id] = order
        trades = []
        
        if order.order_type == OrderType.MARKET:
            trades = self._execute_market_order(order)
            # Market orders do not rest on the book; remove tracking entry
            if order.order_id in self.orders:
                del self.orders[order.order_id]
        else:  # LIMIT order
            trades = self._execute_limit_order(order)
            
        self._update_market_data()
        return trades
        
    def _execute_market_order(self, order: Order) -> List[Trade]:
        """Execute a market order against the best available prices."""
        trades = []
        remaining_quantity = order.quantity
        
        if order.side == OrderSide.BUY:
            # Buy market order - match against asks (sells)
            while remaining_quantity > 0 and self.asks:
                best_ask_price, _, best_ask = heapq.heappop(self.asks)
                
                trade_quantity = min(remaining_quantity, best_ask.quantity)
                trade = self._create_trade(
                    order.agent_name,
                    best_ask.agent_name,
                    trade_quantity,
                    best_ask_price,
                    buy_order_id=order.order_id,
                    sell_order_id=best_ask.order_id,
                )
                trades.append(trade)
                
                remaining_quantity -= trade_quantity
                best_ask.quantity -= trade_quantity
                
                # If ask order is partially filled, put it back
                if best_ask.quantity > 0:
                    heapq.heappush(self.asks, (best_ask_price, best_ask.timestamp, best_ask))
                else:
                    # Remove fully executed order
                    del self.orders[best_ask.order_id]
                    
        else:  # SELL market order
            # Sell market order - match against bids (buys)
            while remaining_quantity > 0 and self.bids:
                neg_best_bid_price, _, best_bid = heapq.heappop(self.bids)
                best_bid_price = -neg_best_bid_price
                
                trade_quantity = min(remaining_quantity, best_bid.quantity)
                trade = self._create_trade(
                    best_bid.agent_name,
                    order.agent_name,
                    trade_quantity,
                    best_bid_price,
                    buy_order_id=best_bid.order_id,
                    sell_order_id=order.order_id,
                )
                trades.append(trade)
                
                remaining_quantity -= trade_quantity
                best_bid.quantity -= trade_quantity
                
                # If bid order is partially filled, put it back
                if best_bid.quantity > 0:
                    heapq.heappush(self.bids, (neg_best_bid_price, best_bid.timestamp, best_bid))
                else:
                    # Remove fully executed order
                    del self.orders[best_bid.order_id]
                    
        return trades
        
    def _execute_limit_order(self, order: Order) -> List[Trade]:
        """Execute a limit order, matching against opposite side if possible."""
        trades = []
        remaining_quantity = order.quantity
        
        if order.side == OrderSide.BUY:
            # Buy limit order - match against asks at or below our price
            while remaining_quantity > 0 and self.asks and self.asks[0][0] <= order.price:
                ask_price, _, ask_order = heapq.heappop(self.asks)
                
                trade_quantity = min(remaining_quantity, ask_order.quantity)
                trade = self._create_trade(
                    order.agent_name,
                    ask_order.agent_name,
                    trade_quantity,
                    ask_price,
                    buy_order_id=order.order_id,
                    sell_order_id=ask_order.order_id,
                )
                trades.append(trade)
                
                remaining_quantity -= trade_quantity
                ask_order.quantity -= trade_quantity
                
                if ask_order.quantity > 0:
                    heapq.heappush(self.asks, (ask_price, ask_order.timestamp, ask_order))
                else:
                    del self.orders[ask_order.order_id]
                    
            # Add remaining quantity to bid book or remove fully filled
            if remaining_quantity > 0:
                order.quantity = remaining_quantity
                heapq.heappush(self.bids, (-order.price, order.timestamp, order))
            else:
                if order.order_id in self.orders:
                    del self.orders[order.order_id]
                
        else:  # SELL limit order
            # Sell limit order - match against bids at or above our price
            while remaining_quantity > 0 and self.bids and -self.bids[0][0] >= order.price:
                neg_bid_price, _, bid_order = heapq.heappop(self.bids)
                bid_price = -neg_bid_price
                
                trade_quantity = min(remaining_quantity, bid_order.quantity)
                trade = self._create_trade(
                    bid_order.agent_name,
                    order.agent_name,
                    trade_quantity,
                    bid_price,
                    buy_order_id=bid_order.order_id,
                    sell_order_id=order.order_id,
                )
                trades.append(trade)
                
                remaining_quantity -= trade_quantity
                bid_order.quantity -= trade_quantity
                
                if bid_order.quantity > 0:
                    heapq.heappush(self.bids, (neg_bid_price, bid_order.timestamp, bid_order))
                else:
                    del self.orders[bid_order.order_id]
                    
            # Add remaining quantity to ask book or remove fully filled
            if remaining_quantity > 0:
                order.quantity = remaining_quantity
                heapq.heappush(self.asks, (order.price, order.timestamp, order))
            else:
                if order.order_id in self.orders:
                    del self.orders[order.order_id]
                
        return trades
        
    def _create_trade(self, buy_agent: str, sell_agent: str, quantity: int, price: float, buy_order_id: str, sell_order_id: str) -> Trade:
        """Create a new trade record."""
        self.trade_counter += 1
        trade = Trade(
            trade_id=f"trade_{self.trade_counter}",
            buy_agent=buy_agent,
            sell_agent=sell_agent,
            quantity=quantity,
            price=price,
            timestamp=time.time(),
            buy_order_id=buy_order_id,
            sell_order_id=sell_order_id,
        )
        self.trades.append(trade)
        self.last_trade_price = price
        return trade
        
    def _update_market_data(self):
        """Update best bid/ask prices."""
        self.best_bid = -self.bids[0][0] if self.bids else None
        self.best_ask = self.asks[0][0] if self.asks else None
        
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order if it exists in the book."""
        if order_id not in self.orders:
            return False
            
        order = self.orders[order_id]
        
        # Remove from appropriate heap
        if order.side == OrderSide.BUY:
            self.bids = [(p, t, o) for p, t, o in self.bids if o.order_id != order_id]
            heapq.heapify(self.bids)
        else:
            self.asks = [(p, t, o) for p, t, o in self.asks if o.order_id != order_id]
            heapq.heapify(self.asks)
            
        del self.orders[order_id]
        self._update_market_data()
        return True
        
    def get_market_depth(self, levels: int = 5) -> Dict:
        """Get market depth showing top N levels of bids and asks."""
        # Aggregate bids by price (descending)
        bid_levels = []
        bid_agg: Dict[float, int] = {}
        for neg_price, _, order in self.bids:
            price = -neg_price
            bid_agg[price] = bid_agg.get(price, 0) + order.quantity
        for price in sorted(bid_agg.keys(), reverse=True)[:levels]:
            bid_levels.append({"price": price, "quantity": bid_agg[price]})
        
        # Aggregate asks by price (ascending)
        ask_levels = []
        ask_agg: Dict[float, int] = {}
        for price, _, order in self.asks:
            ask_agg[price] = ask_agg.get(price, 0) + order.quantity
        for price in sorted(ask_agg.keys())[:levels]:
            ask_levels.append({"price": price, "quantity": ask_agg[price]})
        
        return {
            "bids": bid_levels,
            "asks": ask_levels,
            "spread": ask_levels[0]["price"] - bid_levels[0]["price"] if bid_levels and ask_levels else None
        }
        
    def get_stats(self) -> Dict:
        """Get order book statistics."""
        return {
            "total_orders": len(self.orders),
            "total_trades": len(self.trades),
            "last_trade_price": self.last_trade_price,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread": (self.best_ask - self.best_bid) if self.best_bid and self.best_ask else None,
            "bid_orders": len(self.bids),
            "ask_orders": len(self.asks)
        }
