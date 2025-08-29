import json
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

# Vercel Python function exporting a WSGI app named `app`
app = Flask(__name__)
CORS(app)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/ai_agents")
def get_ai_agents():
    # Resolve path to backend/open_router/ai_agents.json relative to this file
    backend_root = Path(__file__).resolve().parents[1]
    json_path = backend_root / "open_router" / "ai_agents.json"
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
        backend_root = Path(__file__).resolve().parents[1]
        data_dir = backend_root / "data"
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
