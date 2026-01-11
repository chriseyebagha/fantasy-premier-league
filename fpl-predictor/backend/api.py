from flask import Flask, jsonify, request
from flask_cors import CORS
import fpl_engine

app = Flask(__name__)
CORS(app)

@app.route('/api/players', methods=['GET'])
def get_players():
    """Basic players endpoint with standard analysis."""
    position = request.args.get('position')
    sort_by = request.args.get('sort_by', 'predicted_points')
    
    try:
        data = fpl_engine.get_ranked_players(position, include_extended=False)
        
        # Sort if needed
        if sort_by == 'value_score':
            data.sort(key=lambda x: x.get('value_score', 0), reverse=True)
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/players/extended', methods=['GET'])
def get_players_extended():
    """
    Enhanced players endpoint with all advanced metrics:
    - Rotation risk & starting probability
    - Captain score
    - Joker score  
    - Price rise probability
    - Fixture run analysis
    """
    position = request.args.get('position')
    sort_by = request.args.get('sort_by', 'predicted_points')
    limit = request.args.get('limit', type=int)
    
    try:
        data = fpl_engine.get_ranked_players(position, include_extended=True)
        
        # Sort options
        valid_sorts = ['predicted_points', 'value_score', 'captain_score', 
                      'joker_score', 'price_rise_probability', 'ownership']
        
        if sort_by in valid_sorts:
            data.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        
        # Limit results if specified
        if limit:
            data = data[:limit]
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/captains', methods=['GET'])
def get_captain_recommendations():
    """
    Returns top captain options ranked by captain_score.
    Includes explosiveness, fixture, ownership data.
    Query params:
    - top_n: number of captains to return (default 10)
    """
    top_n = request.args.get('top_n', default=10, type=int)
    
    try:
        captains = fpl_engine.get_captain_recommendations(top_n)
        return jsonify(captains)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jokers', methods=['GET'])
def get_joker_picks():
    """
    Returns differential captain options ranked by EXPLOSIVITY INDEX.
    Low ownership (<10%) + High explosivity potential.
    Query params:
    - top_n: number of jokers to return (default 10)
    """
    top_n = request.args.get('top_n', default=10, type=int)
    max_ownership = request.args.get('max_ownership', default=100.0, type=float)
    
    try:
        jokers = fpl_engine.get_joker_picks(top_n, max_ownership)
        return jsonify(jokers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/price-risers', methods=['GET'])
def get_price_risers():
    """
    Returns players most likely to rise in price.
    Sorted by price_rise_probability.
    Query params:
    - top_n: number of players to return (default 20)
    """
    top_n = request.args.get('top_n', default=20, type=int)
    
    try:
        # Get all players with extended stats
        data = fpl_engine.get_ranked_players(include_extended=True)
        
        # Sort by price rise probability
        data.sort(key=lambda x: x.get('price_rise_probability', 0), reverse=True)
        
        # Return top N
        return jsonify(data[:top_n])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "version": "2.0"})

@app.route('/api/model-status', methods=['GET'])
def get_model_status():
    """
    Returns the current status of the prediction model (RL feedback).
    """
    try:
        status = fpl_engine.get_model_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("FPL Predictor API v2.0")
    print("=" * 50)
    print("\nAvailable Endpoints:")
    print("  GET /api/players - Basic player analysis")
    print("  GET /api/players/extended - Advanced player analysis")
    print("  GET /api/captains - Captain recommendations")
    print("  GET /api/jokers - Differential captain picks")
    print("  GET /api/price-risers - Price rise predictions")
    print("  GET /api/health - Health check")
    print("\n" + "=" * 50)
    
    app.run(debug=True, port=5001)
