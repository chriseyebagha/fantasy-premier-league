import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

TRACKER_FILE = 'prediction_history.json'

class PredictionTracker:
    def __init__(self, data_dir='.'):
        self.filepath = os.path.join(data_dir, TRACKER_FILE)
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except:
                return {"gameweeks": {}}
        return {"gameweeks": {}}

    def _save_history(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.history, f, indent=2)

    def save_predictions(self, gameweek: int, players: List[Dict]):
        """
        Saves the current predictions for a gameweek.
        Only saves if not already saved for this GW to avoid overwriting with post-game data.
        """
        gw_key = str(gameweek)
        if gw_key in self.history["gameweeks"]:
            # Already saved, maybe update if needed, but for now assume first snapshot is best
            return

        snapshot = []
        for p in players:
            snapshot.append({
                "id": p["id"],
                "web_name": p["web_name"],
                "predicted_explosivity": p.get("explosivity_index", 0),
                "predicted_points": p.get("predicted_points", 0),
                "actual_points": None  # To be filled later
            })
        
        self.history["gameweeks"][gw_key] = {
            "timestamp": datetime.now().isoformat(),
            "predictions": snapshot,
            "evaluated": False
        }
        self._save_history()

    def update_actuals(self, gameweek: int, player_actuals: Dict[int, int]):
        """
        Updates the actual points for a past gameweek.
        player_actuals: Dict mapping player_id to actual_points
        """
        gw_key = str(gameweek)
        if gw_key not in self.history["gameweeks"]:
            return

        gw_data = self.history["gameweeks"][gw_key]
        updated_count = 0
        
        for p in gw_data["predictions"]:
            pid = p["id"]
            if pid in player_actuals:
                p["actual_points"] = player_actuals[pid]
                updated_count += 1
        
        if updated_count > 0:
            gw_data["evaluated"] = True
            self._save_history()

    def evaluate_performance(self) -> Dict:
        """
        Evaluates model performance over tracked gameweeks.
        Returns status and metrics.
        """
        results = []
        
        for gw, data in self.history["gameweeks"].items():
            if not data.get("evaluated"):
                continue
                
            preds = data["predictions"]
            # Filter for players who played
            valid_preds = [p for p in preds if p["actual_points"] is not None]
            
            if not valid_preds:
                continue
                
            # Metric 1: Top 5 Explosive Picks vs Average
            sorted_by_exp = sorted(valid_preds, key=lambda x: x["predicted_explosivity"], reverse=True)
            top_5 = sorted_by_exp[:5]
            top_5_avg = np.mean([p["actual_points"] for p in top_5])
            overall_avg = np.mean([p["actual_points"] for p in valid_preds])
            
            # Metric 2: RMSE of predicted points
            mse = np.mean([(p["predicted_points"] - p["actual_points"])**2 for p in valid_preds])
            rmse = np.sqrt(mse)
            
            results.append({
                "gameweek": int(gw),
                "top_5_avg": top_5_avg,
                "overall_avg": overall_avg,
                "lift": top_5_avg - overall_avg,
                "rmse": rmse,
                "success": top_5_avg > overall_avg
            })
            
        if not results:
            return None
            
        # Sort by gameweek
        results.sort(key=lambda x: x["gameweek"])
        
        # Check consecutive failures (negative lift)
        consecutive_failures = 0
        for res in reversed(results):
            if res["lift"] <= 0:
                consecutive_failures += 1
            else:
                break
                
        status = "Healthy"
        if consecutive_failures >= 5:
            status = "Underperforming"
            
        return {
            "status": status,
            "consecutive_failures": consecutive_failures,
            "recent_results": results[-5:]
        }
