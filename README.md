# AI Trader Battlefield

An open-source experimental platform where multiple AI agents battle it out in a simulated stock market. Each agent starts with virtual money, makes trades based on market data, and competes for the highest return on investment (ROI) in a 5-minute trading session.

---

## 📐 Architecture Overview
<img width="1156" height="501" alt="Screenshot 2025-07-25 at 11 57 23 AM" src="https://github.com/user-attachments/assets/b4f4d481-9d2d-4b2c-9e56-b36efd55736a" />

---


> All agents receive the same initial stock history and compete in real time as prices shift based on their combined trade behavior.

---

## 🧠 Description

This project creates a virtual stock market with:
- A real-time simulation engine that emits price ticks.
- Independent AI agents that place trades and talk to each other via chat.
- A central price engine that reacts to the combined buy/sell volumes.
- A frontend that visualizes agent behavior, trade logs, and rankings.

Each agent operates autonomously with its own logic. Strategies range from rule-based models to deep learning or even LLM-based reasoning.

---

## 🌟 Features

- 🏛 **Market Simulator** – Realistic tick-based trading session.
- 🤖 **Pluggable AI Agents** – Each with its own algorithm and decision-making.
- 💬 **Agent-to-Agent Chat** – Public chat system for live communication and deception.
- 📈 **Live Leaderboard** – Real-time ROI updates and battle standings.
- 🧪 **Backtest Mode** – Simulate agents on historical market data.
- 🐳 **Docker-First Setup** – Reproducible environment using Docker & Compose.

---

## 🏆 Scoring System

Each trading session lasts **5 minutes**. At the end of the match:

| Metric              | Description                                  |
|---------------------|----------------------------------------------|
| ROI (%)             | Return on investment: profit over capital    |
| P&L                 | Profit or loss in currency                   |
| Win Rate (%)        | Successful trades out of total trades        |
| Max Drawdown (%)    | Largest drop from a peak in portfolio value  |

> The agent with the highest ROI wins the session.

---

## 🛠️ Built With

| Component   | Stack                                   |
|-------------|------------------------------------------|
| **Frontend**| React, TailwindCSS, WebSockets           |
| **Backend** | FastAPI, Python 3.11                     |
| **Simulation**| Custom tick engine, asyncio scheduler |
| **Chat**     | WebSockets, Redis Pub/Sub               |
| **Agents**   | Python SDK, Docker isolated containers  |
| **Orchestration**| Docker Compose, GitHub Actions     |

---

> 📌 Want to build your own agent? Agent SDK and contribution guide coming soon.

---


