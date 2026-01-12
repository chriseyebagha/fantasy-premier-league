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
    def calculate_defcon(player_row: Dict, clean_sheet_prob: float) -> float:
        """
        Defensive Contribution (Defcon).
        Combines Clean Sheet potential with attacking threat (xG/xA/xGI).
        High Defcon = Defender/GK with significant haul potential.
        """
        # Element types: 1=GK, 2=DEF
        if player_row['element_type'] not in [1, 2]:
            return 0.0
            
        xg_90 = float(player_row.get('expected_goals_per_90', 0))
        xa_90 = float(player_row.get('expected_assists_per_90', 0))
        
        defensive_action = float(player_row.get('defensive_contribution_per_90', 0))
        
        # Attack weight: Defenders who shoot or cross/pass are prioritized
        attacking_threat = (xg_90 * 1.5) + (xa_90 * 1.2)
        
        # Defcon Score:
        # 1. Clean Sheet Potential (Foundation)
        # 2. Defensive Work Rate (Bonus Points magnet) - Weight: 4.0 (Scale ~8.0 -> 32 pts)
        # 3. Attacking Threat (Goal/Assist upside) - Weight: 400 (Scale ~0.1 -> 40 pts)
        defcon_score = (clean_sheet_prob * 60) + (defensive_action * 4.0) + (attacking_threat * 400)
        return min(round(defcon_score, 1), 100.0)

    @staticmethod
    def calculate_explosivity_index(history: List[Dict], current_gw: int, form: float = 0.0, xgi_90: float = 0.0) -> float:
        """
        Measures history of 10+ point hauls ('explosivity') and elite current performance.
        Includes "Super Hot" bonuses based on season phase.
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
        score = hist_score + form_bonus + xgi_bonus + haul_bonus
        
        return min(round(score, 1), 100.0)

    @classmethod
    def prepare_features(cls, player_data: Dict, history: List[Dict], next_fixture_diff: int, current_gw: int) -> Dict:
        """Assembles a full feature vector for the XGBoost model."""
        xg_90 = float(player_data.get('expected_goals_per_90', 0))
        xa_90 = float(player_data.get('expected_assists_per_90', 0))
        
        # Simple heuristic for clean sheet prob based on fixture difficulty (will be refined)
        cs_prob = 1.0 / next_fixture_diff if next_fixture_diff > 0 else 0.2
        
        # Explicitly count total seasonal hauls
        hauls = sum(1 for m in history if m.get('total_points', 0) >= 10) if history else 0
        
        xgi_90 = cls.calculate_xgi(xg_90, xa_90)
        return {
            "xGI_90": xgi_90,
            "defcon": cls.calculate_defcon(player_data, cs_prob),
            "explosivity": cls.calculate_explosivity_index(history, current_gw, float(player_data.get('form', 0)), xgi_90),
            "form": float(player_data.get('form', 0)),
            "ict_index": float(player_data.get('ict_index', 0)),
            "fixture_difficulty": next_fixture_diff,
            "selected_by": float(player_data.get('selected_by_percent', 0)),
            "cost": player_data['now_cost'] / 10.0,
            "hauls": hauls
        }
