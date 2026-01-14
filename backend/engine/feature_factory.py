import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class FeatureFactory:
    """Derives high-signal metrics for the FPL model."""
    
    @staticmethod
    def calculate_xgi(xg: float, xa: float) -> float:
        """Expected Goal Involvement."""
        return xg + xa

    @staticmethod
    def calculate_defcon(player_row: Dict, history: List[Dict], fdr: int) -> float:
        """
        Defensive Contribution (Defcon).
        Combines Historic Clean Sheet potential with attacking threat (xG/xA/xGI).
        Adjusted by Fixture Difficulty (FDR).
        """
        # Element types: 1=GK, 2=DEF
        if player_row['element_type'] not in [1, 2]:
            return 0.0
            
        xg_90 = float(player_row.get('expected_goals_per_90', 0))
        xa_90 = float(player_row.get('expected_assists_per_90', 0))
        
        defensive_action = float(player_row.get('defensive_contribution_per_90', 0))
        
        # Calculate Historic Clean Sheet Probability
        # If history exists, sum clean_sheets (usually 0 or 1) and divide by games
        if history:
            total_cs = sum(1 for m in history if m.get('clean_sheets', 0) > 0)
            historic_cs_prob = total_cs / len(history)
        else:
            historic_cs_prob = 0.0

        # Attack weight: Defenders who shoot or cross/pass are prioritized
        attacking_threat = (xg_90 * 1.5) + (xa_90 * 1.2)
        
        # FDR Adjustment: Easy fixture (2) boosts score, Hard fixture (4-5) penalizes
        # Multiplier: 1.15 for FDR <= 2, 1.0 for FDR 3, 0.85 for FDR 4, 0.7 for FDR 5
        fdr_multiplier = 1.0
        if fdr <= 2: fdr_multiplier = 1.15
        elif fdr == 4: fdr_multiplier = 0.85
        elif fdr >= 5: fdr_multiplier = 0.7
        
        # Defcon Score:
        # 1. Clean Sheet Potential (Historic Data) * FDR Modifier
        # 2. Defensive Work Rate (Bonus Points magnet) - Weight: 4.0 
        # 3. Attacking Threat (Goal/Assist upside) - Weight: 400 
        defcon_score = ((historic_cs_prob * 60) * fdr_multiplier) + (defensive_action * 4.0) + (attacking_threat * 400)
        return min(round(defcon_score, 1), 100.0)

    @staticmethod
    def calculate_explosivity_index(history: List[Dict], current_gw: int, fdr: int, form: float = 0.0, xgi_90: float = 0.0) -> float:
        """
        Measures history of 10+ point hauls ('explosivity') and elite current performance.
        Includes "Super Hot" bonuses based on season phase.
        Adjusted by Fixture Difficulty (FDR).
        """
        if not history:
            return 0.0
            
        # Count Double Digit Hauls
        total_hauls = sum(1 for m in history if m.get('total_points', 0) >= 10)
        
        # Recent Form: Last 10 games
        recent_10 = history[-10:] if len(history) >= 10 else history
        recent_10_hauls = sum(1 for m in recent_10 if m.get('total_points', 0) >= 10)
        
        # Base Score (Max 40 pts)
        frequency = total_hauls / len(history) if history else 0
        hist_score = (frequency * 30) + (recent_10_hauls * 10) # Weighted to recent
        
        # 2. Performance Bonuses
        form_bonus = 15.0 if form >= 7.5 else 0.0
        xgi_bonus = 15.0 if xgi_90 >= 0.70 else 0.0
        
        # 3. "Super Hot" / Heavy Hitter Status (User defined logic)
        # - Any time: 5 hauls in last 10 games
        # - Early Season (<= GW20): 5 total hauls
        # - Late Season (> GW20): 10 total hauls
        is_super_hot = False
        
        if recent_10_hauls >= 5:
            is_super_hot = True
        elif current_gw <= 20 and total_hauls >= 5:
            is_super_hot = True
        elif current_gw > 20 and total_hauls >= 10:
            is_super_hot = True
            
        haul_bonus = 25.0 if is_super_hot else 0.0
        
        # 4. Aggregated Score
        # 4. Aggregated Score
        score = hist_score + form_bonus + xgi_bonus + haul_bonus
        
        # FDR Bonus for Explosivity: Easy games unlock ceiling
        if fdr <= 2:
            score *= 1.10
        elif fdr >= 5:
            score *= 0.90
        
        return min(round(score, 1), 100.0)

    @classmethod
    def prepare_features(cls, player_data: Dict, history: List[Dict], next_fixture_diff: int, current_gw: int, opponent_xgc: float = 0.0) -> Dict:
        """Assembles a full feature vector for the XGBoost model."""
        xg_90 = float(player_data.get('expected_goals_per_90', 0))
        xa_90 = float(player_data.get('expected_assists_per_90', 0))
        saves_90 = float(player_data.get('saves_per_90', 0))
        
        # Calculate bps_90 manually as it's missing from standard bootstrap
        mins = float(player_data.get('minutes', 0))
        total_bps = float(player_data.get('bps', 0))
        bps_90 = (total_bps / (mins / 90)) if mins > 0 else 0
        
        defcon_90 = float(player_data.get('defensive_contribution_per_90', 0))
        
        # Calculate actual seasonal delivery per 90 from history (avoids leakage)
        past_mins = sum(m.get('minutes', 0) for m in history) if history else 0
        actual_goals_90 = (sum(m.get('goals_scored', 0) for m in history) / (past_mins / 90)) if past_mins > 0 else 0
        actual_assists_90 = (sum(m.get('assists', 0) for m in history) / (past_mins / 90)) if past_mins > 0 else 0
        actual_cs_90 = (sum(m.get('clean_sheets', 0) for m in history) / (past_mins / 90)) if past_mins > 0 else 0
        
        # Explicitly count total seasonal hauls
        hauls = sum(1 for m in history if m.get('total_points', 0) >= 10) if history else 0
        
        xgi_90 = cls.calculate_xgi(xg_90, xa_90)
        return {
            "xG_90": xg_90,
            "xA_90": xa_90,
            "actual_goals_90": actual_goals_90,
            "actual_assists_90": actual_assists_90,
            "actual_cs_90": actual_cs_90,
            "xGI_90": xgi_90,
            "saves_90": saves_90,
            "bps_90": bps_90,
            "defcon_90": defcon_90,
            "defcon": cls.calculate_defcon(player_data, history, next_fixture_diff),
            "explosivity": cls.calculate_explosivity_index(history, current_gw, next_fixture_diff, float(player_data.get('form', 0)), xgi_90),
            "form": float(player_data.get('form', 0)),
            "ict_index": float(player_data.get('ict_index', 0)),
            "fixture_difficulty": next_fixture_diff,
            "selected_by": float(player_data.get('selected_by_percent', 0)),
            "cost": player_data['now_cost'] / 10.0,
            "hauls": hauls,
            "opponent_xgc": opponent_xgc
        }
