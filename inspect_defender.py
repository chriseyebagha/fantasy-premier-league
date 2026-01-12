import requests
import json

def inspect_defender_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    data = response.json()
    
    # Get a known high-performing defender (e.g., one of the top cost ones)
    defenders = [p for p in data['elements'] if p['element_type'] == 2]
    defenders.sort(key=lambda x: float(x['total_points']), reverse=True)
    top_defender = defenders[0]
    
    print(f"Top Defender: {top_defender['web_name']}")
    print("Keys available:")
    for k, v in top_defender.items():
        print(f"{k}: {v}")

    print("\nChecking specifically for defensive stats...")
    defensive_keys = ['clean_sheets', 'goals_conceded', 'own_goals', 'penalties_saved', 'saves', 'bps', 'influence', 'creativity', 'threat', 'ict_index']
    for k in defensive_keys:
        if k in top_defender:
            print(f"{k}: {top_defender[k]}")

if __name__ == "__main__":
    inspect_defender_data()
