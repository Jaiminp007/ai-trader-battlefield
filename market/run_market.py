

import sys
from pathlib import Path

# Add parent directory to path to allow imports from agents
sys.path.append(str(Path(__file__).parent.parent))

from market.market_simulator import MarketSimulator
from market.agent import TradingAgent

# Import our new AI-powered agents
from agents.ollama_agent import OllamaAgent
from agents.mistral_agent import MistralAgent


def main():
    agents = [
        OllamaAgent("OllamaAI"),
        MistralAgent("MistralAI"),
        TradingAgent("RandomBaseline"),
    ]
    sim = MarketSimulator(agents, starting_price=100.0)  # Start at $100
    print("Starting simulation - 15 ticks with 1-second intervals")
    sim.run(steps=15)  # Run for exactly 15 ticks


if __name__ == "__main__":
    main()
