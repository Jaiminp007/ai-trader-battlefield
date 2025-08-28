"""
Market Simulation Module

This module provides a complete market simulation environment with:
- Order book management with realistic trade matching
- Yahoo Finance data integration for real market data
- Trading agent framework with portfolio management  
- Comprehensive performance tracking and analytics
- Live visualization and reporting

Main Components:
- MarketSimulation: Main simulation orchestrator
- OrderBook: Advanced order matching engine
- YFinanceTickGenerator: Real-time market data provider
- AgentManager: Trading agent and portfolio management
- TradingAgent: Base interface for trading algorithms

Example Usage:
    from market import MarketSimulation, YFinanceTickGenerator
    from market.agent import create_sample_agents
    
    # Create agents and simulation
    agents = create_sample_agents()
    sim = MarketSimulation(agents)
    
    # Run simulation with real data
    tick_gen = YFinanceTickGenerator("AAPL")
    results = sim.run(tick_gen.stream())
"""

# Import main classes for easy access
from .market_simulation import MarketSimulation, SimulationConfig
from .tick_generator import YFinanceTickGenerator, TickData, display_stock_chart
from .order_book import OrderBook, Order, OrderSide, OrderType
from .agent import (
    AgentManager, TradingAgent, BaseAgent, Portfolio,
    RandomAgent, MomentumAgent, MeanReversionAgent, MarketMakerAgent,
    create_sample_agents
)

# Version info
__version__ = "1.0.0"
__author__ = "AI Trader Battlefield"

# Export main classes
__all__ = [
    # Core simulation
    "MarketSimulation",
    "SimulationConfig",
    
    # Data providers
    "YFinanceTickGenerator", 
    "TickData",
    "display_stock_chart",
    
    # Order management
    "OrderBook",
    "Order", 
    "OrderSide",
    "OrderType",
    
    # Agent management
    "AgentManager",
    "TradingAgent",
    "BaseAgent", 
    "Portfolio",
    "RandomAgent",
    "MomentumAgent", 
    "MeanReversionAgent",
    "MarketMakerAgent",
    "create_sample_agents"
]
