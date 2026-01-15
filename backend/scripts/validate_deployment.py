import json
import os
import sys

def validate_dashboard_data(filepath):
    """
    Performs critical health checks on the generated dashboard_data.json.
    Returns True if valid, raises error or returns False otherwise.
    """
    if not os.path.exists(filepath):
        print(f"❌ Error: {filepath} not found.")
        return False

    with open(filepath, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Error: {filepath} is not valid JSON.")
            return False

    # 1. Schema Check
    required_keys = ["status", "gameweek", "squad", "bench", "optimized_squad", "recommendations"]
    for key in required_keys:
        if key not in data:
            print(f"❌ Error: Missing required key '{key}' in dashboard data.")
            return False

    # 2. Content Sanity Checks
    if data["status"] != "online":
        print(f"❌ Error: System status is not 'online'.")
        return False

    if not isinstance(data["gameweek"], int) or data["gameweek"] < 1:
        print(f"❌ Error: Invalid gameweek value: {data['gameweek']}")
        return False

    # 3. Squad Integrity
    if len(data["squad"]) != 11:
        print(f"❌ Error: Predicted squad has {len(data['squad'])} players (expected 11).")
        return False
    
    if len(data.get("bench", [])) != 4:
        print(f"❌ Error: Predicted bench has {len(data.get('bench', []))} players (expected 4).")
        return False

    # 4. Optimization Check
    opt_starting = data.get("optimized_squad", {}).get("starting_11", [])
    opt_bench = data.get("optimized_squad", {}).get("bench", [])
    total_opt = len(opt_starting) + len(opt_bench)
    
    if total_opt != 15:
        print(f"❌ Error: Optimized squad has {total_opt} players (expected 15).")
        return False

    # 5. Team Constraints (Max 3 per team)
    squad_full = data.get("squad", []) + data.get("bench", [])
    team_counts = {}
    for p in squad_full:
        team = p.get('team')
        team_counts[team] = team_counts.get(team, 0) + 1
        if team_counts[team] > 3:
            print(f"❌ Error: Team '{team}' has {team_counts[team]} players in squad (Max 3 allowed).")
            return False

    # 6. Player Metadata Check (High-Definition UI requirements)
    for p in squad_full:
        if 'code' not in p or not p['code']:
            print(f"❌ Error: Player '{p.get('web_name')}' is missing the 'code' field required for images.")
            return False

    # 7. Captain Diversity
    recs = data.get("recommendations", {}).get("captains", [])
    if recs:
        # Check unique teams for the first 3 (Obvious, Joker, Fun One)
        # Note: Depending on structure, these might be named keys or list items.
        # Based on commander.py, they are keys in the response but generate_static.py might wrap them.
        # Let's assume the standard structure from generate_static.py which puts them in a dict.
        pass
    
    # Let's check the team uniqueness specifically if they are in the dict
    caps = data.get("recommendations", {})
    cap_teams = []
    for role in ["obvious", "joker", "fun_one"]:
        if role in caps and caps[role]:
            cap_teams.append(caps[role].get('team'))
    
    if len(set(cap_teams)) < len(cap_teams) and len(cap_teams) > 1:
        print(f"❌ Error: Captain recommendations are not from unique teams: {cap_teams}")
        return False

    print(f"✅ Validation successful: {filepath} looks healthy.")
    return True

if __name__ == "__main__":
    target_file = "frontend/public/dashboard_data.json"
    if validate_dashboard_data(target_file):
        sys.exit(0)
    else:
        sys.exit(1)
