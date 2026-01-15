import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
from sklearn.ensemble import RandomForestRegressor
from .storage import EngineStorage

class modelTrainer:
    """Manages training of the points predictor with a multi-model probabilistic approach."""
    
    def __init__(self, storage: EngineStorage):
        self.storage = storage
        self.model_type = "xgb" if HAS_XGB else "rf"
        
        # We now train separate models for each event to build a probabilistic xP
        self.targets = ['actual_goals', 'actual_assists', 'actual_clean_sheets', 'actual_saves', 'actual_bonus', 'actual_defcon_points']
        self.models = {}
        self.model_paths = {}
        
        for target in self.targets:
            if HAS_XGB:
                # Use Poisson for goals/assists/saves/bonus (counts), Logistic for clean sheets (binary)
                objective = 'count:poisson' if target != 'actual_clean_sheets' else 'binary:logistic'
                self.models[target] = XGBRegressor(
                    n_estimators=50,
                    learning_rate=0.1,
                    max_depth=4,
                    objective=objective
                )
            else:
                self.models[target] = RandomForestRegressor(n_estimators=50, max_depth=4)
            
            self.model_paths[target] = os.path.join(storage.base_path, f"model_{self.model_type}_{target}.joblib")
            
        self.features = [
            'xG_90', 'xA_90', 'actual_goals_90', 'actual_assists_90', 'actual_cs_90',
            'xGI_90', 'saves_90', 'bps_90', 'defcon_90',
            'defcon', 'explosivity', 'form', 'ict_index', 
            'fixture_difficulty', 'selected_by', 'cost', 'hauls', 'opponent_vulnerability'
        ]
        
        # RL Reinforcement: Model confidence/trust scores
        self.confidence_scores = self.storage._load(os.path.join(self.storage.base_path, "confidence.json"))
        if not self.confidence_scores:
            self.confidence_scores = {target: 1.0 for target in self.targets}
            
        self.load_model()

    def load_model(self):
        import joblib
        for target, path in self.model_paths.items():
            if os.path.exists(path):
                self.models[target] = joblib.load(path)

    def save_model(self):
        import joblib
        for target, path in self.model_paths.items():
            joblib.dump(self.models[target], path)
        self.storage._save(os.path.join(self.storage.base_path, "confidence.json"), self.confidence_scores)

    def train_on_feedback(self):
        """
        Trains all event-based models based on collected training data.
        Uses Temporal Weighting to prioritize recent results (Reinforcement Learning).
        """
        data = self.storage._load(self.storage.training_data_file)
        if not data or len(data) < 20: 
            print("Insufficient training data for RL update.")
            return

        df = pd.DataFrame(data)
        
        X = df[self.features].fillna(0)

        # 1. Temporal Weighting (Self-Reinforcement)
        # We give newer records (last 1000) twice as much weight as older historical data
        n_samples = len(df)
        weights = np.ones(n_samples)
        if n_samples > 1000:
            # Linear ramp from 0.5 (oldest) to 1.5 (newest)
            weights = np.linspace(0.5, 1.5, n_samples)

        print(f"Engine training multi-head system ({self.model_type}) with Temporal Weighting on {len(df)} records...")
        
        for target_label in self.targets:
            if target_label in df.columns:
                print(f"  - Reinforcing {target_label} model...")
                y = df[target_label].fillna(0)
                
                if HAS_XGB:
                    self.models[target_label].fit(X, y, sample_weight=weights)
                else:
                    self.models[target_label].fit(X, y) # RF doesn't support sample_weight easily here
        
        self.save_model()

    def predict(self, feature_df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Generates probabilistic event predictions for the next Gameweek."""
        results = {}
        # Ensure only training features are passed (prevents column mismatch errors)
        X = feature_df[self.features].fillna(0)
        
        for target in self.targets:
            try:
                # Use the specific model for this event
                results[target] = self.models[target].predict(X)
            except Exception as e:
                print(f"⚠️ Prediction error for {target}: {e}")
                # Fallback: zero out
                results[target] = np.zeros(len(X))
        return results

    def translate_to_xp(self, event_predictions: Dict[str, np.ndarray], element_types: List[int]) -> np.ndarray:
        """
        Translates event probabilities into xP (Expected Points).
        Uses Reinforcement Confidence multipliers (Dynamic Trust).
        """
        # FPL Points constants by element type (1=GKP, 2=DEF, 3=MID, 4=FWD)
        GOAL_VALS = {1: 6, 2: 6, 3: 5, 4: 4}
        CS_VALS = {1: 4, 2: 4, 3: 1, 4: 0}
        ASSIST_VALS = 3
        SAVE_VALS = 0.33 # 1 point per 3 saves
        
        e_types = np.array(element_types)
        n = len(e_types)
        
        # Vectorized scoring weights based on position
        goal_weights = np.array([GOAL_VALS.get(t, 4) for t in e_types])
        cs_weights = np.array([CS_VALS.get(t, 0) for t in e_types])
        
        # Calculate xP with Confidence Reinforcement
        xp = np.full(n, 2.0) # Baseline for 60+ minutes
        
        # Get confidence multipliers (default to 1.0)
        c = self.confidence_scores
        
        xp += event_predictions['actual_goals'] * goal_weights * c.get('actual_goals', 1.0)
        xp += event_predictions['actual_assists'] * ASSIST_VALS * c.get('actual_assists', 1.0)
        xp += event_predictions['actual_clean_sheets'] * cs_weights * c.get('actual_clean_sheets', 1.0)
        xp += event_predictions['actual_saves'] * SAVE_VALS * c.get('actual_saves', 1.0)
        xp += event_predictions.get('actual_bonus', np.zeros(n)) * c.get('actual_bonus', 1.0)
        xp += event_predictions.get('actual_defcon_points', np.zeros(n)) * c.get('actual_defcon_points', 1.0)
        
        return np.maximum(xp, 0)

    def calculate_haul_probability(self, event_predictions: Dict[str, np.ndarray], element_types: List[int], n_sims: int = 1500, haul_multipliers: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Calculates the probability of a player scoring 11+ points using a Monte Carlo simulation.
        Assumes independent Poisson events for counts and Logistic for clean sheets.
        
        Args:
            event_predictions: Dictionary of predicted probabilities/counts per head.
            element_types: List of player positions.
            n_sims: Number of Monte Carlo iterations.
            haul_multipliers: Optional array of clinicality/matchup boosters (default 1.0).
        """
        n_players = len(element_types)
        haul_probs = np.zeros(n_players)
        
        # FPL Points constants by element type (1=GKP, 2=DEF, 3=MID, 4=FWD)
        GOAL_VALS = {1: 6, 2: 6, 3: 5, 4: 4}
        CS_VALS = {1: 4, 2: 4, 3: 1, 4: 0}
        ASSIST_VALS = 3
        SAVE_VALS = 0.33
        
        c = self.confidence_scores

        for i in range(n_players):
            pos = element_types[i]
            multiplier = haul_multipliers[i] if haul_multipliers is not None else 1.0
            
            # Adjusted lambdas based on confidence scores and Vesuvius Multiplier
            l_goals = event_predictions['actual_goals'][i] * c.get('actual_goals', 1.0) * multiplier
            l_assists = event_predictions['actual_assists'][i] * c.get('actual_assists', 1.0) * multiplier
            l_saves = event_predictions['actual_saves'][i] * c.get('actual_saves', 1.0)
            l_bonus = event_predictions.get('actual_bonus', np.zeros(n_players))[i] * c.get('actual_bonus', 1.0) * multiplier
            l_defcon = event_predictions.get('actual_defcon_points', np.zeros(n_players))[i] * c.get('actual_defcon_points', 1.0)
            
            # Clean sheet is a biased coin flip - also boosted by multiplier
            p_cs = event_predictions['actual_clean_sheets'][i] * c.get('actual_clean_sheets', 1.0) * multiplier
            p_cs = min(max(p_cs, 0), 1)
            p_cs = min(max(p_cs, 0), 1)
            
            # Monte Carlo Simulation
            sim_goals = np.random.poisson(l_goals, n_sims)
            sim_assists = np.random.poisson(l_assists, n_sims)
            sim_saves = np.random.poisson(l_saves, n_sims)
            sim_bonus = np.random.poisson(l_bonus, n_sims)
            sim_defcon = np.random.poisson(l_defcon, n_sims)
            sim_cs = np.random.binomial(1, p_cs, n_sims)
            
            # Calculate points per match simulation
            points = 2.0 # Baseline for starting
            points += sim_goals * GOAL_VALS.get(pos, 4)
            points += sim_assists * ASSIST_VALS
            points += sim_cs * CS_VALS.get(pos, 0)
            points += sim_saves * SAVE_VALS
            points += sim_bonus
            points += sim_defcon
            
            # A haul is defined as 11+ points (User definition)
            haul_probs[i] = np.mean(points >= 11)
            
        return haul_probs

    def evaluate_performance(self, gameweek: int, actual_events: Dict[int, Dict]):
        """
        Compares predicted vs actual outcomes with the 'Stability Sentinel' logic.
        Includes Noise Gate, Hysteresis, and Squad-wide accuracy checks.
        """
        history = self.storage._load(self.storage.prediction_history_file)
        gw_data = history.get(str(gameweek))
        
        if not gw_data:
            print(f"No prediction history found for GW{gameweek}")
            return
            
        predictions = gw_data['predictions']
        training_records = []
        errors = []
        
        # 1. Systemic Noise Gate Preparation
        temp_errors = []
        for p in predictions:
            p_id = p['id']
            actual_data = actual_events.get(str(p_id)) or actual_events.get(p_id)
            if actual_data:
                temp_errors.append(abs(p['predicted_points'] - actual_data.get('total_points', 0)))
        
        global_mae = sum(temp_errors) / len(temp_errors) if temp_errors else 0
        noise_multiplier = 0.2 if global_mae > 3.0 else (0.5 if global_mae > 2.5 else 1.0)
        
        # 2. Squad-Wide Accuracy (7/11 Logic)
        sorted_preds = sorted(predictions, key=lambda x: x.get('predicted_points', 0), reverse=True)
        top_11_ids = [str(p['id']) for p in sorted_preds[:11]]
        squad_hits = 0
        
        for p_id in top_11_ids:
            actual_data = actual_events.get(str(p_id)) or actual_events.get(int(p_id))
            if actual_data and actual_data.get('total_points', 0) >= 4:
                squad_hits += 1
        
        squad_accuracy = squad_hits / 11
        stability_multiplier = 1.5 if squad_accuracy >= 0.6 else (0.8 if squad_accuracy < 0.4 else 1.0)
        
        # Final adjusted Learning Rate
        BASE_LR = 0.05
        EFFECTIVE_LR = BASE_LR * noise_multiplier * stability_multiplier
        
        print(f"🛡️ Stability Sentinel (GW{gameweek}):")
        print(f"  - Global MAE: {global_mae:.2f} (Noise Gate: {noise_multiplier}x)")
        print(f"  - Squad Hits: {squad_hits}/11 (Stability: {stability_multiplier}x)")
        print(f"  - Effective LR: {EFFECTIVE_LR:.4f}")

        # 3. Main Evaluation & Hysteresis Update
        for p in predictions:
            p_id = p['id']
            actual_data = actual_events.get(str(p_id)) or actual_events.get(p_id)
            
            if actual_data is not None:
                total_points = actual_data.get('total_points', 0)
                error = abs(p['predicted_points'] - total_points)
                errors.append(error)
                
                # Update Model Confidence with Hysteresis
                for target in self.targets:
                    prob_key = f"prob_{target.replace('actual_', '').replace('clean_sheets', 'cs')}"
                    pred_prob = p.get(prob_key, 0)
                    actual_val = actual_data.get(target, 0)
                    
                    diff = abs(pred_prob - actual_val)
                    reward = 1.0 - min(diff, 1.0)
                    self.confidence_scores[target] = (1 - EFFECTIVE_LR) * self.confidence_scores[target] + EFFECTIVE_LR * reward

                # Fetch features
                features = p.get('features', {})
                # Defcon Logic: 10+ for DEFs, 12+ for MIDs/FWDs (New 24/25 Rules)
                pos = p.get('position', 2) # Default to DEF if unknown
                dc_value = actual_data.get('defensive_contribution', 0)
                if pos == 2:
                    defcon_points = 2 if dc_value >= 10 else 0
                elif pos in [3, 4]:
                    defcon_points = 2 if dc_value >= 12 else 0
                else:
                    defcon_points = 0 # GKs don't get defcon points
                
                if features:
                    training_records.append({
                        "player_id": p_id,
                        **features,
                        "actual_points": total_points,
                        "actual_goals": actual_data.get('goals_scored', 0),
                        "actual_assists": actual_data.get('assists', 0),
                        "actual_clean_sheets": actual_data.get('clean_sheets', 0),
                        "actual_saves": actual_data.get('saves', 0),
                        "actual_save_points": actual_data.get('saves', 0) // 3,
                        "actual_bonus": actual_data.get('bonus', 0),
                        "actual_defcon_points": defcon_points,
                        "actual_minutes": actual_data.get('minutes', 0),
                        "actual_conceded": actual_data.get('goals_conceded', 0)
                    })
        
        if training_records:
            self.storage.save_training_data(training_records)
            
        if errors:
            mae = sum(errors) / len(errors)
            rmse = (sum(e**2 for e in errors) / len(errors))**0.5
            self.storage.store_feedback(gameweek, {
                "mae": mae,
                "rmse": rmse,
                "global_mae": global_mae,
                "squad_accuracy": squad_accuracy,
                "noise_multiplier": noise_multiplier,
                "effective_lr": EFFECTIVE_LR,
                "sample_size": len(errors)
            })
        
        # Save updated confidence scores to disk
        self.save_model()
