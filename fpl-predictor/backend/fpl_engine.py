import requests
import pandas as pd
import json
import numpy as np
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from prediction_tracker import PredictionTracker

# Initialize tracker
tracker = PredictionTracker()

BASE_URL = "https://fantasy.premierleague.com/api/"

# Cache for player summaries to avoid rate limits
player_summary_cache = {}

def fetch_data():
    """Fetches the latest data from FPL API."""
    print("Fetching bootstrap-static...")
    bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
    return bootstrap

def get_upcoming_fixtures():
    """Fetches all fixtures to determine difficulty."""
    print("Fetching fixtures...")
    fixtures = requests.get(BASE_URL + "fixtures/").json()
    return fixtures

@lru_cache(maxsize=500)
def fetch_element_summary(player_id: int) -> Dict:
    """
    Fetches detailed player history from FPL API.
    Cached to avoid rate limits.
    """
    if player_id in player_summary_cache:
        return player_summary_cache[player_id]
    
    try:
        url = f"{BASE_URL}element-summary/{player_id}/"
        response = requests.get(url)
        data = response.json()
        player_summary_cache[player_id] = data
        return data
    except Exception as e:
        print(f"Error fetching summary for player {player_id}: {e}")
        return {"history": [], "fixtures": [], "history_past": []}

def calculate_recent_form(player_history: List[Dict], num_matches: int = 6) -> Dict:
    """
    Analyzes recent performance over last N matches.
    Returns metrics for form, consistency, and trends.
    """
    if not player_history or len(player_history) == 0:
        return {
            "recent_avg_points": 0,
            "recent_minutes": [],
            "form_trend": "stable",
            "consistency": 0,
            "matches_analyzed": 0
        }
    
    # Get last N matches
    recent_matches = player_history[-num_matches:] if len(player_history) >= num_matches else player_history
    
    points = [m['total_points'] for m in recent_matches]
    minutes = [m['minutes'] for m in recent_matches]
    
    avg_points = np.mean(points) if points else 0
    consistency = np.std(points) if len(points) > 1 else 0
    
    # Determine trend (comparing first half vs second half)
    if len(points) >= 4:
        first_half_avg = np.mean(points[:len(points)//2])
        second_half_avg = np.mean(points[len(points)//2:])
        
        if second_half_avg > first_half_avg * 1.2:
            trend = "up"
        elif second_half_avg < first_half_avg * 0.8:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return {
        "recent_avg_points": round(avg_points, 2),
        "recent_minutes": minutes,
        "form_trend": trend,
        "consistency": round(consistency, 2),
        "matches_analyzed": len(recent_matches)
    }

def calculate_rotation_risk(player_minutes: List[int]) -> Dict:
    """
    Assesses rotation risk based on recent minutes played.
    Returns starting probability and 70+ minute probability.
    """
    if not player_minutes or len(player_minutes) == 0:
        return {
            "starting_probability": 0,
            "min_70_probability": 0,
            "rotation_risk": "high",
            "avg_minutes": 0
        }
    
    avg_minutes = np.mean(player_minutes)
    starts = sum(1 for m in player_minutes if m >= 85)  # Consider 85+ as a start
    min_70_count = sum(1 for m in player_minutes if m >= 70)
    
    starting_prob = (starts / len(player_minutes)) * 100
    min_70_prob = (min_70_count / len(player_minutes)) * 100
    
    # Determine risk level
    if avg_minutes >= 75 and starting_prob >= 70:
        risk = "low"
    elif avg_minutes >= 50 and starting_prob >= 40:
        risk = "medium"
    else:
        risk = "high"
    
    return {
        "starting_probability": round(starting_prob, 1),
        "min_70_probability": round(min_70_prob, 1),
        "rotation_risk": risk,
        "avg_minutes": round(avg_minutes, 1)
    }

def calculate_captain_score(player_data: Dict, player_history: List[Dict], fixtures_data: List[Dict]) -> Dict:
    """
    Multi-factor captain suitability score.
    Considers explosiveness, form, fixture, ownership, and position.
    """
    score = 0
    details = {}
    
    # 1. Historical explosiveness (double-digit hauls)
    if player_history:
        double_digit_hauls = sum(1 for m in player_history if m['total_points'] >= 10)
        high_scores = [m['total_points'] for m in player_history if m['total_points'] >= 10]
        
        explosiveness = np.std(high_scores) if len(high_scores) > 1 else 0
        
        details['double_digit_hauls'] = double_digit_hauls
        details['explosiveness'] = round(explosiveness, 2)
        
        # Weight: More hauls = better captain
        score += min(double_digit_hauls * 5, 25)  # Max 25 points
        score += min(explosiveness * 2, 15)  # Max 15 points
    
    # 2. Recent form
    form = float(player_data.get('form', 0))
    score += min(form * 3, 20)  # Max 20 points
    details['form_contribution'] = min(form * 3, 20)
    
    # 3. ICT Index (attacking threat)
    ep_next = float(player_data.get('ep_next', 0))
    score += min(ep_next * 2, 20)  # Max 20 points
    details['threat_contribution'] = min(ep_next * 2, 20)
    
    # 4. Position preference (strikers and mids preferred)
    position = player_data['element_type']
    if position == 4:  # Forward
        score += 15
    elif position == 3:  # Midfielder
        score += 10
    elif position == 2:  # Defender
        score += 5
    
    details['position_bonus'] = 15 if position == 4 else (10 if position == 3 else 5)
    
    # 5. Ownership (slightly prefer highly owned for safety, but not too much)
    ownership = float(player_data.get('selected_by_percent', 0))
    if 10 <= ownership <= 40:
        score += 10  # Sweet spot
    elif ownership > 40:
        score += 5   # Very popular
    else:
        score += 3   # Low owned
    
    details['ownership'] = ownership
    
    return {
        "captain_score": round(min(score, 100), 1),  # Cap at 100
        "details": details
    }

def calculate_joker_score(player_data: Dict, player_history: List[Dict]) -> Dict:
    """
    Identifies joker captain options using Bayesian-inspired probability approach.
    Two types of jokers:
    1. Low ownership differentials (<15%) with high potential
    2. High ownership low-cost (value) players with explosive potential
    
    Focus: Fixtures, explosiveness, and high probability to score big
    """
    score = 0
    details = {}
    
    ownership = float(player_data.get('selected_by_percent', 0))
    price = player_data['now_cost'] / 10.0
    position = player_data['element_type']
    
    # Filter: Only attackers (MID/FWD) are joker candidates
    if position not in [3, 4]:
        return {"joker_score": 0, "is_differential": False, "details": {}}
    
    # Determine joker type
    is_low_ownership_diff = ownership < 15
    is_value_explosive = (ownership > 15 and price < 8.5)  # High owned but cheap
    
    if not (is_low_ownership_diff or is_value_explosive):
        return {"joker_score": 0, "is_differential": False, "details": {}}
    
    details['joker_type'] = 'differential' if is_low_ownership_diff else 'value_explosive'
    details['ownership'] = ownership
    details['price'] = price
    
    # 1. Bayesian Prior: Historical explosiveness (double-digit hauls)
    if player_history:
        high_scores = [m['total_points'] for m in player_history if m['total_points'] >= 10]
        explosion_count = len(high_scores)
        explosion_rate = explosion_count / len(player_history) if player_history else 0
        
        # Bayesian update: prior belief + observed data
        # Higher explosion rate = higher prior probability of big haul
        prior_explosion_prob = min(explosion_rate * 100, 40)  # Max 40 points
        score += prior_explosion_prob
        
        details['explosion_rate'] = round(explosion_rate * 100, 1)
        details['hauls_count'] = explosion_count
    
    # 2. Underlying stats (Likelihood): xG + xA per 90
    xg_90 = float(player_data.get('expected_goals_per_90', 0))
    xa_90 = float(player_data.get('expected_assists_per_90', 0))
    underlying_score = (xg_90 + xa_90) * 15  # Max ~30 for elite players
    score += min(underlying_score, 30)
    details['underlying_stats'] = round(xg_90 + xa_90, 2)
    
    # 3. Recent form trajectory (Posterior update)
    if player_history:
        recent_form_data = calculate_recent_form(player_history, 6)
        avg_recent_points = recent_form_data['recent_avg_points']
        
        # Weight recent form heavily
        if recent_form_data['form_trend'] == 'up':
            score += 25  # Hot streak
        elif avg_recent_points > 5:
            score += 15  # Consistent
        elif recent_form_data['form_trend'] == 'stable':
            score += 10
        
        details['form_trend'] = recent_form_data['form_trend']
        details['recent_avg_points'] = avg_recent_points
    
    # 4. Fixture quality (Critical for explosiveness)
    # Easy fixtures = higher probability of big haul
    difficulty = player_data.get('difficulty', 3)
    if difficulty <= 2:
        score += 20  # Excellent fixture
    elif difficulty == 3:
        score += 10  # Average
    else:
        score += 0   # Hard fixture
    
    details['next_fixture_difficulty'] = difficulty
    
    # 5. ICT Index (Influence, Creativity, Threat)
    ict = float(player_data.get('ict_index', 0))
    ict_score = min(ict / 8, 15)  # Max 15
    score += ict_score
    
    # 6. Value bonus (for high-owned low-cost players)
    if is_value_explosive:
        # Bonus for being a "cheap" explosive option
        value_bonus = max(0, (8.5 - price) * 5)  # Up to 20 bonus
        score += value_bonus
        details['value_bonus'] = round(value_bonus, 1)
    
    # 7. Ownership penalty/bonus
    if is_low_ownership_diff:
        # Lower ownership = higher differential value
        ownership_bonus = max(0, (15 - ownership) * 1.5)
        score += ownership_bonus
        details['differential_bonus'] = round(ownership_bonus, 1)
    
    return {
        "joker_score": round(min(score, 100), 1),
        "is_differential": is_low_ownership_diff or is_value_explosive,
        "details": details
    }

def calculate_explosivity_index(player_data: Dict, player_history: List[Dict], all_starters: List[Dict]) -> Dict:
    """
    Bayesian explosivity index - measures haul potential (0-100).
    Current season only, 60+ min starters for benchmarks.
    """
    import numpy as np
    
    position = player_data['element_type']
    
    # Bayesian priors for haul rate by position (starters only)
    priors = {1: (0.5, 9.5), 2: (1.0, 9.0), 3: (2.5, 7.5), 4: (3.5, 6.5)}
    α, β = priors.get(position, (1.0, 9.0))
    
    # Count hauls (10+ pts) current season
    hauls = sum(1 for gw in player_history if gw.get('total_points', 0) >= 10)
    non_hauls = len(player_history) - hauls if player_history else 0
    
    α_post = α + hauls
    β_post = β + non_hauls
    haul_prob = α_post / (α_post + β_post)
    haul_uncertainty = np.sqrt(α_post * β_post / ((α_post + β_post)**2 * (α_post + β_post + 1)))
    
    # 2. UNDERLYING STATS (Position-specific percentile among starters)
    pos_starters = [p for p in all_starters if p['element_type'] == position]
    
    if position == 2:  # DEFENDERS: Clean sheets + Attacking threat + BPS
        # Clean sheet component (xGC - lower is better)
        xgc = float(player_data.get('expected_goals_conceded_per_90', 1.5))
        # Normalize: 0 xGC = 100, 2+ xGC = 0
        clean_sheet_score = max(0, min(100, (2.0 - xgc) / 2.0 * 100))
        
        # Attacking threat for full-backs
        xg90 = float(player_data.get('expected_goals_per_90', 0))
        xa90 = float(player_data.get('expected_assists_per_90', 0))
        attacking_score = min(100, (xg90 + xa90) * 80)  # Scale up for defenders
        
        # BPS (bonus point system) - defenders with high BPS are explosive
        ict = float(player_data.get('ict_index', 0))
        bps_score = min(100, ict / 10)  # ICT index as proxy for BPS potential
        
        # Defensive Actions Bonus (User Request: 10+ actions = +2 pts)
        def_bonus_score = 0
        if player_history:
            recent_matches = player_history[-5:]
            for match in recent_matches:
                # Calculate defensive contributions
                def_con = match.get('defensive_contribution', 0)
                if def_con == 0:
                    def_con = (
                        match.get('recoveries', 0) + 
                        match.get('clearances_blocks_interceptions', 0) + 
                        match.get('tackles', 0)
                    )
                
                if def_con >= 10:
                    def_bonus_score += 20  # Significant boost to underlying component
        
        # Weighted combination for defenders
        underlying_score = (
            clean_sheet_score * 0.40 +   # 40% - Clean sheet potential
            attacking_score * 0.30 +      # 30% - Attacking returns
            bps_score * 0.20 +            # 20% - General BPS
            min(100, def_bonus_score) * 0.10 # 10% - High defensive work rate bonus
        )
        # Allow bonus to push score higher if it's really high
        if def_bonus_score > 0:
            underlying_score += (def_bonus_score * 0.5) # Add raw bonus on top
        
        underlying_score = min(100, underlying_score)
    
    elif position == 1:  # GOALKEEPERS: Clean sheets + Saves
        xgc = float(player_data.get('expected_goals_conceded_per_90', 1.5))
        clean_sheet_score = max(0, min(100, (2.0 - xgc) / 2.0 * 100))
        
        # Saves (use ICT as proxy)
        ict = float(player_data.get('ict_index', 0))
        saves_score = min(100, ict / 8)
        
        underlying_score = (
            clean_sheet_score * 0.70 +
            saves_score * 0.30
        )
    
    else:  # MIDFIELDERS & FORWARDS: Pure attacking stats
        xg90 = float(player_data.get('expected_goals_per_90', 0))
        xa90 = float(player_data.get('expected_assists_per_90', 0))
        combined = xg90 + xa90
        
        if pos_starters:
            vals = sorted([float(p.get('expected_goals_per_90', 0)) + float(p.get('expected_assists_per_90', 0)) for p in pos_starters])
            underlying_score = (sum(1 for v in vals if v < combined) / len(vals) * 100) if vals else 50
        else:
            underlying_score = 50
    
    # Recent form (last 5, exponential decay)
    if player_history:
        pts = [gw.get('total_points', 0) for gw in player_history[:5]]
        if pts:
            weights = np.exp(-0.3 * np.arange(len(pts)))
            form = min(100, (np.average(pts, weights=weights) / 15) * 100)
        else:
            form = 50
    else:
        form = 50
    
    # Fixture multiplier
    diff = player_data.get('difficulty', 3)
    fix_mult = {1: 1.4, 2: 1.2, 3: 1.0, 4: 0.85, 5: 0.7}.get(diff, 1.0)
    
    # Team reliance (ICT proxy)
    ict = float(player_data.get('ict_index', 0))
    team_s = [p for p in all_starters if p.get('team') == player_data.get('team')]
    if team_s:
        team_ict = sum(float(p.get('ict_index', 0)) for p in team_s)
        reliance = min(30, (ict / team_ict * 300)) if team_ict > 0 else 0
    else:
        reliance = 0
    
    # Weighted combination
    base = haul_prob * 100 * 0.35 + underlying_score * 0.30 + form * 0.25 + reliance * 0.10
    adjusted = base * fix_mult
    explosivity = min(100, adjusted + haul_uncertainty * 40)
    
    return {
        "explosivity_index": round(explosivity, 1),
        "haul_probability": round(haul_prob * 100, 1),
        "hauls_this_season": hauls
    }

def predict_price_rise(player_data: Dict, player_history: List[Dict]) -> Dict:
    """
    Predicts likelihood of price rise based on transfer trends.
    """
    # Get recent transfer data from last 3 gameweeks
    if not player_history or len(player_history) < 3:
        return {
            "price_rise_probability": 0,
            "net_transfers": 0,
            "transfer_trend": "stable"
        }
    
    recent_matches = player_history[-3:]
    
    net_transfers = []
    for match in recent_matches:
        transfers_in = match.get('transfers_in', 0)
        transfers_out = match.get('transfers_out', 0)
        net_transfers.append(transfers_in - transfers_out)
    
    total_net = sum(net_transfers)
    avg_net = np.mean(net_transfers)
    
    # Determine trend
    if all(nt > 0 for nt in net_transfers):
        trend = "rising"
    elif all(nt < 0 for nt in net_transfers):
        trend = "falling"
    else:
        trend = "stable"
    
    # Calculate probability (simplified model)
    # Positive sustained transfers = higher probability
    probability = 0
    if total_net > 100000:
        probability = 80
    elif total_net > 50000:
        probability = 60
    elif total_net > 20000:
        probability = 40
    elif total_net > 0:
        probability = 20
    else:
        probability = 0
    
    return {
        "price_rise_probability": probability,
        "net_transfers": total_net,
        "transfer_trend": trend
    }

def analyze_fixture_run(player_team_id: int, fixtures_data: List[Dict], num_gameweeks: int = 4) -> Dict:
    """
    Analyzes next N gameweeks for fixture difficulty and value.
    """
    # Get next upcoming fixtures for player's team
    upcoming = [f for f in fixtures_data if not f['finished'] and f['event'] is not None]
    upcoming.sort(key=lambda x: x['event'])
    
    # Filter for player's team
    team_fixtures = [
        f for f in upcoming 
        if f['team_h'] == player_team_id or f['team_a'] == player_team_id
    ][:num_gameweeks]
    
    if not team_fixtures:
        return {
            "fixture_run_difficulty": 3,
            "fixtures_analyzed": 0,
            "difficulty_rating": "average"
        }
    
    # Calculate average difficulty
    difficulties = []
    for f in team_fixtures:
        if f['team_h'] == player_team_id:
            difficulties.append(f['team_h_difficulty'])
        else:
            difficulties.append(f['team_a_difficulty'])
    
    avg_difficulty = np.mean(difficulties)
    
    # Rating
    if avg_difficulty <= 2.5:
        rating = "excellent"
    elif avg_difficulty <= 3.0:
        rating = "good"
    elif avg_difficulty <= 3.5:
        rating = "average"
    else:
        rating = "difficult"
    
    return {
        "fixture_run_difficulty": round(avg_difficulty, 2),
        "fixtures_analyzed": len(team_fixtures),
        "difficulty_rating": rating
    }

def process_players(bootstrap_data, fixtures_data, include_extended_stats=False):
    """
    Processes raw data into a DataFrame with calculated prediction scores.
    If include_extended_stats=True, fetches detailed player history (slower but more comprehensive).
    """
    elements = bootstrap_data['elements']
    teams = bootstrap_data['teams']
    
    # Create a map of team id to team name
    team_map = {t['id']: t['name'] for t in teams}
    
    players = []
    
    # Get next gameweek fixtures
    next_gw_fixtures = [f for f in fixtures_data if f['finished'] == False and f['event'] is not None]
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

    print(f"Processing {len(elements)} players...")
    
    for idx, p in enumerate(elements):
        # Filter unavailable players
        if p['status'] not in ['a', 'd']:  # 'a' = available, 'd' = doubtful
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
            position = p['element_type']  # 1=GK, 2=DEF, 3=MID, 4=FWD
            team_id = p['team']
            
            # Fixture Difficulty
            difficulty = team_difficulty.get(team_id, 3)
            
            # Base prediction score (FPL's own algorithm)
            base_score = float(p.get('ep_next', 0))
            
            # Small fixture adjustment
            if position in [1, 2]:
                if difficulty <= 2: multiplier = 1.15
                elif difficulty == 3: multiplier = 1.0
                elif difficulty == 4: multiplier = 0.9
                else: multiplier = 0.8
            else:
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
            
            # Handle NaN values for JSON serialization
            chance_val = p.get('chance_of_playing_next_round')
            if chance_val is not None and (isinstance(chance_val, float) and np.isnan(chance_val)):
                chance_val = None
            
            player_dict = {
                'id': p['id'],
                'code': p['code'],  # For player photos
                'web_name': p['web_name'],
                'team': team_map.get(team_id, 'Unknown'),
                'team_id': team_id,
                'position': position,
                'price': price,
                'form': form,
                'xg_90': xg,
                'xa_90': xa,
                'difficulty': difficulty,
                'predicted_points': round(predicted_points, 2),
                'value_score': round(value_score, 2),
                'status': p['status'],
                'chance_of_playing': chance_val,
                'ownership': float(p.get('selected_by_percent', 0)),
                'ict_index': float(p.get('ict_index', 0))
            }
            
            # Extended stats (requires individual API calls - use sparingly)
            if include_extended_stats:
                if idx % 50 == 0:
                    print(f"Processed {idx}/{len(elements)} players...")
                
                player_summary = fetch_element_summary(p['id'])
                player_history = player_summary.get('history', [])
                
                # Recent form (last 5 matches)
                form_data = calculate_recent_form(player_history, num_matches=5)
                player_dict['recent_avg_points'] = form_data['recent_avg_points']
                player_dict['recent_minutes'] = form_data['recent_minutes']
                player_dict['form_trend'] = form_data['form_trend']
                
                # Rotation risk
                rotation_data = calculate_rotation_risk(form_data['recent_minutes'])
                player_dict['starting_probability'] = rotation_data['starting_probability']
                player_dict['min_70_probability'] = rotation_data['min_70_probability']
                player_dict['rotation_risk'] = rotation_data['rotation_risk']
                player_dict['avg_minutes'] = rotation_data['avg_minutes']  # Add for explosivity filtering
                
                # Captain score
                captain_data = calculate_captain_score(p, player_history, fixtures_data)
                player_dict['captain_score'] = captain_data['captain_score']
                player_dict['double_digit_hauls'] = captain_data['details'].get('double_digit_hauls', 0)
                
                # Joker score
                joker_data = calculate_joker_score(p, player_history)
                player_dict['joker_score'] = joker_data['joker_score']
                player_dict['is_differential'] = joker_data['is_differential']
                
                # Explosivity index (for starters with 60+ min)
                # Calculate after we have all_starters list
                player_dict['_needs_explosivity'] = True  # Flag for second pass
                
                # Price rise prediction
                price_data = predict_price_rise(p, player_history)
                player_dict['price_rise_probability'] = price_data['price_rise_probability']
                player_dict['net_transfers'] = price_data['net_transfers']
                
                # Fixture run
                fixture_run = analyze_fixture_run(team_id, fixtures_data, 4)
                player_dict['fixture_run_difficulty'] = fixture_run['fixture_run_difficulty']
                player_dict['fixture_run_value'] = round(predicted_points / fixture_run['fixture_run_difficulty'], 2) if fixture_run['fixture_run_difficulty'] > 0 else 0
                
            players.append(player_dict)
            
        except (ValueError, TypeError) as e:
            print(f"Error processing player {p.get('web_name', 'Unknown')}: {e}")
            continue
    
    # Second pass: Calculate explosivity for starters (60+ min)
    if include_extended_stats:
        # Filter starters - use total minutes or avg check
        # Check if player has played at least 540 mins total (approximates 60+ avg over recent games)
        all_starters = []
        for p in players:
            # Use avg_minutes from rotation_risk if available
            avg_mins = p.get('avg_minutes', 0) if 'avg_minutes' in p else 0
            # Or check total minutes if available  
            if avg_mins == 0 and 'recent_minutes' in p:
                recent = p.get('recent_minutes', 0)
                if isinstance(recent, (int, float)):
                    avg_mins = recent
            
            if avg_mins >= 60:  # Average 60+ mins per game
                all_starters.append(p)
        
        for player in players:
            if player.get('_needs_explosivity'):
                # Check if this player is a starter
                avg_mins = player.get('avg_minutes', 0) if 'avg_minutes' in player else 0
                if avg_mins == 0 and 'recent_minutes' in player:
                    recent = player.get('recent_minutes', 0)
                    if isinstance(recent, (int, float)):
                        avg_mins = recent
                
                if avg_mins >= 60 and len(all_starters) > 0:
                    # Get player's history again for explosivity calculation
                    try:
                        player_id = player['id']
                        player_summary = fetch_element_summary(player_id)
                        player_history = player_summary.get('history', [])
                        
                        # Find original player data from elements
                        orig_player = next((p for p in elements if p['id'] == player_id), None)
                        
                        if orig_player and player_history:
                            # Build all_starters_elements from elements (not player dicts)
                            starter_ids = [p['id'] for p in all_starters]
                            all_starters_elements = [e for e in elements if e['id'] in starter_ids]
                            
                            explosivity_data = calculate_explosivity_index(orig_player, player_history, all_starters_elements)
                            player['explosivity_index'] = explosivity_data['explosivity_index']
                            player['haul_probability'] = explosivity_data['haul_probability']
                            player['hauls_this_season'] = explosivity_data['hauls_this_season']
                        else:
                            player['explosivity_index'] = 0
                            player['haul_probability'] = 0
                            player['hauls_this_season'] = 0
                    except Exception as e:
                        print(f"Error calculating explosivity for {player.get('web_name')}: {e}")
                        player['explosivity_index'] = 0
                        player['haul_probability'] = 0
                        player['hauls_this_season'] = 0
                else:
                    # Not a starter - set to 0
                    player['explosivity_index'] = 0
                    player['haul_probability'] = 0
                    player['hauls_this_season'] = 0
            
            # Clean up flag
            if '_needs_explosivity' in player:
                del player['_needs_explosivity']
            
    # Convert to DataFrame
    df = pd.DataFrame(players)
    
    # Update tracker if we have extended stats (meaning we have good predictions)
    if include_extended_stats:
        update_tracker_data(bootstrap_data, players)
        
    return df

def get_model_status():
    """Returns the current status of the prediction model."""
    return tracker.evaluate_performance()

def update_tracker_data(bootstrap, players):
    """Updates the prediction tracker with new predictions and actuals."""
    try:
        # Get gameweek info
        events = bootstrap.get('events', [])
        next_gw = next((e for e in events if e.get('is_next')), None)
        
        # 1. Save predictions for NEXT gameweek
        if next_gw:
            tracker.save_predictions(next_gw['id'], players)
            
    except Exception as e:
        print(f"Error updating tracker: {e}")

def get_ranked_players(position=None, include_extended=False):
    """
    Orchestrates fetching and ranking.
    """
    bootstrap = fetch_data()
    fixtures = get_upcoming_fixtures()
    
    df = process_players(bootstrap, fixtures, include_extended_stats=include_extended)
    
    if position:
        df = df[df['position'] == int(position)]
        
    # Sort by predicted points descending
    df = df.sort_values(by='predicted_points', ascending=False)
    
    # Replace NaN with None for valid JSON serialization
    df = df.astype(object).where(pd.notnull(df), None)
    
    return df.to_dict(orient='records')

def get_captain_recommendations(top_n=10):
    """
    Returns top captain options based on captain_score.
    """
    bootstrap = fetch_data()
    fixtures = get_upcoming_fixtures()
    
    df = process_players(bootstrap, fixtures, include_extended_stats=True)
    
    # Filter to only attackers (MID and FWD)
    df = df[df['position'].isin([3, 4])]
    
    # Sort by captain score
    df = df.sort_values(by='captain_score', ascending=False)
    
    # Replace NaN with None
    df = df.astype(object).where(pd.notnull(df), None)
    
    return df.head(top_n).to_dict(orient='records')

def get_joker_picks(top_n=5, max_ownership=100.0):
    """
    Returns differential captain options (jokers).
    """
    bootstrap = fetch_data()
    fixtures = get_upcoming_fixtures()
    
    df = process_players(bootstrap, fixtures, include_extended_stats=True)
    
    # Filter by ownership if specified
    if max_ownership < 100:
        df = df[df['ownership'] <= max_ownership]
    
    # Filter to decent explosivity (>30)
    df = df[df['explosivity_index'] > 30]
    
    # Sort by explosivity_index (descending)
    df = df.sort_values(by='explosivity_index', ascending=False)
    
    # Replace NaN with None
    df = df.astype(object).where(pd.notnull(df), None)
    
    return df.head(top_n).to_dict(orient='records')

if __name__ == "__main__":
    # Test run
    print("Running test prediction...")
    top_picks = get_ranked_players()
    print(f"\nTop 5 Overall: {top_picks[:5]}")
    
    print("\n\nTesting extended stats...")
    extended = get_ranked_players(include_extended=True)
    print(f"\nTop player with extended stats: {extended[0]}")
