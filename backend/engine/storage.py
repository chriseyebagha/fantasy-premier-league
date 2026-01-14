import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class EngineStorage:
    """Handles persistence for the feedback loop and historical predictions."""
    
    def __init__(self, base_path: str = "backend/data"):
        self.base_path = base_path
        self.feedback_file = os.path.join(base_path, "feedback_loop.json")
        self.prediction_history_file = os.path.join(base_path, "prediction_history.json")
        self.training_data_file = os.path.join(base_path, "training_data.json")
        self.deadline_history_file = os.path.join(base_path, "deadline_history.json")
        self._ensure_paths()

    def _ensure_paths(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        
        for f in [self.feedback_file, self.prediction_history_file, self.training_data_file, self.deadline_history_file]:
            if not os.path.exists(f):
                # feedback, prediction_history, and deadline_history are dicts, training_data is a list
                initial_content = [] if "training_data" in f else {}
                with open(f, 'w') as fh:
                    json.dump(initial_content, fh)

    def save_predictions(self, gameweek: int, predictions: List[Dict]):
        """Stores predictions for a specific gameweek to be evaluated later."""
        history = self._load(self.prediction_history_file)
        history[str(gameweek)] = {
            "timestamp": datetime.now().isoformat(),
            "predictions": predictions
        }
        self._save(self.prediction_history_file, history)

    def store_feedback(self, gameweek: int, error_metrics: Dict):
        """Stores the result of the prediction vs actual comparison."""
        feedback = self._load(self.feedback_file)
        feedback[str(gameweek)] = {
            "timestamp": datetime.now().isoformat(),
            "metrics": error_metrics
        }
        self._save(self.feedback_file, feedback)

    def save_training_data(self, records: List[Dict]):
        """Appends new feature/actual pairs for future training."""
        data = self._load(self.training_data_file)
        if not isinstance(data, list): data = []
        data.extend(records)
        self._save(self.training_data_file, data)

    def get_latest_feedback(self) -> Optional[Dict]:
        feedback = self._load(self.feedback_file)
        if not feedback:
            return None
        latest_gw = max(map(int, feedback.keys()))
        return feedback[str(latest_gw)]

    def get_feedback(self) -> Dict:
        """Returns the full feedback loop history."""
        return self._load(self.feedback_file)

    def get_confidence_scores(self) -> Dict:
        """Loads and returns current model confidence scores."""
        conf_path = os.path.join(self.base_path, "confidence.json")
        if os.path.exists(conf_path):
            with open(conf_path, 'r') as f:
                return json.load(f)
        return {
            "actual_goals": 1.0,
            "actual_assists": 1.0,
            "actual_clean_sheets": 1.0,
            "actual_saves": 1.0,
            "actual_bonus": 1.0,
            "actual_defcon_points": 1.0
        }

    def _load(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, path: str, data: Dict):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
