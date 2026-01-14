import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from backend.engine.data_manager import FPLDataManager
from backend.engine.feature_factory import FeatureFactory
from backend.engine.trainer import modelTrainer

class EngineCommander:
    """The 'Brain' that orchestrates predictions and selections."""
    
    def __init__(self, data_manager: FPLDataManager, trainer: modelTrainer):
        self.dm = data_manager
        self.trainer = trainer

    def _get_rolling_team_stats(self, players: List[Dict], window: int = 7) -> Tuple[Dict[int, float], float]:
        """Calculates blended rolling Vulnerability Score (xGC + GC) per match for each team."""
        team_vulnerability = {}
        
        # Group defenders/keepers by team
        team_groups = {}
        for p in players:
            t_id = p['team']
            if t_id not in team_groups:
                team_groups[t_id] = []
            team_groups[t_id].append(p)
        
        # For each team, pick an anchor or ensemble to get the team's recent defensive stats
        for t_id, members in team_groups.items():
            gks = [p for p in members if p['element_type'] == 1]
            defs = [p for p in members if p['element_type'] == 2]
            candidates = sorted(gks + defs, key=lambda x: x.get('minutes', 0), reverse=True)[:3]
            
            if not candidates:
                team_vulnerability[t_id] = 1.5 # Default approx score
                continue
                
            gw_stats = {} # round -> (xgc, gc)
            for p in candidates:
                summary = self.dm.get_player_summary(p['id'])
                history = summary.get('history', [])
                for h in history:
                    gw = h.get('round')
                    xgc = float(h.get('expected_goals_conceded') or 0)
                    gc = float(h.get('goals_conceded') or 0)
                    
                    if gw not in gw_stats:
                        gw_stats[gw] = (xgc, gc)
                    else:
                        # Take max of candidates to represent the team (avoiding rotation bias)
                        curr_xgc, curr_gc = gw_stats[gw]
                        gw_stats[gw] = (max(curr_xgc, xgc), max(curr_gc, gc))
            
            recent_gws = sorted(gw_stats.keys(), reverse=True)[:window]
            recent_xgc = [gw_stats[gw][0] for gw in recent_gws]
            recent_gc = [gw_stats[gw][1] for gw in recent_gws]
            
            avg_xgc = sum(recent_xgc) / len(recent_xgc) if recent_xgc else 1.5
            avg_gc = sum(recent_gc) / len(recent_gc) if recent_gc else 1.5
            
            # Blended Vulnerability Score: 50% Process (xGC) + 50% Reality (GC)
            vulnerability_score = (avg_xgc * 0.5) + (avg_gc * 0.5)
            team_vulnerability[t_id] = round(vulnerability_score, 2)
            
        # Calculate 30th Percentile Threshold (Worst Defenses)
        sorted_values = sorted(team_vulnerability.values(), reverse=True)
        threshold_idx = min(5, len(sorted_values) - 1)
        leaky_threshold = sorted_values[threshold_idx] if sorted_values else 1.8
        
        # Log the rankings with breakdown for transparency
        sorted_rankings = sorted(team_vulnerability.items(), key=lambda x: x[1], reverse=True)
        print(f"\n🛡️  Rolling {window}-Game Blended Vulnerability Rankings (0.5*xGC + 0.5*GC):")
        print(f"📊  Leaky Defense Threshold (30th %ile): {leaky_threshold}")
        for i, (t_id, score) in enumerate(sorted_rankings):
            status = " [LEAKY]" if score >= leaky_threshold else ""
            print(f"  {i+1}. Team {t_id}: {score} score{status}")
            
        return team_vulnerability, leaky_threshold

    def get_top_15_players(self) -> Dict[str, List[Dict]]:
        """Returns the best 15 players separated into Starting XI and Bench."""
        bootstrap = self.dm.get_bootstrap_static()
        players = bootstrap['elements']
        teams = {t['id']: t['name'] for t in bootstrap['teams']}
        
        fixtures = self.dm.get_fixtures()
        next_gw = self.dm.get_upcoming_gameweek(bootstrap)
        gw_fixtures = [f for f in fixtures if f['event'] == next_gw]
        
        team_diff = {}
        # Calculate rolling team-level Vulnerability (Last 7 games)
        team_vulnerability, leaky_threshold = self._get_rolling_team_stats(players, window=7)

        for f in gw_fixtures:
            team_diff[f['team_h']] = f['team_h_difficulty']
            team_diff[f['team_a']] = f['team_a_difficulty']

        # 1. Performance-based Pre-filter (Top 120 players to minimize API calls)
        candidates = sorted(players, key=lambda x: (float(x.get('form') or 0) * 1.5) + float(x.get('points_per_game') or 0), reverse=True)[:120]
        
        valid_players = []
        player_features = []

        for p in candidates:
            if p['status'] != 'a': continue
            
            # Smarter Minutes Tracking: Don't penalize consistent starters for one-off rests (e.g. Christmas)
            summary = self.dm.get_player_summary(p['id'])
            history = summary.get('history', [])
            last_5 = history[-5:] if history else []
            appearances = [m['minutes'] for m in last_5 if m['minutes'] > 0]
            starts_last_5 = len(appearances)
            
            if starts_last_5 >= 3:
                # Consistent Starter: Use average of non-zero appearances
                avg_minutes = sum(appearances) / starts_last_5 if starts_last_5 > 0 else 0
            else:
                # Bench/Rotation player: Use raw average of last 5
                avg_minutes = sum(m['minutes'] for m in last_5) / len(last_5) if last_5 else 0
            
            # Prepare features
            diff = team_diff.get(p['team'], 3)
            
            # Map team ID to opponent ID
            opponent_id = None
            for f in gw_fixtures:
                if f['team_h'] == p['team']:
                    opponent_id = f['team_a']
                    break
                elif f['team_a'] == p['team']:
                    opponent_id = f['team_h']
                    break
            
            opp_vulnerability = team_vulnerability.get(opponent_id, 1.5) if opponent_id else 1.5 # Fallback to mid-range
            features = FeatureFactory.prepare_features(p, history, diff, next_gw, opp_vulnerability)
            
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

        # Multi-Target Probabilistic Prediction
        feature_df = pd.DataFrame(player_features)
        self.trainer.load_model()
        event_predictions = self.trainer.predict(feature_df)
        
        # Translate to Expected Points (xP) and Haul Probabilities
        positions = [item['p']['element_type'] for item in valid_players]
        xp_points = self.trainer.translate_to_xp(event_predictions, positions)
        
        # Calculate Vesuvius Multipliers (Booster Layer)
        # 1. Clinicality Boost: Based on seasonal haul frequency
        # 2. Vulnerability Boost: Based on opponent xGC
        haul_multipliers = np.ones(len(valid_players))
        for idx, item in enumerate(valid_players):
            p = item['p']
            features = item['features']
            
            # Clinicality: hauls / apps
            # We use 'hauls' from features and calculate apps from history
            summary = self.dm.get_player_summary(p['id'])
            history = summary.get('history', [])
            apps = len(history) if history else 1
            haul_freq = features.get('hauls', 0) / apps
            
            # Clinicality multiplier: 1.0 (0 hauls) to 1.15 (high frequency)
            clinicality_boost = 1.0 + (min(haul_freq, 0.4) * 0.375) # Max +15% boost
            
            # Matchup: opponent_vulnerability >= leaky_threshold indicates a leaking defense
            matchup_boost = 1.0
            if opp_vulnerability >= leaky_threshold:
                matchup_boost = 1.10 # +10% boost for leaking defense
                
            haul_multipliers[idx] = clinicality_boost * matchup_boost

        haul_probs = self.trainer.calculate_haul_probability(event_predictions, positions, haul_multipliers=haul_multipliers)

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

            # Reality Score: Now fully derived from the Probabilistic xP model
            final_score = float(xp_points[i])
            
            # Extract individual probabilities
            prob_goal = float(event_predictions['actual_goals'][i])
            prob_assist = float(event_predictions['actual_assists'][i])
            prob_cs = float(event_predictions['actual_clean_sheets'][i])
            prob_saves = float(event_predictions['actual_saves'][i])
            prob_bonus = float(event_predictions.get('actual_bonus', np.zeros(len(valid_players)))[i])
            prob_defcon = float(event_predictions.get('actual_defcon_points', np.zeros(len(valid_players)))[i])

            # 3. Probabilistic Reasoning & Vesuvius Alert
            reasoning = []
            haul_prob = float(haul_probs[i])
            haul_alert = haul_prob >= 0.20 # 20% chance of 11+ points is a major alert
            
            if haul_alert:
                reasoning.append(f"VESUVIUS ALERT: {haul_prob*100:.0f}% Haul Probability (11+ pts)")
            
            if prob_goal > 0.4: reasoning.append(f"High goal threat ({prob_goal:.1f} Exp)")
            if prob_assist > 0.4: reasoning.append(f"Playmaker potential ({prob_assist:.1f} Exp)")
            if prob_cs > 0.6: reasoning.append(f"Strong CS chance ({prob_cs*100:.0f}%)")
            
            # Refined Bonus vs Defcon logic
            if prob_bonus > 1.2: 
                reasoning.append(f"Bonus Magnet ({prob_bonus:.1f} Exp)")
            
            if prob_defcon > 0.4:
                # 0.4 probability of +2 points is significant
                reasoning.append(f"Defcon Point Threat (+2 chance: {prob_defcon*100/2:.0f}%)")
            
            if not reasoning:
                reasoning.append("Solid underlying metric coverage")

            processed.append({
                "id": p['id'],
                "web_name": p['web_name'],
                "team": teams.get(p['team'], "Unknown"),
                "position": p['element_type'],
                "price": p['now_cost'] / 10.0,
                "predicted_points": round(final_score, 2),
                "haul_prob": round(haul_prob, 2),
                "haul_alert": haul_alert,
                "prob_goal": round(prob_goal, 2),
                "prob_assist": round(prob_assist, 2),
                "prob_cs": round(prob_cs, 2),
                "prob_saves": round(prob_saves, 2),
                "prob_bonus": round(prob_bonus, 2),
                "prob_defcon": round(prob_defcon, 2),
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
                "reasoning": " | ".join(reasoning),
                "features": features # Essential for retraining
            })

        # Final Selection: 11 Starters (filtered by minutes) + 4 Bench
        # Constraint: Max 3 players from the same team
        processed.sort(key=lambda x: x['predicted_points'], reverse=True)
        
        starters = []
        remaining = processed[:]
        team_counts = {}
        
        # Formation Rules (Minima)
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        
        def can_add_team(team_name):
            return team_counts.get(team_name, 0) < 3

        # 1. Fill mandatory minimum slots
        for p in remaining[:]:
            if not p['can_start']: continue
            if not can_add_team(p['team']): continue
            
            pos = p['position']
            if pos == 1 and counts[1] < 1:
                starters.append(p)
                remaining.remove(p)
                counts[1] += 1
                team_counts[p['team']] = team_counts.get(p['team'], 0) + 1
            elif pos == 2 and counts[2] < 3:
                starters.append(p)
                remaining.remove(p)
                counts[2] += 1
                team_counts[p['team']] = team_counts.get(p['team'], 0) + 1
            elif pos == 3 and counts[3] < 2:
                starters.append(p)
                remaining.remove(p)
                counts[3] += 1
                team_counts[p['team']] = team_counts.get(p['team'], 0) + 1
            elif pos == 4 and counts[4] < 1:
                starters.append(p)
                remaining.remove(p)
                counts[4] += 1
                team_counts[p['team']] = team_counts.get(p['team'], 0) + 1

        # 2. Fill remaining starter slots (Strategic Formation: Favor Attackers)
        max_counts = {1: 1, 2: 5, 3: 5, 4: 3}
        
        while len(starters) < 11 and remaining:
            def_candidates = [p for p in remaining if p['position'] == 2 and counts[2] < max_counts[2] and p['can_start'] and can_add_team(p['team'])]
            atk_candidates = [p for p in remaining if p['position'] in [3, 4] and counts[p['position']] < max_counts[p['position']] and p['can_start'] and can_add_team(p['team'])]
            
            best_def = def_candidates[0] if def_candidates else None
            best_atk = atk_candidates[0] if atk_candidates else None
            
            if not best_def and not best_atk:
                # Fallback: Look for ANY player who meets team constraint, even if minutes are low
                valid_backups = [p for p in remaining if can_add_team(p['team'])]
                if not valid_backups: break # Complete exhaustion
                
                selected_p = valid_backups[0]
            else:
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
            team_counts[selected_p['team']] = team_counts.get(selected_p['team'], 0) + 1

        # 3. Fill bench (remaining top players, applying team constraint)
        remaining.sort(key=lambda x: x['predicted_points'], reverse=True)
        bench = []
        for p in remaining:
            if len(bench) >= 4: break
            if can_add_team(p['team']):
                bench.append(p)
                team_counts[p['team']] = team_counts.get(p['team'], 0) + 1
        
        # PERSIST: Save predictions for future feedback loop evaluation
        # We save all 'processed' players who have features extracted
        self.trainer.storage.save_predictions(next_gw, processed)
        
        return {"starters": starters, "bench": bench}

    def get_tier_captains(self, squad: List[Dict]) -> Dict[str, Dict]:
        """Categorizes players into three distinct tiers across different teams."""
        if not squad:
            return {"obvious": {}, "joker": {}, "fun_one": {}, "weights": {}}

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



        # 2. Obvious: Highest Predicted Points among attacking pool
        attacking_pool.sort(key=lambda x: x['predicted_points'], reverse=True)
        obvious = (attacking_pool[0] if attacking_pool else squad[0]).copy()
        obvious['reason'] = f"The algorithm identifies {obvious['web_name']} as the most reliable pick with {obvious['predicted_points']} projected points."
        
        # Track selected teams to enforce diversity
        selected_teams = {obvious['team']}
        selected_ids = {obvious['id']}

        # 3. Joker: Highest Explosivity among low ownership attacking pool (<15%)
        # Exclude players from already selected teams (and same player ID)
        joker_pool = [p for p in attacking_pool if p['ownership'] < 15 and p['team'] not in selected_teams and p['id'] not in selected_ids]
        joker_pool.sort(key=lambda x: x['explosivity'], reverse=True)
        
        # If no one under 15% ownership fits criteria, try ANY ownership but distinct team
        if not joker_pool:
            # Fallback 1: Any ownership, distinct team
            fallback_pool = [p for p in attacking_pool if p['team'] not in selected_teams and p['id'] not in selected_ids]
            if fallback_pool:
                joker_pool = sorted(fallback_pool, key=lambda x: (x['ownership'], -x['explosivity']))
            else:
                # Fallback 2: Must pick someone, even if team duplicates (should be rare)
                joker_pool = [p for p in attacking_pool if p['id'] not in selected_ids]
                if not joker_pool: joker_pool = [obvious] # Absolute fail-safe
            
        joker = joker_pool[0].copy()
        selected_teams.add(joker['team'])
        selected_ids.add(joker['id'])
        
        if joker['ownership'] < 15:
            joker['reason'] = f"{joker['web_name']} offers high explosivity ({joker['explosivity']}) combined with low ownership ({joker['ownership']}%), a classic differential."
        else:
            joker['reason'] = f"{joker['web_name']} is selected as the best relative differential ({joker['ownership']}% ownership) with explosive potential."
        
        # 4. The Fun One: Best defensive attacking prospect (Defensive candidates with high Defcon)
        # Exclude players from already selected teams
        defensive_candidates = [p for p in defensive_pool if p['team'] not in selected_teams and p['id'] not in selected_ids]
        
        if not defensive_candidates:
             # Fallback 1: Try ALL defenders (ignore explosivity threshold) but KEEP team constraint
             full_def_pool = [p for p in squad if p['position'] in [1, 2]]
             defensive_candidates = [p for p in full_def_pool if p['team'] not in selected_teams and p['id'] not in selected_ids]

        if not defensive_candidates:
             # Fallback 2: Ignore team constraint if strictly necessary (use full pool)
             if 'full_def_pool' not in locals(): full_def_pool = [p for p in squad if p['position'] in [1, 2]]
             defensive_candidates = [p for p in full_def_pool if p['id'] not in selected_ids]

        if not defensive_candidates:
             defensive_candidates = [joker if joker['id'] != obvious['id'] else obvious] # Absolute fail-safe

        defensive_candidates.sort(key=lambda x: x['defcon'], reverse=True)
        fun_one = defensive_candidates[0].copy()
        
        if fun_one['defcon'] > 70:
            fun_one['reason'] = f"Elite Defcon level ({fun_one['defcon']}): {fun_one['web_name']} is picked for their massive clean sheet bonus and offensive participation."
        else:
            fun_one['reason'] = f"The best defensive attacking prospect available, focusing on clean sheet security."
        
        return {
            "obvious": obvious,
            "joker": joker,
            "fun_one": fun_one,
            # ...
            "weights": {
                "form_weight": 0.7,
                "fdr_weight": 0.5,
                "ict_weight": 0.3,
                "model_type": self.trainer.model_type,
                "brain": {
                    "noise_multiplier": (self.trainer.storage.get_latest_feedback() or {}).get('metrics', {}).get('noise_multiplier', 1.0),
                    "confidence_ema": self.trainer.storage.get_confidence_scores(),
                    "squad_accuracy": (self.trainer.storage.get_latest_feedback() or {}).get('metrics', {}).get('squad_accuracy', 0.0)
                }
            }
        }
