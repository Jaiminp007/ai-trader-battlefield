from __future__ import annotations

import sys
import os
from pathlib import Path
import traceback
import hashlib
import random

# Add the open_router directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent / "open_router"))

from market.tick_generator import YFinanceTickGenerator, display_stock_chart
from market.market_simulation import MarketSimulation
from market.agent import MarketMakerAgent

import warnings
from typing import Callable, Dict, Any, List
import uuid
import importlib.util

# Optimized AlgoAgent that loads the module once and calls it directly
class AlgoAgent:
    def __init__(self, name: str, module_path: str, symbol: str):
        self.name = name
        self.symbol = symbol
        self._module_path = module_path
        self._hold_streak = 0  # Count consecutive HOLDs to seed positions
        self._trade_function = self._load_module()
        # Per-agent deterministic behavior parameters to diversify actions
        seed_int = int(hashlib.md5(self.name.encode()).hexdigest()[:8], 16)
        self._rng = random.Random(seed_int)
        # Trade frequency throttle: some agents act every tick, others every 2nd/3rd tick
        self._tick_skip_mod = self._rng.choice([1, 1, 1, 2])
        # Position sizing (fractions of affordable/held)
        self._buy_frac_lo = self._rng.uniform(0.05, 0.15)
        self._buy_frac_hi = min(0.60, self._buy_frac_lo + self._rng.uniform(0.05, 0.25))
        self._sell_frac = self._rng.uniform(0.10, 0.50)
        # Limit price offsets in basis points (bps)
        self._buy_bps = self._rng.uniform(10.0, 40.0)   # 0.10% - 0.40% above market
        self._sell_bps = self._rng.uniform(10.0, 40.0)  # 0.10% - 0.40% below market
        # HOLD seeding cadence and preference
        self._seed_ticks = self._rng.randint(2, 5)
        self._seed_prefer_sell = self._rng.choice([True, False])
        print(f"✅ {self.name}: Loaded with direct import optimization")

    def _load_module(self) -> Callable[..., str]:
        """Load the execute_trade function from the agent's module path."""
        try:
            spec = importlib.util.spec_from_file_location(self.name, self._module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'execute_trade') and callable(module.execute_trade):
                    return module.execute_trade
        except Exception as e:
            print(f"❌ Error loading module for {self.name}: {e}")
        # Return a dummy function if loading fails
        return lambda ticker, cash, stock: "HOLD"

    def on_tick(self, price: float, current_tick: int, cash: float = 0.0, stock: int = 0):
        """Execute the AI-generated trading algorithm with optimized isolation."""
        try:
            # Optional per-agent tick throttling
            if self._tick_skip_mod > 1 and (current_tick % self._tick_skip_mod != 0):
                return []

            # Execute the AI algorithm's decision function directly
            decision = self._trade_function(self.symbol, cash, stock)
            
            # Process the AI's decision (un-gated to allow margin/short; engine clamps size)
            if decision == "BUY":
                self._hold_streak = 0
                qty = self._rng.randint(5, 18)
                bid_price = round(price * (1.0 + self._buy_bps / 10000.0), 2)
                return [{"agent": self.name, "side": "buy", "price": bid_price, "quantity": qty}]

            elif decision == "SELL":
                self._hold_streak = 0
                qty = self._rng.randint(5, 18)
                ask_price = round(price * (1.0 - self._sell_bps / 10000.0), 2)
                return [{"agent": self.name, "side": "sell", "price": ask_price, "quantity": qty}]

            # If HOLD, track streaks to seed a position if algos are too conservative
            else: # decision == "HOLD"
                self._hold_streak += 1
                if self._hold_streak >= self._seed_ticks:
                    self._hold_streak = 0 # Reset after seeding
                    # Prefer a small sell if configured and we hold stock; otherwise seed a buy
                    if self._seed_prefer_sell and stock > 0:
                        qty = max(1, min(3, stock))
                        ask_price = round(price * (1.0 - self._sell_bps / 20000.0), 2)  # half offset
                        return [{"agent": self.name, "side": "sell", "price": ask_price, "quantity": qty}]
                    elif cash > price:
                        max_affordable = int(cash // price)
                        if max_affordable > 0:
                            qty = max(1, min(3, max_affordable))
                            bid_price = round(price * (1.0 + self._buy_bps / 20000.0), 2)  # half offset
                            return [{"agent": self.name, "side": "buy", "price": bid_price, "quantity": qty}]
        
        except Exception as e:
            print(f"⚠️ Error executing {self.name} algorithm: {e}")
            # Print full traceback to pinpoint source lines inside generated algorithms
            print(traceback.format_exc())
            
        return []

def main():
    print("🤖 AI TRADER BATTLEFIELD - Market Simulation")
    print("=" * 50)
    
    # Silence noisy future warnings from pandas/yfinance during the battle
    warnings.filterwarnings("ignore", category=FutureWarning)

    symbol = "AAPL"
    
    # Step 1: Generate trading algorithms (skipped if we already have any)
    print("\n🧠 STEP 1: Generating Trading Algorithms")
    print("-" * 40)
    base_gen = Path(__file__).resolve().parent / "generate_algo"
    base_open = Path(__file__).resolve().parent / "open_router"
    pre_existing = list(base_gen.glob("generated_algo_*.py")) + list(base_open.glob("generated_algo_*.py"))
    if pre_existing:
        print(f"⏭️ Skipping generation: found {len(pre_existing)} existing generated algorithms")
    else:
        try:
            from open_router.algo_gen import main as generate_algorithms
            selected_ticker = generate_algorithms()
            if selected_ticker:
                symbol = selected_ticker
                print(f"✅ Algorithm generation completed successfully (selected ticker: {symbol})")
            else:
                print("✅ Algorithm generation completed successfully")
        except Exception as e:
            print(f"⚠️ Warning: Algorithm generation failed: {e}")
            print("📝 Continuing with existing algorithms...")
    
    # Step 2: Display 30-day stock chart
    print("\n📈 STEP 2: Displaying Stock Chart")
    print("-" * 40)
    try:
        display_stock_chart(symbol, days=30)
    except Exception as e:
        print(f"⚠️ Warning: Chart display failed: {e}")
        print("📝 Continuing without chart...")
    
    # Step 3: Initialize market simulation
    print("\n🏦 STEP 3: Starting Market Simulation")
    print("-" * 40)
    
    # Create tick generator for simulation with faster processing
    tick_src = YFinanceTickGenerator(symbol=symbol, period="1d", interval="1m").stream(sleep_seconds=0.1)  # Reduced sleep

    # Discover generated algorithm modules
    # Paths already defined above for generation skip
    
    # Discover any generated_algo_*.py files in both locations
    discovered = list(base_gen.glob("generated_algo_*.py")) + list(base_open.glob("generated_algo_*.py"))
    
    # Deduplicate by name
    seen = set()
    algo_modules = []
    for p in discovered:
        if p.name in seen:
            continue
        seen.add(p.name)
        algo_modules.append(p)

    # Load AI-generated trading agents
    agents = []
    if not algo_modules:
        print(f"❌ No generated algorithms found in {base_gen} or {base_open}.")
        print("Please run the algorithm generation first.")
        return
        
    print(f"🔍 Found {len(algo_modules)} algorithm files:")
    for p in algo_modules:
        print(f"  - {p.name}")
    
    # Load each algorithm as a separate agent
    for p in algo_modules:
        try:
            agent = AlgoAgent(name=p.stem, module_path=str(p), symbol=symbol)
            agents.append(agent)
            print(f"✅ Loaded: {p.stem}")
        except Exception as e:
            print(f"❌ Failed to load {p.name}: {e}")

    if not agents:
        print("❌ No valid trading agents could be loaded. Exiting.")
        return
    
    print(f"📊 Loaded {len(agents)} AI trading agents for simulation")

    # Add liquidity providers (excluded from the final leaderboard)
    agents.append(MarketMakerAgent("Liquidity_MM1", spread_bps=8.0, quantity=5))
    agents.append(MarketMakerAgent("Liquidity_MM2", spread_bps=12.0, quantity=3))
    print("➕ Added liquidity providers: Liquidity_MM1, Liquidity_MM2")

    # Create simulation with ORDER BOOK ENABLED and faster processing
    from market.market_simulation import SimulationConfig
    config = SimulationConfig(
        max_ticks=60,
        tick_sleep=0.01,  # 10ms between ticks for speed
        log_trades=True,
        log_orders=True,  # Enable order logging to see what's happening
        enable_order_book=True,  # ENABLE ORDER BOOK for proper matching
        initial_cash=10000.0,
        initial_stock=5,
        # Enable margin and short selling to increase volume/ROE dispersion
        allow_negative_cash=True,
        cash_borrow_limit=20000.0,
        allow_short=True,
        max_short_shares=25,
        # Expire unfilled limit orders each tick to free reservations
        order_ttl_ticks=1
    )
    
    sim = MarketSimulation(agents, config)

    # Run the simulation
    try:
        results = sim.run(ticks=tick_src, max_ticks=60, log=True)
    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")

    # Compute final results and declare winner
    print("\n" + "=" * 60)
    print("🏁 BATTLE RESULTS (sorted by ROI)")
    print("=" * 60)

    # Prefer simulation's leaderboard (uses fair baseline set on first tick)
    leaderboard = []
    if isinstance(results, dict) and 'leaderboard' in results:
        leaderboard = [row for row in results['leaderboard'] if not row['name'].startswith("Liquidity_")]
    else:
        # Fallback: compute from sim state if results missing
        leaderboard = []
        for name, pf in sim.portfolio.items():
            if name.startswith("Liquidity_"):
                continue
            initial = getattr(sim.agent_manager, 'initial_values', {}).get(name, 10000.0)
            final_val = pf.cash + pf.stock * max(sim.last_price, 0.0)
            roi_val = 0.0 if initial == 0 else (final_val - initial) / initial * 100.0
            leaderboard.append({
                'name': name,
                'roi': roi_val,
                'current_value': final_val,
                'cash': pf.cash,
                'stock': pf.stock,
                'trades': len([t for t in sim.agent_manager.trade_records if t.agent_name == name])
            })

    leaderboard.sort(key=lambda x: x['roi'], reverse=True)

    for row in leaderboard:
        print(f"{row['name']}: ROI={row['roi']:+.2f}% | Final=${row['current_value']:.2f} (cash=${row['cash']:.2f}, stock={row['stock']})")

    if leaderboard:
        winner = leaderboard[0]
        print("-" * 60)
        print(f"🏆 Winner: {winner['name']} with ROI {winner['roi']:+.2f}% and Final ${winner['current_value']:.2f}")
        
        # Show performance analysis
        print("\n📊 PERFORMANCE ANALYSIS:")
        print("-" * 30)
        for i, row in enumerate(leaderboard, 1):
            if i == 1:
                print(f"🥇 {row['name']}: {row['roi']:+.2f}% ROI")
            elif i == 2:
                print(f"🥈 {row['name']}: {row['roi']:+.2f}% ROI")
            elif i == 3:
                print(f"🥉 {row['name']}: {row['roi']:+.2f}% ROI")
            else:
                print(f"  {i}. {row['name']}: {row['roi']:+.2f}% ROI")


if __name__ == "__main__":
    main()