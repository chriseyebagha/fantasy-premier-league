import requests
import pandas as pd
import json

BASE_URL = "https://fantasy.premierleague.com/api/"

def fetch_data():
    """Fetches the latest data from FPL API."""
    print("Fetching bootstrap-static...")
    bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
    
    # We need element summaries for detailed match data, but for the MVP 
    # and to avoid rate limits, we might start with just bootstrap data 
    # which contains 'form', 'now_cost', 'chance_of_playing', etc.
    # For 'upcoming fixture difficulty', bootstrap 'elements' has 'team' 
    # and 'fixtures' endpoint has difficulty.
    
    return bootstrap

def get_upcoming_fixtures():
    """Fetches all fixtures to determine difficulty."""
    print("Fetching fixtures...")
    fixtures = requests.get(BASE_URL + "fixtures/").json()
    return fixtures

def process_players(bootstrap_data, fixtures_data):
    """
    Processes raw data into a DataFrame with calculated prediction scores.
    """
    elements = bootstrap_data['elements']
    teams = bootstrap_data['teams']
    
    # Create a map of team id to team name and strength (if needed)
    team_map = {t['id']: t['name'] for t in teams}
    
    players = []
    
    # Helper to find next fixture difficulty for a team
    # This is a simplified lookup. In reality, we'd look at the next gameweek.
    # For MVP, let's assume the next available gameweek in the fixtures list.
    next_gw_fixtures = [f for f in fixtures_data if f['finished'] == False and f['event'] is not None]
    # Sort by event to get the very next one
    if next_gw_fixtures:
        next_event = next_gw_fixtures[0]['event']
        current_gw_fixtures = [f for f in next_gw_fixtures if f['event'] == next_event]
    else:
        current_gw_fixtures = []

    # Map team_id to difficulty
    team_difficulty = {}
    for f in current_gw_fixtures:
        team_difficulty[f['team_h']] = f['team_h_difficulty']
        team_difficulty[f['team_a']] = f['team_a_difficulty']

    for p in elements:
        # Filter unavailable players
        if p['status'] != 'a' and p['status'] != 'd': # 'a' = available, 'd' = doubtful
            continue

        # Filter low minutes (sample size too small)
        if p['minutes'] < 270:
            continue
            
        # Basic Stats
        try:
            xg = float(p.get('expected_goals_per_90', 0))
            xa = float(p.get('expected_assists_per_90', 0))
            form = float(p.get('form', 0))
            price = p['now_cost'] / 10.0
            position = p['element_type'] # 1=GK, 2=DEF, 3=MID, 4=FWD
            team_id = p['team']
            
            # Fixture Difficulty
            # Default to 3 (average) if no fixture found (e.g. blank gameweek)
            difficulty = team_difficulty.get(team_id, 3)
            
            # --- USE FPL'S OFFICIAL PREDICTION (ep_next) ---
            # This is FPL's own algorithm for predicting next gameweek points
            # It's already calibrated to realistic values (5-8 pts range)
            
            base_score = float(p.get('ep_next', 0))
            
            # Small fixture adjustment (optional, can be tweaked)
            # FPL's ep_next already accounts for fixtures, so we keep this minimal
            if position in [1, 2]:
                # Defenders: CS are very fixture-dependent
                if difficulty <= 2: multiplier = 1.15
                elif difficulty == 3: multiplier = 1.0
                elif difficulty == 4: multiplier = 0.9
                else: multiplier = 0.8
            else:
                # Attackers: less fixture-dependent
                if difficulty <= 2: multiplier = 1.1
                elif difficulty == 3: multiplier = 1.0
                else: multiplier = 0.95
            
            predicted_points = base_score * multiplier
            
            # Availability Penalty
            chance = p.get('chance_of_playing_next_round')
            if chance is not None:
                predicted_points = predicted_points * (float(chance) / 100.0)
            
            # Value Score
            value_score = predicted_points / price if price > 0 else 0
            
            players.append({
                'id': p['id'],
                'web_name': p['web_name'],
                'team': team_map.get(team_id, 'Unknown'),
                'position': position,
                'price': price,
                'form': form,
                'xg_90': xg,
                'xa_90': xa,
                'difficulty': difficulty,
                'predicted_points': round(predicted_points, 2),
                'value_score': round(value_score, 2),
                'status': p['status'],
                'chance_of_playing': p['chance_of_playing_next_round']
            })
            
        except (ValueError, TypeError):
            continue
            
    df = pd.DataFrame(players)
    return df

def get_ranked_players(position=None):
    """
    Orchestrates fetching and ranking.
    """
    bootstrap = fetch_data()
    fixtures = get_upcoming_fixtures()
    
    df = process_players(bootstrap, fixtures)
    
    if position:
        df = df[df['position'] == int(position)]
        
    # Sort by predicted points descending
    df = df.sort_values(by='predicted_points', ascending=False)
    
    # Replace NaN with None for valid JSON serialization
    # Must convert to object first to allow None in float columns
    df = df.astype(object).where(pd.notnull(df), None)
    
    return df.to_dict(orient='records')

if __name__ == "__main__":
    # Test run
    print("Running test prediction...")
    top_picks = get_ranked_players()
    print(f"Top 5 Overall: {top_picks[:5]}")
