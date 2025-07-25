"""OllamaAgent
This agent demonstrates how you could integrate a local Ollama LLM to produce trading
signals.  If Ollama is not installed or the model call fails, it falls back to a
very simple moving-average crossover strategy so the simulation can still run.

NOTE: Replace the `_query_llm` implementation with your actual Ollama invocation
details.  For large-scale runs you might want async calls, caching, etc.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

# Re-use base TradingAgent interface for typing clarity.
from market.agent import TradingAgent

DATA_PATH = Path(__file__).resolve().parent.parent / "market" / "data" / "historical_prices.csv"


class OllamaAgent(TradingAgent):
    def __init__(self, name: str = "OllamaTrader", model: str = "llama3"):
        super().__init__(name)
        self.model = model
        self.prices = self._load_prices()
        # Pre-compute two MAs for fallback algo
        self.short_ma = self.prices.rolling(window=5).mean()
        self.long_ma = self.prices.rolling(window=20).mean()
        self.tick_index = 0  # moves forward each on_tick

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _load_prices(self) -> pd.Series:
        """Load historical prices CSV into a pandas Series."""
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Historical data file not found: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
        # assume columns: date, price
        return df["price"]

    def _query_llm(self, prompt: str) -> str:
        """Call Ollama via CLI; returns raw text.  You can adjust flags as needed."""
        try:
            proc = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                check=True,
            )
            return proc.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Ollama not available – raise so we trigger fallback
            raise RuntimeError("Ollama call failed")

    # ---------------------------------------------------------------------
    # Core API consumed by MarketSimulator
    # ---------------------------------------------------------------------
    def on_tick(self, price: float) -> List[Dict[str, Any]]:
        """Return a list with at most one order dict for this tick."""
        # 1) Build simple JSON prompt
        prompt = (
            "You are an algorithmic trader. Current market price is "
            f"{price:.2f}. Respond with JSON having keys side (buy/sell/hold) "
            "and quantity (int, 1-5). Do not output anything else."
        )

        try:
            raw = self._query_llm(prompt)
            data = json.loads(raw)
            side = data.get("side", "hold").lower()
            qty = int(data.get("quantity", 0))
        except Exception:
            # Fallback: MA crossover
            side, qty = self._fallback_signal()

        if side == "hold" or qty <= 0:
            return []

        return [
            {
                "agent": self.name,
                "side": side,
                "price": price,  # market order at current price
                "quantity": min(qty, 5),
            }
        ]

    # ------------------------------------------------------------------
    # Fallback strategy: moving-average crossover
    # ------------------------------------------------------------------
    def _fallback_signal(self):
        if self.tick_index >= len(self.prices):
            return "hold", 0
        short = self.short_ma.iloc[self.tick_index]
        long = self.long_ma.iloc[self.tick_index]
        self.tick_index += 1
        if pd.isna(short) or pd.isna(long):
            return "hold", 0
        if short > long:
            return "buy", 3
        elif short < long:
            return "sell", 3
        else:
            return "hold", 0
