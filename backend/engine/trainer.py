import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from backend.engine.storage import EngineStorage

# Try to import XGBoost, fallback to RandomForest if libomp is missing
try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except (ImportError, Exception):
    from sklearn.ensemble import RandomForestRegressor
    HAS_XGB = False
    print("⚠️ XGBoost load failed (likely missing libomp). Falling back to RandomForestRegressor.")

class modelTrainer:
    """Manages training of the points predictor and the RL loop."""
    
    def __init__(self, storage: EngineStorage):
        self.storage = storage
        if HAS_XGB:
            self.model = XGBRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                objective='reg:squarederror'
            )
            self.model_type = "xgb"
        else:
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=5
            )
            self.model_type = "rf"
            
        self.model_path = os.path.join(storage.base_path, f"model_{self.model_type}.joblib")

    def load_model(self):
        # Using joblib for models is generally safer across types
        import joblib
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception as e:
                print(f"Error loading model: {e}")

    def save_model(self):
        import joblib
        joblib.dump(self.model, self.model_path)

    def train_on_feedback(self):
        """
        Trains a new model based on collected training data.
        """
        data = self.storage._load(self.storage.training_data_file)
        if not data or len(data) < 20: # Minimum sample size
            print("Insufficient training data for RL update.")
            return

        df = pd.DataFrame(data)
        X = df.drop(columns=['actual_points', 'player_id'], errors='ignore')
        y = df['actual_points']

        print(f"Engine training system ({self.model_type}) on {len(df)} historical records...")
        self.model.fit(X, y)
        self.save_model()

    def predict(self, feature_df: pd.DataFrame) -> np.ndarray:
        """Generates point predictions for the next Gameweek."""
        try:
            return self.model.predict(feature_df)
        except Exception:
            # Fallback heuristic
            return feature_df['form'].values * 1.0

    def evaluate_performance(self, gameweek: int, actual_points: Dict[int, float]):
        """
        Compares predicted vs actual, stores feedback, and saves training records.
        """
        history = self.storage._load(self.storage.prediction_history_file)
        gw_data = history.get(str(gameweek))
        
        if not gw_data:
            return
            
        predictions = gw_data['predictions']
        training_records = []
        errors = []
        
        for p in predictions:
            p_id = p['id']
            # Support both integer and string keys in actual_points
            actual = actual_points.get(str(p_id)) or actual_points.get(p_id)
            
            if actual is not None:
                error = abs(p['predicted_points'] - actual)
                errors.append(error)
                
                # Fetch features from prediction history
                features = p.get('features', {})
                if features:
                    training_records.append({
                        "player_id": p_id,
                        **features,
                        "actual_points": actual
                    })
        
        if training_records:
            self.storage.save_training_data(training_records)

        if errors:
            mae = np.mean(errors)
            rmse = np.sqrt(np.mean(np.array(errors)**2))
            
            self.storage.store_feedback(gameweek, {
                "mae": float(mae),
                "rmse": float(rmse),
                "sample_size": len(errors)
            })
            print(f"GW{gameweek} evaluation complete. MAE: {mae:.2f}")
