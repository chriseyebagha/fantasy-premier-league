import pandas as pd
from typing import Dict, List, Tuple
from backend.engine.data_manager import FPLDataManager
from backend.engine.feature_factory import FeatureFactory
from backend.engine.trainer import modelTrainer

class EngineCommander:
    """The 'Brain' that orchestrates predictions and selections."""
    
    def __init__(self, data_manager: FPLDataManager, trainer: modelTrainer):
        self.dm = data_manager
        self.trainer = trainer

    def get_top_15_players(self) -> Dict[str, List[Dict]]:
        """Returns the best 15 players separated into Starting XI and Bench."""
        bootstrap = self.dm.get_bootstrap_static()
        players = bootstrap['elements']
        teams = {t['id']: t['name'] for t in bootstrap['teams']}
        
        fixtures = self.dm.get_fixtures()
        next_gw = self.dm.get_upcoming_gameweek(bootstrap)
        gw_fixtures = [f for f in fixtures if f['event'] == next_gw]
        
        team_diff = {}
        for f in gw_fixtures:
            team_diff[f['team_h']] = f['team_h_difficulty']
            team_diff[f['team_a']] = f['team_a_difficulty']

        # 1. Performance-based Pre-filter (Top 120 players to minimize API calls)
        candidates = sorted(players, key=lambda x: (float(x.get('form') or 0) * 1.5) + float(x.get('points_per_game') or 0), reverse=True)[:120]
        
        valid_players = []
        player_features = []

        for p in candidates:
            if p['status'] != 'a': continue
            
            # Fetch Minutes History (Last 5 GWs)
            summary = self.dm.get_player_summary(p['id'])
            history = summary.get('history', [])
            last_5 = history[-5:] if history else []
            avg_minutes = sum(m['minutes'] for m in last_5) / len(last_5) if last_5 else 0
            
            # Prepare features
            diff = team_diff.get(p['team'], 3)
            features = FeatureFactory.prepare_features(p, history, diff)
            
            # Constraint: Must avg 65+ minutes to be a Starter candidate
            can_start = avg_minutes >= 65
            
            player_features.append(features)
            valid_players.append({
                "p": p,
                "features": features,
                "diff": diff,
                "avg_minutes": avg_minutes,
                "can_start": can_start
            })

        if not valid_players:
            return {"starters": [], "bench": []}

        # XGBoost Prediction
        feature_df = pd.DataFrame(player_features)
        self.trainer.load_model()
        predictions = self.trainer.predict(feature_df)

        processed = []
        for i, item in enumerate(valid_players):
            p = item['p']
            features = item['features']
            fdr = item['diff']
            
            # Map team ID to opponent name
            opponent_id = None
            is_home = False
            for f in gw_fixtures:
                if f['team_h'] == p['team']:
                    opponent_id = f['team_a']
                    is_home = True
                    break
                elif f['team_a'] == p['team']:
                    opponent_id = f['team_h']
                    is_home = False
                    break
            
            opponent_name = teams.get(opponent_id, "???")
            venue = "(H)" if is_home else "(A)"
            next_fix_str = f"{opponent_name[:3].upper()} {venue}"

            # Reality Score: Boost high-performing players, but penalize hard fixtures
            # 1. Base ML Prediction
            prediction = float(predictions[i])
            
            # 2. Performance Boost (Season-long reliability)
            performance_boost = (float(p.get('form') or 0) * 0.4) + (float(p.get('total_points') or 0) / 60.0)
            
            # 3. Fixture Adjustment (Boost easy, Penalize hard)
            fixture_multiplier = 1.0
            
            # Fixture-Proof Logic: Unified High Performance Indicator (Explosivity >= 70)
            explosivity = float(features.get('explosivity', 0))
            is_fixture_proof = explosivity >= 70
            
            if fdr <= 2: 
                fixture_multiplier = 1.15
            elif fdr >= 5: 
                fixture_multiplier = 0.8 if is_fixture_proof else 0.6
            elif fdr >= 4: 
                fixture_multiplier = 0.9 if is_fixture_proof else 0.75
            
            # 4. Position Bias (Favor MIDs and FWDs for explosivity)
            # 5% Premium for Attackers, 10% Discount for Defenders (Clean Sheet Risk is high)
            pos_bias = 1.05 if p['element_type'] in [3, 4] else 0.90
            
            final_score = round((prediction + performance_boost) * fixture_multiplier * pos_bias, 2)
            
            processed.append({
                "id": p['id'],
                "web_name": p['web_name'],
                "team": teams.get(p['team'], "Unknown"),
                "position": p['element_type'],
                "price": p['now_cost'] / 10.0,
                "predicted_points": final_score,
                "goals": p.get('goals_scored', 0),
                "assists": p.get('assists', 0),
                "xG": round(float(p.get('expected_goals', 0)), 2),
                "xA": round(float(p.get('expected_assists', 0)), 2),
                "avg_minutes": round(item['avg_minutes'], 1),
                "can_start": item['can_start'],
                "next_fixture": next_fix_str,
                "next_fixture_difficulty": fdr,
                "explosivity": float(features.get('explosivity', 0)),
                "defcon": float(features.get('defcon', 0)),
                "ownership": float(features.get('selected_by', 0)),
                "hauls": int(features.get('hauls', 0)),
            })

        # Final Selection: 11 Starters (filtered by minutes) + 4 Bench
        processed.sort(key=lambda x: x['predicted_points'], reverse=True)
        
        starters = []
        remaining = processed[:]
        
        # Formation Rules (Minima)
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        
        # 1. Fill mandatory minimum slots (MUST meet can_start trigger)
        for p in remaining[:]:
            if not p['can_start']: continue
            pos = p['position']
            if pos == 1 and counts[1] < 1:
                starters.append(p)
                remaining.remove(p)
                counts[1] += 1
            elif pos == 2 and counts[2] < 3:
                starters.append(p)
                remaining.remove(p)
                counts[2] += 1
            elif pos == 3 and counts[3] < 2:
                starters.append(p)
                remaining.remove(p)
                counts[3] += 1
            elif pos == 4 and counts[4] < 1:
                starters.append(p)
                remaining.remove(p)
                counts[4] += 1

        # 2. Fill remaining starter slots (Strategic Formation: Favor Attackers)
        # Rule: Only take a 4th/5th defender if they outscore the best available attacker by 0.8+ points
        max_counts = {1: 1, 2: 5, 3: 5, 4: 3}
        
        while len(starters) < 11 and remaining:
            # Separate remaining candidates into Def and Attack
            def_candidates = [p for p in remaining if p['position'] == 2 and counts[2] < max_counts[2] and p['can_start']]
            atk_candidates = [p for p in remaining if p['position'] in [3, 4] and counts[p['position']] < max_counts[p['position']] and p['can_start']]
            
            best_def = def_candidates[0] if def_candidates else None
            best_atk = atk_candidates[0] if atk_candidates else None
            
            if not best_def and not best_atk:
                # Fallback to any remaining player if no one meets can_start
                remaining.sort(key=lambda x: x['predicted_points'], reverse=True)
                p = remaining[0]
                starters.append(p)
                remaining.remove(p)
                counts[p['position']] += 1
                continue

            # Selection Logic:
            selected_p = None
            if best_def and not best_atk:
                selected_p = best_def
            elif best_atk and not best_def:
                selected_p = best_atk
            else:
                # Decider: 4th+ Defender must be 0.8 points better than best attacker
                is_defender_luxury = counts[2] >= 3
                if is_defender_luxury and (best_def['predicted_points'] < best_atk['predicted_points'] + 0.8):
                    selected_p = best_atk
                else:
                    selected_p = best_def if best_def['predicted_points'] > best_atk['predicted_points'] else best_atk

            starters.append(selected_p)
            remaining.remove(selected_p)
            counts[selected_p['position']] += 1

        # 3. Fill bench (remaining top players, min constraint does NOT apply to bench)
        remaining.sort(key=lambda x: x['predicted_points'], reverse=True)
        bench = remaining[:4]
        
        return {"starters": starters, "bench": bench}

    def get_tier_captains(self, squad: List[Dict]) -> Dict[str, Dict]:
        """Categorizes players into four tiers with strict position and explosivity rules."""
        if not squad:
            return {"easy_choice": {}, "obvious": {}, "joker": {}, "fun_one": {}, "weights": {}}

        # Explosivity Floor: A player must have >= 33 explosivity to be considered a captain
        EXPLOSIVITY_FLOOR = 33
        
        # Categorize candidates
        # Rule: Only MIDs (3) and FWDs (4) for Easy, Obvious, and Joker
        attacking_pool = [p for p in squad if p['position'] in [3, 4] and p['explosivity'] >= EXPLOSIVITY_FLOOR]
        # Rule: Only DEFs (2) and GKs (1) for The Fun One
        defensive_pool = [p for p in squad if p['position'] in [1, 2] and p['explosivity'] >= EXPLOSIVITY_FLOOR]
        
        # Fallback if no one meets the floor
        if not attacking_pool:
            attacking_pool = [p for p in squad if p['position'] in [3, 4]]
        if not defensive_pool:
            defensive_pool = [p for p in squad if p['position'] in [1, 2]]

        # 1. Easy Choice: Attacking player, High Ownership (>25%) AND high seasonal hauls (>4)
        easy_pool = [p for p in attacking_pool if p['ownership'] > 25 and p['hauls'] > 4]
        if not easy_pool:
            # Fallback to highest ownership attacking hauler
            easy_pool = [p for p in attacking_pool if p['hauls'] > 0]
            easy_pool.sort(key=lambda x: x['ownership'], reverse=True)
            easy_reason_meta = "highest ownership profile"
        else:
            easy_pool.sort(key=lambda x: (x['hauls'], x['ownership']), reverse=True)
            easy_reason_meta = f"{easy_pool[0]['hauls']} double-digit hauls"
            
        easy_choice = (easy_pool[0] if easy_pool else attacking_pool[0]).copy()
        easy_choice['reason'] = f"{easy_choice['web_name']} is the 'Easy Choice' based on {easy_reason_meta} and {easy_choice['ownership']}% ownership."

        # 2. Obvious: Highest Predicted Points among attacking pool
        attacking_pool.sort(key=lambda x: x['predicted_points'], reverse=True)
        obvious = (attacking_pool[0] if attacking_pool else squad[0]).copy()
        obvious['reason'] = f"The algorithm identifies {obvious['web_name']} as the most reliable pick with {obvious['predicted_points']} projected points."
        
        # 3. Joker: Highest Explosivity among low ownership attacking pool (<15%)
        joker_pool = [p for p in attacking_pool if p['ownership'] < 15]
        joker_pool.sort(key=lambda x: x['explosivity'], reverse=True)
        
        # If no one under 15% ownership, expand slightly or pick the best differential profile
        if not joker_pool:
            joker_pool = sorted(attacking_pool, key=lambda x: (x['ownership'], -x['explosivity']))
            
        joker = joker_pool[0].copy()
        
        if joker['ownership'] < 15:
            joker['reason'] = f"{joker['web_name']} offers high explosivity ({joker['explosivity']}) combined with low ownership ({joker['ownership']}%), a classic differential."
        else:
            joker['reason'] = f"{joker['web_name']} is selected as the best relative differential ({joker['ownership']}% ownership) with explosive potential."
        
        # 4. The Fun One: Best defensive attacking prospect (Defensive candidates with high Defcon)
        defensive_pool.sort(key=lambda x: x['defcon'], reverse=True)
        fun_one = (defensive_pool[0] if defensive_pool else squad[0]).copy()
        
        if fun_one['defcon'] > 70:
            fun_one['reason'] = f"Elite Defcon level ({fun_one['defcon']}): {fun_one['web_name']} is picked for their massive clean sheet bonus and offensive participation."
        else:
            fun_one['reason'] = f"The best defensive attacking prospect available, focusing on clean sheet security."
        
        return {
            "easy_choice": easy_choice,
            "obvious": obvious,
            "joker": joker,
            "fun_one": fun_one,
            # ...
            "weights": {
                "form_weight": 0.7,
                "fdr_weight": 0.5,
                "ict_weight": 0.3,
                "model_type": self.trainer.model_type
            }
        }
