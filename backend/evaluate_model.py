import os
import json
from datetime import datetime
from backend.engine.data_manager import FPLDataManager
from backend.engine.storage import EngineStorage
from backend.engine.trainer import modelTrainer

def generate_expert_report(gameweek: int, feedback: dict, predictions: list, actual_points: dict):
    """Generates a markdown report comparing predicted vs actual points."""
    report_path = "backend/data/performance_report.md"
    
    # Sort predictions by error magnitude to highlight biggest misses
    rows = []
    for p in predictions:
        p_id = p['id']
        actual = actual_points.get(str(p_id)) or actual_points.get(p_id)
        if actual is not None:
            pred = p['predicted_points']
            error = pred - actual
            rows.append({
                "name": p['web_name'],
                "team": p['team'],
                "predicted": pred,
                "actual": actual,
                "error": error
            })
    
    rows.sort(key=lambda x: abs(x['error']), reverse=True)
    
    with open(report_path, "w") as f:
        f.write(f"# FPL Model Performance Report - Gameweek {gameweek}\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        f.write("## Summary Metrics\n")
        f.write(f"- **Mean Absolute Error (MAE):** {feedback['mae']:.2f}\n")
        f.write(f"- **Root Mean Squared Error (RMSE):** {feedback['rmse']:.2f}\n")
        f.write(f"- **Sample Size:** {feedback['sample_size']} players\n\n")
        
        f.write("## Top Prediction Discrepancies (Experts: Please Review)\n")
        f.write("| Player | Team | Predicted | Actual | Error |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: |\n")
        for r in rows[:15]:
            f.write(f"| {r['name']} | {r['team']} | {r['predicted']:.1f} | {r['actual']:.1f} | {r['error']:+.1f} |\n")
        
        f.write("\n\n## Retraining Status\n")
        f.write("The XGBoost model has been retrained with these new historical records added to the training set.\n")

def main():
    print("🚀 Starting Model Feedback Loop...")
    
    dm = FPLDataManager()
    storage = EngineStorage()
    trainer = modelTrainer(storage)
    
    # 1. Determine last completed gameweek
    bootstrap = dm.get_bootstrap_static()
    events = bootstrap.get('events', [])
    last_gw = None
    for event in events:
        if event.get('finished'):
            last_gw = event['id']
    
    if not last_gw:
        print("❌ Could not identify a finished gameweek.")
        return

    print(f"📊 Evaluating Gameweek {last_gw}...")
    
    # 2. Check if we have predictions for this GW
    history = storage._load(storage.prediction_history_file)
    if str(last_gw) not in history:
        print(f"⚠️ No prediction history found for GW{last_gw}. Skipping evaluation.")
        return
        
    # Check if we already have feedback to avoid duplicate effort (optional)
    feedback_history = storage._load(storage.feedback_file)
    if str(last_gw) in feedback_history:
        print(f"ℹ️ GW{last_gw} already evaluated. Re-running to ensure model is fresh.")

    # 3. Fetch actual points
    print(f"📡 Fetching actual points for GW{last_gw}...")
    actual_points = dm.get_actual_points(last_gw)
    
    # 4. Trigger evaluation and training data collection
    trainer.evaluate_performance(last_gw, actual_points)
    
    # 5. Trigger retraining
    trainer.train_on_feedback()
    
    # 6. Generate report
    latest_feedback = storage.get_latest_feedback()
    if latest_feedback:
        predictions = history[str(last_gw)]['predictions']
        generate_expert_report(last_gw, latest_feedback['metrics'], predictions, actual_points)
        print(f"✅ Feedback loop complete. Report saved: backend/data/performance_report.md")
    else:
        print("❌ Evaluation failed to produce metrics.")

if __name__ == "__main__":
    main()
