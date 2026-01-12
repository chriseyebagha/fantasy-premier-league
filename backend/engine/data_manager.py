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

    def get_actual_points(self, gameweek: int) -> Dict[int, float]:
        """Fetches actual points scored by all players in a specific gameweek."""
        bootstrap = self.get_bootstrap_static()
        players = bootstrap['elements']
        actual_points = {}
        
        # We need individual summaries to get historical points for a specific GW
        # However, for efficiency, if it's a past GW, we can often find it in player history
        for p in players:
            summary = self.get_player_summary(p['id'])
            history = summary.get('history', [])
            for entry in history:
                if entry['round'] == gameweek:
                    actual_points[p['id']] = float(entry['total_points'])
                    break
        return actual_points
