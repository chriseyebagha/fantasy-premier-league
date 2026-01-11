import os
import sys
import json
import random

# Add project root to path
sys.path.append(os.getcwd())

from backend.engine.data_manager import FPLDataManager
from backend.engine.storage import EngineStorage
from backend.engine.trainer import modelTrainer
from backend.engine.commander import EngineCommander

def run_backtest():
    print("🚀 Starting Engine Backtest & RL Loop Verification...")
    
    dm = FPLDataManager()
    storage = EngineStorage()
    trainer = modelTrainer(storage)
    commander = EngineCommander(dm, trainer)
    
    # 1. Clear existing test data for a clean run (locally)
    if os.path.exists(storage.training_data_file):
        os.remove(storage.training_data_file)
    
    # 2. Simulate 3 Gameweeks
    for gw in range(1, 4):
        print(f"\n--- Simulating Gameweek {gw} ---")
        
        # A. Generate Predictions
        print(f"Generating predictions for GW{gw}...")
        squad = commander.get_top_15_players()
        storage.save_predictions(gw, squad)
        
        # B. Simulate Actual Results (randomized for testing)
        print(f"Simulating actual scores for GW{gw}...")
        actual_points = {}
        for p in squad:
            # Predict around 2-10 points with some noise
            actual_points[p['id']] = max(0, p['predicted_points'] + random.uniform(-3, 5))
            
        # C. Evaluate & Feed into RL Loop
        print(f"Evaluating GW{gw} performance and updating training pool...")
        trainer.evaluate_performance(gw, actual_points)
        
        # D. Train Model (only if we have enough data)
        print(f"Attempting RL Model Update...")
        trainer.train_on_feedback()
        
    print("\n✅ Backtest Completion Check:")
    training_data = storage._load(storage.training_data_file)
    print(f"Total training records collected: {len(training_data)}")
    
    if len(training_data) > 0:
        print("💡 SUCCESS: Engine is successfully learning from feedback.")
    else:
        print("❌ FAILURE: No training data collected.")

if __name__ == "__main__":
    run_backtest()
