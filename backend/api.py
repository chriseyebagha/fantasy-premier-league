from flask import Flask, jsonify, request
from flask_cors import CORS
import fpl_engine

app = Flask(__name__)
CORS(app)

# Cache data in memory for MVP (refresh on restart or add endpoint)
# In production, use a proper cache or database.
print("Initializing Data...")
# We can fetch on startup or on request. For speed on request, let's fetch now.
# But to avoid startup delay, maybe just let the first request trigger it 
# or use a global variable that updates periodically.
# For MVP, simple is best: fetch on request (with simple in-memory caching if needed later).

@app.route('/api/players', methods=['GET'])
def get_players():
    position = request.args.get('position')
    sort_by = request.args.get('sort_by', 'predicted_points') # 'predicted_points' or 'value_score'
    
    try:
        data = fpl_engine.get_ranked_players(position)
        
        # Sort if needed (engine defaults to predicted_points)
        if sort_by == 'value_score':
            data.sort(key=lambda x: x['value_score'], reverse=True)
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
