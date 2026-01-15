
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.engine.data_manager import FPLDataManager

def check_team_xgc():
    print("📊 Fetching FPL data for xGC analysis...")
    dm = FPLDataManager()
    bootstrap = dm.get_bootstrap_static()
    players = bootstrap['elements']
    teams = {t['id']: t['name'] for t in bootstrap['teams']}
    
    # 1. Group defenders/keepers by team
    team_groups = {}
    for p in players:
        t_id = p['team']
        if t_id not in team_groups:
            team_groups[t_id] = []
        team_groups[t_id].append(p)
    
    team_stats = []

    print("🔄 Processing rolling stats for all 20 teams...")
    
    # 2. For each team, get stats
    for t_id, members in team_groups.items():
        # Pick top 3 defensive assets by minutes to represent the team
        gks = [p for p in members if p['element_type'] == 1]
        defs = [p for p in members if p['element_type'] == 2]
        candidates = sorted(gks + defs, key=lambda x: x.get('minutes', 0), reverse=True)[:3]
        
        if not candidates:
            continue
            
        gw_stats = {} # round -> (xgc, gc)
        
        for p in candidates:
            try:
                summary = dm.get_player_summary(p['id'])
                history = summary.get('history', [])
            except:
                continue
                
            for h in history:
                gw = h.get('round')
                xgc = float(h.get('expected_goals_conceded') or 0)
                gc = float(h.get('goals_conceded') or 0)
                
                if gw not in gw_stats:
                    gw_stats[gw] = (xgc, gc)
                else:
                    # MAX logic as per commander.py to avoid partial game (sub) noise
                    curr_xgc, curr_gc = gw_stats[gw]
                    gw_stats[gw] = (max(curr_xgc, xgc), max(curr_gc, gc))
        
        # Get last 7 gameweeks
        recent_gws = sorted(gw_stats.keys(), reverse=True)[:7]
        
        if not recent_gws:
            continue
            
        recent_xgc = [gw_stats[gw][0] for gw in recent_gws]
        recent_gc = [gw_stats[gw][1] for gw in recent_gws]
        
        avg_xgc = sum(recent_xgc) / len(recent_xgc)
        avg_gc = sum(recent_gc) / len(recent_gc)
        blended = (avg_xgc * 0.5) + (avg_gc * 0.5)
        
        team_stats.append({
            "name": teams[t_id],
            "avg_xgc": avg_xgc,
            "avg_gc": avg_gc,
            "blended": blended,
            "games": len(recent_xgc)
        })

    # Sort by Avg xGC (Descending - Worst Defense First)
    team_stats.sort(key=lambda x: x['avg_xgc'], reverse=True)

    print("\n🛡️  WORST DEFENSES: Last 7 Gameweeks (sorted by xGC)")
    print(f"{'Rank':<5} {'Team':<20} {'xGC/Match':<12} {'GC/Match':<12} {'Blended Score':<12}")
    print("-" * 65)
    
    for i, t in enumerate(team_stats):
        print(f"{i+1:<5} {t['name']:<20} {t['avg_xgc']:<12.2f} {t['avg_gc']:<12.2f} {t['blended']:<12.2f}")

if __name__ == "__main__":
    check_team_xgc()
