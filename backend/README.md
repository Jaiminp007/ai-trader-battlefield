# 🤖 AI Trading Battlefield - Market Simulation

A sophisticated real-time stock market simulation where AI-generated trading algorithms compete against each other in a realistic trading environment.

## 🏗️ System Architecture

The AI Trading Battlefield consists of several interconnected components:

```
📦 AI Trading Battlefield
├── 🧠 Algorithm Generation (open_router/)
│   ├── algo_gen.py          # Generates trading algorithms using LLMs
│   ├── model_fecthing.py    # Fetches available AI models
│   └── ai_agents.json       # Model configurations
├── 🏦 Market Simulation (market/)
│   ├── market_simulation.py # Main simulation orchestrator
│   ├── order_book.py        # Advanced order matching engine
│   ├── tick_generator.py    # Yahoo Finance data provider
│   ├── agent.py             # Trading agent management
│   └── __init__.py          # Module interface
├── 📁 Generated Algorithms (generate_algo/)
│   └── generated_algo_*.py  # AI-generated trading strategies
├── 📊 Data (data/)
│   └── stock_data.csv       # Historical market data
└── 🚀 main.py               # Application entry point
```

## ✨ Key Features

### 🔥 Real-Time Market Simulation
- **Yahoo Finance Integration**: Live market data for AAPL and other stocks
- **Professional Order Book**: Realistic bid/ask matching and trade execution
- **Multiple Agent Support**: Unlimited trading agents can compete simultaneously
- **Live Performance Tracking**: Real-time ROI calculations and leaderboards

### 🧠 AI Algorithm Generation
- **Multi-Model Support**: Integrates with OpenAI, Google, DeepSeek, Meta, and more
- **Automated Strategy Creation**: Generates sophisticated trading algorithms
- **Risk Management**: Built-in position sizing and risk controls
- **Strategy Diversity**: Momentum, mean reversion, market making, and custom strategies

### 📈 Advanced Market Features
- **Realistic Order Types**: Limit orders, market orders, and partial fills
- **Market Depth**: Full order book visibility with bid/ask spreads
- **Trade History**: Complete audit trail of all transactions
- **Portfolio Management**: Cash and stock position tracking per agent

### 🎮 Interactive Experience
- **30-Day Stock Charts**: Visual market analysis before simulation
- **Live Leaderboards**: Real-time performance rankings
- **Configurable Duration**: Adjustable simulation length
- **Hot-Plugging**: Add/remove agents during live simulation

## 🚀 Quick Start

### Option 1: Interactive Setup (Recommended)
```bash
cd backend
./run_simulation.sh
```
Follow the interactive menu to:
1. Run complete simulation
2. Market simulation only
3. Generate new algorithms
4. Show stock chart
5. Test system components

### Option 2: Direct Execution
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python main.py            # Run complete simulation
```

## 🔧 Installation

### Prerequisites
- Python 3.9+ 
- Internet connection (for Yahoo Finance data)
- OpenRouter API key (for algorithm generation)

### Setup Instructions

1. **Clone and Navigate**
   ```bash
   cd /Users/jaiminpatel/Documents/GitHub/ai-trader-battlefield/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key (Optional)**
   ```bash
   echo "OPENROUTER_API_KEY=your_key_here" > .env
   ```

## 🎯 Usage Examples

### Basic Market Simulation
```python
from market import MarketSimulation, YFinanceTickGenerator
from market.agent import create_sample_agents

# Create trading agents
agents = create_sample_agents()

# Initialize simulation
sim = MarketSimulation(agents)

# Run with real market data
tick_gen = YFinanceTickGenerator("AAPL")
results = sim.run(tick_gen.stream(), max_ticks=100)

# View results
print(f"Winner: {results['leaderboard'][0]['name']}")
```

### Custom Trading Agent
```python
from market.agent import BaseAgent

class MyTradingAgent(BaseAgent):
    def on_tick(self, price, current_tick, cash=0.0, stock=0):
        # Your trading logic here
        if price < 150:  # Buy if price drops below $150
            quantity = min(10, int(cash // price))
            if quantity > 0:
                return [{"agent": self.name, "side": "buy", 
                        "price": price, "quantity": quantity}]
        return []

# Add to simulation
agent = MyTradingAgent("MyAgent")
sim.add_agent_during_simulation(agent)
```

### Algorithm Generation
```python
from open_router.algo_gen import main as generate_algorithms

# Generate new trading algorithms
generate_algorithms()

# Algorithms will be saved to generate_algo/ directory
```

## 📊 Market Components

### Order Book Engine
- **Priority-based matching**: Price-time priority
- **Partial fills**: Orders can be partially executed
- **Market depth**: Real-time bid/ask levels
- **Trade reporting**: Complete execution details

### Trading Agents
- **RandomAgent**: Baseline random trading
- **MomentumAgent**: Trend-following strategy
- **MeanReversionAgent**: Contrarian approach
- **MarketMakerAgent**: Provides liquidity
- **AlgoAgent**: Wrapper for AI-generated strategies

### Data Provider
- **YFinanceTickGenerator**: Live market data
- **Historical replay**: Use past price data
- **Multiple timeframes**: 1m, 5m, 1h, 1d intervals
- **Multiple symbols**: AAPL, GOOGL, TSLA, etc.

## ⚙️ Configuration

### Simulation Settings
```python
from market.market_simulation import SimulationConfig

config = SimulationConfig(
    max_ticks=60,           # Number of price updates
    tick_sleep=1.0,         # Seconds between ticks
    log_trades=True,        # Show trade executions
    enable_order_book=True, # Use realistic matching
    initial_cash=10000.0    # Starting capital per agent
)

sim = MarketSimulation(agents, config)
```

### Agent Parameters
```python
# Customize agent behavior
momentum_agent = MomentumAgent(
    name="FastMomentum",
    lookback_period=3  # Look at last 3 price points
)

market_maker = MarketMakerAgent(
    name="TightSpreads",
    spread_bps=5.0,    # 0.05% bid-ask spread
    quantity=5         # 5 shares per order
)
```

## 📈 Performance Metrics

The system tracks comprehensive performance metrics:

- **ROI (Return on Investment)**: Percentage gain/loss
- **Total Portfolio Value**: Cash + stock holdings
- **Trade Count**: Number of executed transactions  
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest loss from peak

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'yfinance'**
```bash
source venv/bin/activate
pip install yfinance
```

**2. No generated algorithms found**
- Ensure OpenRouter API key is configured in `.env`
- Run algorithm generation: `python -c "from open_router.algo_gen import main; main()"`

**3. Chart display fails**
```bash
pip install matplotlib
# For headless systems: export MPLBACKEND=Agg
```

**4. Yahoo Finance connection errors**
- Check internet connection
- Try different time periods: `period="1d"` instead of `period="30d"`
- The system will fall back to dummy data if Yahoo Finance is unavailable

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run simulation with detailed logging
sim.run(ticks, log=True)
```

## 🏆 Battle Results

After each simulation, you'll see results like:

```
🏁 BATTLE RESULTS (sorted by ROI)
============================================
🏆 Winner: generated_algo_deepseek with ROI +15.32% and Final $11,532.00
2. MomentumFollower: ROI=+12.45% | Final=$11,245.00 (cash=$2,245.00, stock=45)
3. MarketMaker1: ROI=+8.90% | Final=$10,890.00 (cash=$890.00, stock=50)
4. RandomBaselineA: ROI=-2.15% | Final=$9,785.00 (cash=$785.00, stock=46)
```

## 🔮 Future Enhancements

- **Multi-asset trading**: Support for multiple stocks simultaneously
- **Advanced order types**: Stop-loss, take-profit, iceberg orders
- **Options and derivatives**: More complex financial instruments
- **Machine learning integration**: RL-based trading agents
- **Web interface**: Real-time browser-based monitoring
- **Database persistence**: Historical simulation storage
- **Paper trading**: Connect to real broker APIs for live paper trading

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Test your changes: `./run_simulation.sh` → option 5
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Yahoo Finance** for providing free market data
- **OpenRouter** for AI model access
- **Python Trading Community** for algorithmic trading inspiration
- **Contributors** who helped build this system

---

**Ready to start trading? Run `./run_simulation.sh` and let the battle begin!** 🚀
