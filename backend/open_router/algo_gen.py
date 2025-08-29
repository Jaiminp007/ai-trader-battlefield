import os
import requests
import json
from dotenv import load_dotenv
import time
import hashlib
import random

# Import the main function from your model fetching script
from model_fecthing import get_models_to_use

# Load environment variables from a .env file
load_dotenv()

# --- 1. Configuration ---
API_KEY = os.getenv('OPENROUTER_API_KEY')
CHAT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generate_algo')

# Data directory for local CSVs
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def list_available_stocks(data_dir: str) -> list:
    """List available stock CSVs (filters *_data.csv) in the data directory."""
    try:
        files = [f for f in os.listdir(data_dir) if f.lower().endswith('_data.csv')]
        files.sort()
        return files
    except Exception:
        return []

def generate_algorithms_for_agents(selected_agents, ticker, progress_callback=None):
    """Generate algorithms for specific agents (API-driven)"""
    if not API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        return
    
    print(f"🎯 Generating algorithms for {len(selected_agents)} agents using {ticker} data")
    print(f"✅ Using {len(selected_agents)} models selected from frontend")
    
    # Use the selected agents directly (no interactive selection)
    models_to_use = selected_agents
    if not models_to_use:
        print("❌ No models provided for generation")
        return
    
    # Generate algorithm for each selected agent
    for i, agent_model in enumerate(selected_agents):
        try:
            if progress_callback:
                progress = 30 + (i * 5)  # 30-55% for algorithm generation
                progress_callback(progress, f"Generating algorithm {i+1}/6 using {agent_model}...")
            
            print(f"\n🔄 Generating algorithm {i+1}/6 using {agent_model}...")
            
            # Build prompt for this specific model and ticker
            # Load CSV preview for the selected ticker
            csv_path = os.path.join(DATA_DIR, f"{ticker}_data.csv")
            csv_preview = load_csv_preview(csv_path) if os.path.exists(csv_path) else ""
            prompt = build_generation_prompt(ticker, csv_preview)
            
            # Generate algorithm
            algorithm_code = generate_algorithm(agent_model, prompt)
            
            if algorithm_code:
                # Create output directory if it doesn't exist
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                
                # Save algorithm with model name (sanitize filename)
                safe_name = agent_model.replace('/', '_').replace('-', '_').replace(':', '_').replace('.', '_')
                filename = f"generated_algo_{safe_name}.py"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                with open(filepath, 'w') as f:
                    f.write(algorithm_code)
                
                print(f"✅ Saved: {filename}")
                print(f"📁 Path: {os.path.abspath(filepath)}")
            else:
                print(f"❌ Failed to generate algorithm for {agent_model}")
                
        except Exception as e:
            print(f"❌ Error generating algorithm for {agent_model}: {e}")
    
    if progress_callback:
        progress_callback(55, "All algorithms generated successfully!")
    
    print(f"\n🎉 Algorithm generation completed for {ticker}")

def select_stock_file() -> tuple:
    """Interactively ask the user to pick a stock CSV. Returns (ticker, filename, full_path)."""
    files = list_available_stocks(DATA_DIR)
    fallback_file = 'stock_data.csv'
    if not files:
        # Fallback to stock_data.csv if present
        if os.path.exists(os.path.join(DATA_DIR, fallback_file)):
            files = [fallback_file]
        else:
            print("❌ No stock CSVs found in data directory.")
            return None, None, None

    print("\n📂 Available stock datasets (backend/data/):")
    for idx, fname in enumerate(files, 1):
        print(f"  {idx}. {fname}")

    choice = input(f"Select a dataset by number (1-{len(files)}) or press Enter for 1: ").strip()

    selected = None
    if not choice:
        selected = files[0]
    else:
        try:
            idx = int(choice)
            if 1 <= idx <= len(files):
                selected = files[idx - 1]
        except ValueError:
            pass

    # Try matching by ticker symbol if numeric selection failed
    if selected is None:
        ticker_guess = choice.upper().replace('.CSV', '').replace('_DATA', '')
        match = next((f for f in files if f.upper().startswith(f"{ticker_guess}_")), None)
        if match:
            selected = match
        else:
            print("⚠️ Invalid selection. Defaulting to 1.")
            selected = files[0]

    ticker = selected.split('_')[0].upper()
    path = os.path.join(DATA_DIR, selected)
    return ticker, selected, path

def load_csv_preview(csv_path: str, max_rows: int = 200) -> str:
    """Return header + last max_rows of CSV to keep prompt size reasonable."""
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
        if not lines:
            return ""
        header = lines[0].strip()
        data_lines = [ln.strip() for ln in lines[1:] if ln.strip()]
        preview = data_lines[-max_rows:] if len(data_lines) > max_rows else data_lines
        out = [header] + preview
        return "\n".join(out)
    except Exception:
        return ""

def build_generation_prompt(ticker: str, csv_preview: str) -> str:
    """Build a dynamic prompt that instructs the model and includes selected stock context."""
    base = f"""
You are an expert quantitative trading algorithm developer. Your task is to write a Python function `execute_trade(ticker, cash_balance, shares_held)` that decides whether to BUY, SELL, or HOLD a stock based on its recent historical data. You must use the `yfinance` library to get the latest historical data for the given ticker.

**Function Signature:**
`def execute_trade(ticker: str, cash_balance: float, shares_held: int) -> str:`
2) Return ONLY: "BUY", "SELL", or "HOLD"
3) Output ONLY raw Python code - no markdown, comments, or explanations
4) MUST use yfinance to get REAL market data - NO fake prices or random numbers

CRITICAL ERROR PREVENTION RULES:
- ALWAYS use .flatten() when extracting numpy arrays from pandas DataFrames
- ALWAYS check array lengths before using np.convolve() or similar functions
- ALWAYS handle division by zero and NaN values
- ALWAYS use proper variable naming (no Unicode characters, consistent naming)
- ALWAYS validate data exists before performing calculations

MANDATORY MARKET DATA USAGE:
- Import yfinance as yf
- Download real market data for the selected ticker using the period/interval consistent with the chosen DATA PERIOD below. Examples: 5d/1m, 30d/15m, 60d/30m, 90d/1h. Always set progress=False.
- Use actual Close prices from the downloaded data with .flatten() method
- NO random.uniform(), NO fake prices, NO using cash_balance as price

MANDATORY UNIQUENESS RULES (choose ONE approach from each category):

STRATEGY TYPE (choose ONE):
- MEAN REVERSION: Buy when price drops below moving average, sell when above
- MOMENTUM: Buy when price is rising, sell when falling
- VOLATILITY: Buy during low volatility, sell during high volatility
- VOLUME-BASED: Use trading volume to confirm price movements
- TECHNICAL INDICATORS: RSI, MACD, Bollinger Bands, Stochastic, Williams %R
- PATTERN RECOGNITION: Support/resistance, breakouts, chart patterns
- TIME-BASED: Different strategies for different times of day
- RISK-ADJUSTED: Position sizing based on volatility or drawdown
- ARBITRAGE: Exploit price differences between time periods
- CONTRARIAN: Buy when others sell, sell when others buy

DATA PERIOD (choose ONE):
- SHORT-TERM: 5-10 days (intraday patterns)
- MEDIUM-TERM: 15-30 days (weekly patterns)
- LONG-TERM: 45-90 days (monthly patterns)
- MIXED: Combine multiple timeframes

INDICATOR COMBINATION (choose ONE):
- SINGLE INDICATOR: Use only one technical indicator
- DUAL CROSSOVER: Two moving averages or oscillators
- MULTI-FACTOR: Combine 3+ different indicators
- CUSTOM METRIC: Create your own unique calculation

THRESHOLD VALUES (choose ONE set):
- AGGRESSIVE: 0.001-0.005 (frequent trading)
- MODERATE: 0.005-0.015 (balanced approach)
- CONSERVATIVE: 0.015-0.030 (selective trading)
- ADAPTIVE: Dynamic thresholds based on market conditions

CACHE VARIABLE NAMES (MUST be unique):
- Use completely different variable names than other models
- Examples: _my_unique_cache, _strategy_data, _price_history, _market_cache, etc.
- NO generic names like _cache, _data, _df

TRADING LOGIC (choose ONE):
- ALWAYS BUY/SELL: Return BUY or SELL whenever conditions are met
- CONDITIONAL: Only trade when multiple conditions align
- PROBABILISTIC: Use probability-based decisions (but never random price data)
- THRESHOLD-BASED: Different thresholds for different market conditions

PORTFOLIO MANAGEMENT (choose ONE):
- AGGRESSIVE: Trade with most available cash/stock
- CONSERVATIVE: Trade small amounts, preserve capital
- BALANCED: Moderate position sizes
- ADAPTIVE: Adjust based on current portfolio value

EXAMPLE TEMPLATE (adapt but make it unique):
import yfinance as yf
import numpy as np

_unique_cache = {{}}

def execute_trade(ticker, cash_balance, shares_held):
    global _unique_cache

    # Get real market data
    if ticker not in _unique_cache:
        _unique_cache[ticker] = yf.download(ticker, period="5d", interval="1m", progress=False)

    df = _unique_cache.get(ticker)
    if df is None or len(df) < 20:
        return "HOLD"

    # Use REAL close prices with proper array handling
    close_prices = df['Close'].values.flatten()  # ALWAYS use .flatten()
    if len(close_prices) == 0:
        return "HOLD"
    
    current_price = float(close_prices[-1])

    # Example: Simple moving average with proper validation
    window = 10
    if len(close_prices) < window:
        return "HOLD"
    
    # Calculate moving average safely
    ma = np.mean(close_prices[-window:])
    
    # Safe comparison with NaN check
    if np.isnan(ma) or np.isnan(current_price):
        return "HOLD"
    
    # Your unique strategy here...
    return "HOLD"  # Replace with your logic

NOW CREATE A COMPLETELY UNIQUE ALGORITHM FOR TICKER {ticker}:
- Choose DIFFERENT combinations from each category above
- Use DIFFERENT mathematical formulas and calculations
- Implement DIFFERENT decision-making logic
- Make it AGGRESSIVE (return BUY/SELL 30-50% of the time)
- Use UNIQUE variable names and cache structures
- MUST use real market data from yfinance

CRITICAL IMPLEMENTATION REQUIREMENTS:
1. ALWAYS use close_prices = df['Close'].values.flatten() for price arrays
2. ALWAYS check if len(close_prices) >= required_length before calculations
3. ALWAYS handle NaN values: if np.isnan(value): return "HOLD"
4. ALWAYS handle division by zero: if denominator == 0: return "HOLD"
5. For np.convolve(): ensure input array is 1D and has sufficient length
6. For moving averages: use np.mean() instead of complex convolution when possible
7. Use consistent ASCII variable names (no Unicode characters)
8. Always validate data exists before mathematical operations

CONTEXT: Here is a preview of the local historical dataset for {ticker} (header + last rows) to help calibrate thresholds. Do NOT invent prices or rely on this as the data source; still fetch yfinance data for decisions.
"""
    if csv_preview:
        base += f"\n```\n{csv_preview}\n```\n"
    return base

def build_diversity_directives(model_id: str) -> str:
    """Create deterministic per-model directives to enforce diverse strategies."""
    # Deterministic seed from model_id
    seed_int = int(hashlib.md5(model_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed_int)

    strategy_types = [
        "MEAN REVERSION", "MOMENTUM", "VOLATILITY", "VOLUME-BASED",
        "TECHNICAL INDICATORS", "PATTERN RECOGNITION", "TIME-BASED",
        "RISK-ADJUSTED", "ARBITRAGE", "CONTRARIAN"
    ]
    data_periods = [
        ("SHORT-TERM", "5d", "1m"), ("SHORT-TERM", "10d", "1m"),
        ("MEDIUM-TERM", "30d", "15m"), ("MEDIUM-TERM", "45d", "30m"),
        ("LONG-TERM", "60d", "30m"), ("LONG-TERM", "90d", "1h"),
        ("MIXED", "30d", "15m")
    ]
    indicator_combo = ["SINGLE INDICATOR", "DUAL CROSSOVER", "MULTI-FACTOR", "CUSTOM METRIC"]
    thresholds = ["AGGRESSIVE", "MODERATE", "CONSERVATIVE", "ADAPTIVE"]
    logic_types = ["ALWAYS BUY/SELL", "CONDITIONAL", "PROBABILISTIC", "THRESHOLD-BASED"]
    portfolio_styles = ["AGGRESSIVE", "CONSERVATIVE", "BALANCED", "ADAPTIVE"]

    strat = rng.choice(strategy_types)
    period_label, period_val, interval_val = rng.choice(data_periods)
    combo = rng.choice(indicator_combo)
    thresh = rng.choice(thresholds)
    logic = rng.choice(logic_types)
    port = rng.choice(portfolio_styles)

    # Unique variable prefix and cache name
    var_prefix = f"v{hashlib.md5((model_id+'-vars').encode()).hexdigest()[:6]}_"
    cache_name = f"_{var_prefix}cache"

    # Build explicit directives
    dir_text = f"""

MANDATORY PER-MODEL DIRECTIVES (for model: {model_id}):
- You MUST implement STRATEGY TYPE = {strat}
- You MUST implement DATA PERIOD = {period_label} using yf.download(..., period="{period_val}", interval="{interval_val}")
- You MUST implement INDICATOR COMBINATION = {combo}
- You MUST implement THRESHOLD VALUES = {thresh}
- You MUST implement TRADING LOGIC = {logic}
- You MUST implement PORTFOLIO MANAGEMENT = {port}
- You MUST use a UNIQUE cache variable named exactly: {cache_name}
- You MUST use unique variable names prefixed with: {var_prefix}
- You MUST return BUY/SELL in roughly 30-50% of calls (be actionable, not overly conservative)
"""
    return dir_text

# --- 2. Core Algorithm Generation Functions ---

def generate_algorithm(model_id, prompt_text: str):
    """Sends the generation prompt to a specific model and returns its response."""
    print(f"\n--- Generating algorithm with: {model_id} ---")
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": model_id, "messages": [{"role": "user", "content": prompt_text}]}
    try:
        response = requests.post(CHAT_API_URL, headers=headers, json=data, timeout=180)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()
        
        # Clean up code blocks
        if content.startswith("```python"):
            content = content[9:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        print(f"✅ SUCCESS: Code received from {model_id}.")
        return content
    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED to get code from {model_id}.\n   Error: {e}")
        return None
    except (KeyError, IndexError):
        print(f"❌ FAILED to parse response from {model_id}.")
        return None

def save_algorithm_to_file(code, model_name):
    """Saves the generated code to a uniquely named file."""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        # Sanitize the model name to create a valid filename (e.g., replace '/' with '_')
        safe_filename = model_name.replace('/', '_')
        output_path = os.path.join(OUTPUT_DIR, f'generated_algo_{safe_filename}.py')
        
        with open(output_path, 'w') as f:
            f.write(code)
        print(f"✅ Algorithm successfully saved to: {os.path.abspath(output_path)}")
    except IOError as e:
        print(f"❌ FAILED to save algorithm for {model_name}.\n   Error: {e}")

# --- 3. Main Execution ---

def main():
    """Main function to orchestrate the entire process."""
    print("--- Starting Algorithm Generation Process ---")
    # Step 1: Run the model fetching and testing process to get the list of models.
    generator_models = get_models_to_use()
    
    # Step 2: Check if a list of models was successfully returned.
    if not generator_models:
        print("\nHalting execution as no models were selected from the testing phase.")
        return None
        
    print(f"\n--- Starting Generation for {len(generator_models)} Models ---")

    # Step 2b: Ask the user which stock dataset to use as context
    ticker, filename, csv_path = select_stock_file()
    if ticker and csv_path:
        csv_preview = load_csv_preview(csv_path, max_rows=200)
        print(f"📌 Using dataset: {filename} (ticker {ticker}) for prompt context")
    else:
        ticker = "AAPL"
        csv_preview = ""
        print("⚠️ Proceeding without local CSV context; defaulting ticker to AAPL for prompt.")

    base_prompt = build_generation_prompt(ticker, csv_preview)
    
    # Step 3: Loop through each selected model, generate, and save.
    for model in generator_models:
        per_model_prompt = base_prompt + build_diversity_directives(model)
        generated_code = generate_algorithm(model, per_model_prompt)
        if generated_code:
            save_algorithm_to_file(generated_code, model)
        # Add a small delay to be respectful to the API
        time.sleep(2)
    
    print("\n--- All generation tasks completed. ---")
    return ticker


if __name__ == "__main__":
    main()