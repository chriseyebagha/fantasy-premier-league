import os
import json
import pandas as pd
from backend.engine.data_manager import FPLDataManager
from backend.engine.feature_factory import FeatureFactory
from backend.engine.storage import EngineStorage

def backfill():
    storage = EngineStorage("/Users/chriseyebagha/Documents/Projects/Fantasy Premier League Project/backend/data")
    dm = FPLDataManager()
    bootstrap = dm.get_bootstrap_static()
    players = bootstrap['elements']
    
    # We'll backfill the last 5 gameweeks to get high-quality labeled data
    current_gw = dm.get_upcoming_gameweek(bootstrap)
    gws_to_backfill = sorted(list(range(max(1, current_gw - 5), current_gw)))
    
    print(f"Backfilling GWS: {gws_to_backfill}")
    
    # Pre-fetch live event data for all GWs
    gw_events = {}
    for gw in gws_to_backfill:
        try:
            gw_events[gw] = dm.get_actual_events(gw)
        except Exception as e:
            print(f"Error fetching GW{gw}: {e}")
    
    all_training_records = []
    
    for i, p in enumerate(players):
        p_id = p['id']
        if i % 100 == 0:
            print(f"Processing player {i}/{len(players)}: {p['web_name']}...")
            
        try:
            summary = dm.get_player_summary(p_id)
            history = summary.get('history', [])
        except Exception as e:
            print(f"Error fetching summary for {p['web_name']}: {e}")
            continue
            
        for gw in gws_to_backfill:
            actual = gw_events.get(gw, {}).get(p_id)
            if not actual or actual.get('minutes', 0) == 0:
                continue
                
            past_history = [m for m in history if m['round'] < gw]
            
            # Opponent difficulty for THAT gameweek
            gw_entry = next((m for m in history if m['round'] == gw), None)
            if not gw_entry: continue
            
            diff = gw_entry.get('difficulty', 3)
            
            # Prepare features
            features = FeatureFactory.prepare_features(p, past_history, diff, gw)
            
            # Logic for points events:
            # 1. Defcon Points: +2 for 12+ defensive contributions
            defcon_points = 2 if actual.get('defensive_contribution', 0) >= 12 else 0
            
            # 2. Saves: 1 point per 3 saves
            saves_points = actual.get('saves', 0) // 3
            
            record = {
                "player_id": p_id,
                **features,
                "actual_points": actual['total_points'],
                "actual_goals": actual['goals_scored'],
                "actual_assists": actual['assists'],
                "actual_clean_sheets": actual['clean_sheets'],
                "actual_saves": actual['saves'], # raw saves for the model
                "actual_save_points": saves_points, # points for the xP calculation
                "actual_bonus": actual['bonus'],
                "actual_defcon_points": defcon_points,
                "actual_minutes": actual['minutes'],
                "actual_conceded": actual['goals_conceded']
            }
            all_training_records.append(record)
            
    if all_training_records:
        print(f"Saving {len(all_training_records)} new training records...")
        storage.save_training_data(all_training_records)
        print("Backfill complete.")

if __name__ == "__main__":
    backfill()
