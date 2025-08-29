import os
import json
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# Health check
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

# Serve AI agents JSON from backend/open_router/ai_agents.json
@app.get("/api/ai_agents")
def get_ai_agents():
    json_path = Path(__file__).resolve().parent / "open_router" / "ai_agents.json"
    if not json_path.exists():
        return jsonify({"error": f"ai_agents.json not found at {str(json_path)}"}), 404
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/data_files")
def list_data_files():
    """List available stock CSVs in backend/data ending with *_data.csv"""
    try:
        data_dir = Path(__file__).resolve().parent / "data"
        if not data_dir.exists():
            return jsonify({"stocks": []})
        files = sorted([p.name for p in data_dir.glob("*_data.csv")])
        stocks = [{
            "ticker": name.replace("_data.csv", "").upper(),
            "filename": name
        } for name in files]
        return jsonify({"stocks": stocks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Store running simulations
running_simulations = {}

@app.post("/api/run")
def run_simulation():
    """Start a new simulation with selected agents and stock"""
    try:
        data = request.get_json()
        agents = data.get('agents', [])
        stock = data.get('stock', 'AAPL_data.csv')
        
        # Validate we have 6 agents
        if len(agents) != 6:
            return jsonify({"error": "Exactly 6 agents required"}), 400
            
        # Generate unique simulation ID
        sim_id = f"sim_{int(time.time())}"
        
        # Store simulation status
        running_simulations[sim_id] = {
            "status": "starting",
            "progress": 0,
            "results": None,
            "error": None
        }
        
        # Start simulation in background thread
        thread = threading.Thread(
            target=run_simulation_background,
            args=(sim_id, agents, stock)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "simulation_id": sim_id,
            "status": "started",
            "message": "Simulation started successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/simulation/<sim_id>")
def get_simulation_status(sim_id):
    """Get status of a running simulation"""
    if sim_id not in running_simulations:
        return jsonify({"error": "Simulation not found"}), 404
        
    return jsonify(running_simulations[sim_id])

def run_simulation_background(sim_id, agents, stock_file):
    """Run the simulation in background thread"""
    try:
        running_simulations[sim_id]["status"] = "running"
        running_simulations[sim_id]["progress"] = 10
        running_simulations[sim_id]["message"] = "Starting simulation..."
        
        # Import and run the main simulation logic
        from main import run_simulation_with_params
        
        # Extract ticker from filename
        ticker = stock_file.replace("_data.csv", "").upper()
        
        running_simulations[sim_id]["progress"] = 20
        running_simulations[sim_id]["message"] = f"Generating algorithms for {ticker}..."
        
        # Run the simulation with progress callback
        def progress_callback(progress, message):
            running_simulations[sim_id]["progress"] = progress
            running_simulations[sim_id]["message"] = message
        
        results = run_simulation_with_params(agents, ticker, progress_callback)
        
        running_simulations[sim_id]["status"] = "completed"
        running_simulations[sim_id]["progress"] = 100
        running_simulations[sim_id]["message"] = "Simulation completed!"
        running_simulations[sim_id]["results"] = results
        
    except Exception as e:
        running_simulations[sim_id]["status"] = "error"
        running_simulations[sim_id]["error"] = str(e)
        running_simulations[sim_id]["message"] = f"Error: {str(e)}"
        print(f"Simulation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
