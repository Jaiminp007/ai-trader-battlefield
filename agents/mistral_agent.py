"""MistralAgent
Example agent that could call a Mistral 7B/8x endpoint (local or remote).
If the HTTP call fails, it falls back to a simple momentum strategy.
"""
from __future__ import annotations

import json
import os
from typing import List, Dict, Any, Optional

import requests

from market.agent import TradingAgent

MISTRAL_ENDPOINT = os.getenv("MISTRAL_ENDPOINT", "http://localhost:11434/v1/chat")


class MistralAgent(TradingAgent):
    def __init__(self, name: str = "MistralTrader", model: str = "mistral"):
        super().__init__(name)
        self.model = model
        self.last_price: Optional[float] = None  # for fallback momentum strategy

    # ------------------------------------------------------------------
    def _query_llm(self, price: float) -> dict | None:
        """Call a Mistral-compatible chat endpoint. Returns parsed JSON dict or None on failure."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "You are an algorithmic trader. Current price is "
                        f"{price:.2f}. Reply STRICTLY with JSON of the form "
                        "{\"side\": \"buy|sell|hold\", \"quantity\": int}."
                    ),
                }
            ],
            "temperature": 0.2,
        }
        try:
            r = requests.post(MISTRAL_ENDPOINT, json=payload, timeout=5)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception:
            return None

    # ------------------------------------------------------------------
    def on_tick(self, price: float) -> List[Dict[str, Any]]:
        # Try the LLM first
        data = self._query_llm(price)
        if data:
            side = data.get("side", "hold").lower()
            qty = int(data.get("quantity", 0))
        else:
            # Fallback momentum: buy if price>last_price, sell if price<last_price
            if self.last_price is None:
                self.last_price = price
                return []
            side = "buy" if price > self.last_price else "sell" if price < self.last_price else "hold"
            qty = 2

        self.last_price = price

        if side == "hold" or qty <= 0:
            return []

        return [
            {
                "agent": self.name,
                "side": side,
                "price": price,
                "quantity": min(qty, 5),
            }
        ]
