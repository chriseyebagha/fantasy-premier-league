from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.engine.data_manager import FPLDataManager
from backend.engine.storage import EngineStorage
from backend.engine.trainer import modelTrainer
from backend.engine.commander import EngineCommander

app = Flask(__name__)
CORS(app)

# Initialize Engine components
storage = EngineStorage()
dm = FPLDataManager()
trainer = modelTrainer(storage)
commander = EngineCommander(dm, trainer)

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Returns the main dashboard data with squad and recommendations."""
    try:
        data = commander.get_top_15_players()
        starters = data['starters']
        bench = data['bench']
        
        recommendations = commander.get_tier_captains(starters + bench)
        
        return jsonify({
            "status": "online",
            "gameweek": dm.get_upcoming_gameweek(dm.get_bootstrap_static()),
            "squad": starters,
            "bench": bench,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"status": "offline", "error": str(e)}), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate_gameweek():
    """Endpoint for the RL loop to evaluate previous performance."""
    data = request.json
    gw = data.get('gameweek')
    actuals = data.get('actual_points') # {player_id: points}
    
    if not gw or not actuals:
        return jsonify({"error": "Missing gameweek or actuals"}), 400
        
    try:
        trainer.evaluate_performance(gw, actuals)
        trainer.train_on_feedback()
        return jsonify({"status": "RL loop triggered", "gameweek": gw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "version": "3.0-thinking-engine"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
