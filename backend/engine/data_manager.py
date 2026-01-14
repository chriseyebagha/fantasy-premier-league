import requests
import os
from typing import Dict, List, Optional
from functools import lru_cache

class FPLDataManager:
    """Robust interface for the official FPL API."""
    
    BASE_URL = "https://fantasy.premierleague.com/api"
    
    def __init__(self):
        self.session = requests.Session()

    def get_bootstrap_static(self) -> Dict:
        """Fetches core game data (players, teams, events)."""
        response = self.session.get(f"{self.BASE_URL}/bootstrap-static/")
        response.raise_for_status()
        return response.json()

    def get_fixtures(self, event: Optional[int] = None) -> List[Dict]:
        """Fetches fixtures, optionally filtered by gameweek."""
        url = f"{self.BASE_URL}/fixtures/"
        if event:
            url += f"?event={event}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    @lru_cache(maxsize=1000)
    def get_player_summary(self, player_id: int) -> Dict:
        """Fetches detailed history and upcoming fixtures for a player."""
        response = self.session.get(f"{self.BASE_URL}/element-summary/{player_id}/")
        response.raise_for_status()
        return response.json()

    def get_raw_xg_xa_data(self, player_id: int) -> List[Dict]:
        """Extracts historical xG and xA from player history."""
        summary = self.get_player_summary(player_id)
        return summary.get('history', [])

    def get_upcoming_gameweek(self, bootstrap_data: Dict) -> int:
        """Determines the next active gameweek."""
        events = bootstrap_data.get('events', [])
        for event in events:
            if event.get('is_next'):
                return event.get('id', 1)
        return 1

    def get_actual_events(self, gameweek: int) -> Dict[int, Dict]:
        """Fetches detailed actual performance stats for all players in a specific gameweek using the Live API."""
        print(f"📡 Fetching live event data for GW{gameweek}...")
        
        response = self.session.get(f"{self.BASE_URL}/event/{gameweek}/live/")
        response.raise_for_status()
        data = response.json()
        
        actual_events = {}
        for item in data.get('elements', []):
            stats = item.get('stats', {})
            actual_events[item['id']] = {
                "total_points": float(stats.get('total_points', 0)),
                "goals_scored": int(stats.get('goals_scored', 0)),
                "assists": int(stats.get('assists', 0)),
                "clean_sheets": int(stats.get('clean_sheets', 0)),
                "goals_conceded": int(stats.get('goals_conceded', 0)),
                "saves": int(stats.get('saves', 0)),
                "bonus": int(stats.get('bonus', 0)),
                "yellow_cards": int(stats.get('yellow_cards', 0)),
                "red_cards": int(stats.get('red_cards', 0)),
                "minutes": int(stats.get('minutes', 0)),
                "defensive_contribution": int(stats.get('defensive_contribution', 0))
            }
            
        return actual_events
