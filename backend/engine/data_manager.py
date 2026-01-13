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
        
        # Optimization: Check if the requested gameweek is the "current" one in bootstrap
        # If so, we can simply use p['event_points'] instead of 600+ API calls
        is_current_gw = False
        for event in bootstrap['events']:
            if event['id'] == gameweek and event.get('is_current', False):
                is_current_gw = True
                break
        
        if is_current_gw:
            print(f"GW{gameweek} is current. Using bootstrap data for points (Fast).")
            for p in players:
                actual_points[p['id']] = float(p['event_points'])
            return actual_points

        print(f"GW{gameweek} is historical. Fetching individual summaries (Slow)...")
        # Fallback: We need individual summaries to get historical points
        count = 0
        for p in players:
            summary = self.get_player_summary(p['id'])
            history = summary.get('history', [])
            for entry in history:
                if entry['round'] == gameweek:
                    actual_points[p['id']] = float(entry['total_points'])
                    break
            count += 1
            if count % 50 == 0: print(f"Fetched {count}/{len(players)}...", end='\r')
            
        return actual_points
