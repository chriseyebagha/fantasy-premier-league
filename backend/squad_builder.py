"""
Squad Builder Module for FPL Predictor
Builds optimal 15-man squads with formation optimization
"""

import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
from backend.engine.data_manager import FPLDataManager
from backend.engine.commander import EngineCommander

# Formation configurations: (GK, DEF, MID, FWD)
# Constraints: 3-5 DEF, 2-5 MID, 1-3 FWD, always 1 GK
FORMATIONS = {
    "3-4-3": (1, 3, 4, 3),
    "3-5-2": (1, 3, 5, 2),
    "4-4-2": (1, 4, 4, 2),
    "4-3-3": (1, 4, 3, 3),
    "4-5-1": (1, 4, 5, 1),
    "5-3-2": (1, 5, 3, 2),
    "5-2-3": (1, 5, 2, 3),
    "5-4-1": (1, 5, 4, 1),
}

# Squad requirements
SQUAD_SIZE = 15
BENCH_SIZE = 4  # 1 GK + 3 outfield
MAX_PLAYERS_PER_TEAM = 3
TOTAL_BUDGET = 100.0

def build_optimal_squad(dm: FPLDataManager, commander: EngineCommander, budget: float = TOTAL_BUDGET) -> Dict:
    """
    Main entry point for squad building.
    Returns optimal 15-man squad with formation and players using Engine predictions.
    """
    print("Building optimal squad with Thinking Engine metrics...")
    
    # 1. Get predictions from the Thinking Engine
    # get_top_15_players actually processes ~120 candidates
    # We'll use the processed results which already have predicted_points and features
    engine_results = commander.get_top_15_players()
    
    # The EngineCommander returns only 15 players by default in get_top_15_players result
    # We need a wider pool for budget optimization. 
    # Let's modify commander slightly or just use its logic to get the full processed list.
    # For now, let's assume we want to optimize from the best candidates.
    
    # Actually, EngineCommander.get_top_15_players() returns only 15 players.
    # We need to process more players to find the best 15-man squad within budget.
    
    # Let's replicate the prediction logic or expose a method in EngineCommander
    # that returns all processed candidates.
    
    # Since I don't want to change EngineCommander.py too much right now, 
    # I'll use its internal logic to get a larger pool of predicted players.
    
    all_players = get_all_predicted_players(dm, commander)
    
    # Separate by position
    gk_pool = [p for p in all_players if p['position'] == 1]
    def_pool = [p for p in all_players if p['position'] == 2]
    mid_pool = [p for p in all_players if p['position'] == 3]
    fwd_pool = [p for p in all_players if p['position'] == 4]
    
    # Sort each pool by predicted points
    gk_pool.sort(key=lambda x: x['predicted_points'], reverse=True)
    def_pool.sort(key=lambda x: x['predicted_points'], reverse=True)
    mid_pool.sort(key=lambda x: x['predicted_points'], reverse=True)
    fwd_pool.sort(key=lambda x: x['predicted_points'], reverse=True)
    
    # Try each formation and find the best one
    best_formation = None
    best_squad = None
    best_points = 0
    
    # We need to reserve some budget for the bench
    # Cheapest players approx: GK (4.0), DEF (4.0), MID (4.5), FWD (4.5)
    # Average bench cost ~17.5m
    bench_reserve = 17.5
    starting_budget = budget - bench_reserve
    
    for formation_name, (gk, defs, mids, fwds) in FORMATIONS.items():
        result = select_starting_11(
            formation_name, gk, defs, mids, fwds,
            gk_pool, def_pool, mid_pool, fwd_pool,
            starting_budget
        )
        
        if result and result['total_predicted_points'] > best_points:
            best_points = result['total_predicted_points']
            best_formation = formation_name
            best_squad = result
    
    if not best_squad:
        # Retry with slightly more budget if possible
        best_squad = select_starting_11(
            "4-4-2", 1, 4, 4, 2,
            gk_pool, def_pool, mid_pool, fwd_pool,
            budget - 16.5 # Absolute minimum bench
        )
        best_formation = "4-4-2"
        
    if not best_squad:
        return {"error": "Could not build a valid squad within budget"}
    
    # Now fill the bench
    starting_11 = best_squad['players']
    remaining_budget = budget - best_squad['total_cost']
    
    bench = select_bench(
        starting_11, remaining_budget,
        gk_pool, def_pool, mid_pool, fwd_pool
    )
    
    return {
        "formation": best_formation,
        "starting_11": starting_11,
        "bench": bench,
        "total_cost": round(best_squad['total_cost'] + sum(p['price'] for p in bench), 1),
        "total_predicted_points": round(best_squad['total_predicted_points'], 2),
        "bench_predicted_points": round(sum(p['predicted_points'] for p in bench), 2)
    }

def get_all_predicted_players(dm: FPLDataManager, commander: EngineCommander) -> List[Dict]:
    """Helper to get predicted points for a larger pool of players."""
    import pandas as pd
    from backend.engine.feature_factory import FeatureFactory
    
    bootstrap = dm.get_bootstrap_static()
    players = bootstrap['elements']
    teams = {t['id']: t['name'] for t in bootstrap['teams']}
    
    fixtures = dm.get_fixtures()
    next_gw = dm.get_upcoming_gameweek(bootstrap)
    gw_fixtures = [f for f in fixtures if f['event'] == next_gw]
    
    team_diff = {}
    for f in gw_fixtures:
        team_diff[f['team_h']] = f['team_h_difficulty']
        team_diff[f['team_a']] = f['team_a_difficulty']

    # Process fewer candidates for stability (120 is plenty for a 15-man squad)
    candidates = sorted(players, key=lambda x: (float(x.get('form') or 0) * 1.5) + float(x.get('points_per_game') or 0), reverse=True)[:120]
    
    valid_players = []
    player_features = []

    for p in candidates:
        if p['status'] != 'a' and p['status'] != 'd': continue
        
        import time
        time.sleep(0.05) # Rate limit protection
        summary = dm.get_player_summary(p['id'])
        history = summary.get('history', [])
        last_5 = history[-5:] if history else []
        avg_minutes = sum(m['minutes'] for m in last_5) / len(last_5) if last_5 else 0
        
        # Chance of playing penalty
        chance = p.get('chance_of_playing_next_round')
        chance_mult = (float(chance) / 100.0) if chance is not None else 1.0
        
        diff = team_diff.get(p['team'], 3)
        features = FeatureFactory.prepare_features(p, history, diff, next_gw)
        
        player_features.append(features)
        valid_players.append({
            "p": p,
            "features": features,
            "diff": diff,
            "avg_minutes": avg_minutes,
            "chance_mult": chance_mult
        })

    if not valid_players: return []

    feature_df = pd.DataFrame(player_features)
    commander.trainer.load_model()
    predictions = commander.trainer.predict(feature_df)

    processed = []
    for i, item in enumerate(valid_players):
        p = item['p']
        fdr = item['diff']
        
        # Model Prediction
        # Model Prediction
        prediction = float(predictions[i])
        # performance_boost removed to match commander.py and prevent inflation
        
        fixture_multiplier = 1.0
        if fdr <= 2: fixture_multiplier = 1.15
        elif fdr >= 5: fixture_multiplier = 0.7
        elif fdr >= 4: fixture_multiplier = 0.85
        
        pos_bias = 1.05 if p['element_type'] in [3, 4] else 0.95
        
        final_score = round(prediction * fixture_multiplier * pos_bias * item['chance_mult'], 2)
        
        # Calculate a value score for bench selection
        price = p['now_cost'] / 10.0
        value_score = final_score / price if price > 0 else 0

        # Opponent name
        opponent_name = "???"
        venue = ""
        for f in gw_fixtures:
            if f['team_h'] == p['team']:
                opponent_name = teams.get(f['team_a'], "???")[:3].upper()
                venue = "(H)"
                break
            elif f['team_a'] == p['team']:
                opponent_name = teams.get(f['team_h'], "???")[:3].upper()
                venue = "(A)"
                break
        
        processed.append({
            "id": p['id'],
            "web_name": p['web_name'],
            "team": teams.get(p['team'], "Unknown"),
            "team_id": p['team'],
            "position": p['element_type'],
            "price": price,
            "predicted_points": final_score,
            "value_score": round(value_score, 2),
            "goals": p.get('goals_scored', 0),
            "assists": p.get('assists', 0),
            "xG": round(float(p.get('expected_goals', 0)), 2),
            "xA": round(float(p.get('expected_assists', 0)), 2),
            "avg_minutes": round(item['avg_minutes'], 1),
            "next_fixture": f"{opponent_name} {venue}",
            "next_fixture_difficulty": fdr,
            "explosivity": float(item['features'].get('explosivity', 0)),
            "ownership": float(item['features'].get('selected_by', 0)),
        })
    
    return processed

def select_starting_11(
    formation_name: str,
    num_gk: int, num_def: int, num_mid: int, num_fwd: int,
    gk_pool: List[Dict], def_pool: List[Dict], 
    mid_pool: List[Dict], fwd_pool: List[Dict],
    budget: float
) -> Dict:
    selected = []
    total_cost = 0
    total_points = 0
    team_counts = defaultdict(int)
    
    # 1. Mandatory GK
    for p in gk_pool[:5]:
        if p['price'] <= (budget - total_cost) / (11 - len(selected)):
            selected.append(p)
            total_cost += p['price']
            total_points += p['predicted_points']
            team_counts[p['team_id']] += 1
            break
    
    if not selected: return None

    # 2. Fill positions with greedy approach
    for pos, count, pool in [(2, num_def, def_pool), (3, num_mid, mid_pool), (4, num_fwd, fwd_pool)]:
        pos_selected = 0
        for p in pool:
            if pos_selected >= count: break
            if team_counts[p['team_id']] < 3 and total_cost + p['price'] <= budget:
                selected.append(p)
                total_cost += p['price']
                total_points += p['predicted_points']
                team_counts[p['team_id']] += 1
                pos_selected += 1
        
        if pos_selected < count: return None

    return {
        "players": selected,
        "total_cost": round(total_cost, 1),
        "total_predicted_points": round(total_points, 2)
    }

def select_bench(
    starting_11: List[Dict],
    remaining_budget: float,
    gk_pool: List[Dict], def_pool: List[Dict],
    mid_pool: List[Dict], fwd_pool: List[Dict]
) -> List[Dict]:
    bench = []
    selected_ids = {p['id'] for p in starting_11}
    team_counts = defaultdict(int)
    for p in starting_11: team_counts[p['team_id']] += 1
    
    budget = remaining_budget
    
    # GK Bench
    for p in sorted(gk_pool, key=lambda x: x['price']):
        if p['id'] not in selected_ids and team_counts[p['team_id']] < 3 and p['price'] <= budget - 12.0: # leave room for 3 others
            bench.append(p)
            budget -= p['price']
            selected_ids.add(p['id'])
            team_counts[p['team_id']] += 1
            break
            
    # Outfield Bench (Cheapest possible to stay in budget, or best value if budget allows)
    outfield = sorted(def_pool + mid_pool + fwd_pool, key=lambda x: x['value_score'], reverse=True)
    for p in outfield:
        if len(bench) >= 4: break
        if p['id'] not in selected_ids and team_counts[p['team_id']] < 3 and p['price'] <= budget:
            bench.append(p)
            budget -= p['price']
            selected_ids.add(p['id'])
            team_counts[p['team_id']] += 1
            
    return bench

def get_squad_summary(squad: Dict) -> Dict:
    if 'error' in squad: return squad
    return {
        "formation": squad['formation'],
        "total_cost": squad['total_cost'],
        "starting_11_points": squad['total_predicted_points'],
        "bench_points": squad['bench_predicted_points'],
        "players": {
            "starting_11": squad['starting_11'],
            "bench": squad['bench']
        }
    }
