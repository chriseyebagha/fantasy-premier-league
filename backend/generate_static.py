import os
import json
import sys
import argparse
from datetime import datetime, timedelta, timezone
from backend.engine.data_manager import FPLDataManager
from backend.engine.storage import EngineStorage
from backend.engine.trainer import modelTrainer
from backend.engine.commander import EngineCommander

def check_deadline_eligibility(dm: FPLDataManager, storage: EngineStorage):
    """
    Checks if today is exactly 2 days before the next gameweek deadline,
    OR if the FPL API reports a deadline change since our last check.
    Returns True if we should run the refresh.
    """
    bootstrap = dm.get_bootstrap_static()
    events = bootstrap.get('events', [])
    
    next_event = None
    for event in events:
        if event.get('is_next'):
            next_event = event
            break
            
    if not next_event:
        print("No upcoming gameweek found.")
        return False
        
    gw_id = next_event.get('id')
    deadline_str = next_event.get('deadline_time')
    # FPL deadline is in UTC, e.g., '2026-01-13T18:15:00Z'
    deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    
    # Target date: 48 hours (2 days) before the deadline
    target_date = deadline - timedelta(days=2)
    
    # --- DEADLINE SENTINEL (Dynamic Tracking) ---
    history = storage._load(storage.deadline_history_file)
    last_known_deadline = history.get(str(gw_id))
    
    print(f"Next Gameweek: {next_event.get('name')} (GW{gw_id})")
    print(f"Deadline: {deadline}")
    print(f"Target Refresh Date: {target_date.date()}")
    print(f"Current Date: {now.date()}")
    
    # Case 1: Deadline Shift Detected (Event Rescheduled)
    if last_known_deadline and last_known_deadline != deadline_str:
        print(f"🚨 ALERT: Deadline shift detected for GW{gw_id}!")
        print(f"   Old: {last_known_deadline}")
        print(f"   New: {deadline_str}")
        return True

    # Case 2: Standard 2-day Refresh Window
    if now.date() == target_date.date():
        # Check if we've already run a refresh for this specific deadline string to avoid double-runs
        # (Though every 12h run would catch it, we want a clean record)
        if last_known_deadline == deadline_str:
            # We already know this deadline, and we are in the window. 
            # We should check if we already have valid dashboard data for this GW?
            # For simplicity, we trigger on the target date.
            pass
        print("MATCH: Today is the scheduled refresh day.")
        return True
    
    # Store the current deadline as the "last known" for future runs
    history[str(gw_id)] = deadline_str
    storage._save(storage.deadline_history_file, history)
    
    return False

def run_prediction_and_save():
    print("Initializing FPL Engine for static generation...")
    
    # Ensure data directory exists
    if not os.path.exists('backend/data'):
        os.makedirs('backend/data')
        
    dm = FPLDataManager()
    storage = EngineStorage() # Default path is backend/data
    trainer = modelTrainer(storage)
    commander = EngineCommander(dm, trainer)
    
    # --- SELF-TRAINING LOOP ---
    try:
        bootstrap = dm.get_bootstrap_static()
        current_gw = dm.get_upcoming_gameweek(bootstrap)
        previous_gw = current_gw - 1
        
        if previous_gw > 0:
            print(f"Checking for results from GW{previous_gw} to self-train...")
            actual_events = dm.get_actual_events(previous_gw)
            
            if actual_events:
                print(f"Found events data for {len(actual_events)} players. Evaluating performance...")
                # 1. Evaluate past predictions
                trainer.evaluate_performance(previous_gw, actual_events)
                # 2. Retrain model with new data
                trainer.train_on_feedback()
            else:
                print("No actual points data available yet for previous GW.")
    except Exception as e:
        print(f"⚠️ Self-training warning: {e}")
        # Continue execution even if training fails
    # --------------------------
    
    print("Generating top 15 players...")
    data = commander.get_top_15_players()
    starters = data['starters']
    bench = data['bench']
    
    print("Building budget-optimized squad...")
    from backend import squad_builder
    optimized_squad_data = squad_builder.build_optimal_squad(dm, commander)
    
    print("Generating recommendations...")
    recommendations = commander.get_tier_captains(starters + bench)
    
    dashboard_data = {
        "status": "online",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "gameweek": dm.get_upcoming_gameweek(dm.get_bootstrap_static()),
        "squad": starters,
        "bench": bench,
        "optimized_squad": optimized_squad_data,
        "recommendations": recommendations
    }
    
    # Path to frontend public folder
    output_dir = os.path.join(os.path.dirname(__file__), '../frontend/public')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'dashboard_data.json')
    
    print(f"Saving static data to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(dashboard_data, f, indent=4)
        
    print("Success!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FPL Static Data Generator')
    parser.add_argument('--force', action='store_true', help='Force data generation regardless of deadline')
    args = parser.parse_args()
    
    dm_check = FPLDataManager()
    storage_check = EngineStorage()
    
    try:
        if args.force:
            print("Force flag detected. Proceeding with generation.")
            run_prediction_and_save()
        elif check_deadline_eligibility(dm_check, storage_check):
            print("Deadline criteria met. Proceeding with generation.")
            run_prediction_and_save()
        else:
            print("Not a refresh day. Skipping generation.")
            sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR during static generation:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        sys.exit(1)
