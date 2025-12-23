"""
API-Football Client (api-sports.io)
Fetches real squad data, team info, and fixtures for ALL leagues including Liga Pro Ecuador

API Docs: https://www.api-football.com/documentation-v3
Free tier: 100 requests/day

Key endpoints:
- /teams?search={name} - Search teams
- /players/squads?team={id} - Get current squad
- /teams?country=Ecuador - Get all Ecuadorian teams
"""
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.core.config import settings
from src.domain.entities import Team


class APIFootballClient:
    """
    Client for API-Football (api-sports.io) - Real squad data for ALL leagues
    
    Covers:
    - Liga Pro Ecuador (Emelec, Barcelona SC, LDU, Independiente del Valle, etc.)
    - ALL South American leagues
    - European leagues
    - MLS, Liga MX, etc.
    """
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    # Cache for teams to avoid repeated API calls
    _team_cache: Dict[str, dict] = {}
    _squad_cache: Dict[str, List[dict]] = {}
    
    @classmethod
    def _get_headers(cls) -> dict:
        """Get API headers"""
        api_key = getattr(settings, 'API_FOOTBALL_KEY', None) or settings.FOOTBALL_DATA_API_KEY
        return {
            "x-apisports-key": api_key,
            "x-rapidapi-host": "v3.football.api-sports.io",
        }
    
    @classmethod
    async def search_team(cls, team_name: str) -> Optional[dict]:
        """
        Search for a team by name
        Returns raw API response with team data
        """
        cache_key = team_name.lower()
        if cache_key in cls._team_cache:
            return cls._team_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/teams",
                    headers=cls._get_headers(),
                    params={"search": team_name}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("errors"):
                        print(f"⚠️ API-Football error: {data['errors']}")
                        return None
                    
                    teams = data.get("response", [])
                    if teams:
                        # Return first match
                        team_data = teams[0]
                        cls._team_cache[cache_key] = team_data
                        print(f"✅ Found team: {team_data['team']['name']} (ID: {team_data['team']['id']})")
                        return team_data
                    
                    print(f"⚠️ No teams found for: {team_name}")
                    
        except Exception as e:
            print(f"❌ API-Football search error: {e}")
        
        return None
    
    @classmethod
    async def get_team_squad(cls, team_id: int) -> List[dict]:
        """
        Get current squad for a team
        Returns list of players with their info
        
        Response format per player:
        {
            "id": 123,
            "name": "Player Name",
            "age": 25,
            "number": 10,
            "position": "Midfielder",
            "photo": "url"
        }
        """
        cache_key = str(team_id)
        if cache_key in cls._squad_cache:
            return cls._squad_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/players/squads",
                    headers=cls._get_headers(),
                    params={"team": team_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("errors"):
                        print(f"⚠️ API-Football squad error: {data['errors']}")
                        return []
                    
                    squads = data.get("response", [])
                    if squads and squads[0].get("players"):
                        players = squads[0]["players"]
                        cls._squad_cache[cache_key] = players
                        print(f"✅ Found {len(players)} players for team {team_id}")
                        return players
                        
        except Exception as e:
            print(f"❌ API-Football squad error: {e}")
        
        return []
    
    @classmethod
    async def get_team_with_squad(cls, team_name: str) -> Optional[dict]:
        """
        Get team info AND full squad in one call sequence
        Returns:
        {
            "team": Team entity,
            "players": [{"name": "...", "position": "...", "overall": 75}, ...]
        }
        """
        # First search for the team
        team_data = await cls.search_team(team_name)
        if not team_data:
            return None
        
        team_info = team_data["team"]
        venue = team_data.get("venue", {})
        
        team = Team(
            id=f"apif_{team_info['id']}",
            name=team_info["name"],
            short_name=team_info.get("code", team_info["name"][:3].upper()),
            logo_url=team_info.get("logo", ""),
            country=team_info.get("country", ""),
            venue=venue.get("name", ""),
        )
        
        # Then get the squad
        players = await cls.get_team_squad(team_info["id"])
        
        # Convert to our format with estimated overall ratings
        player_list = []
        for p in players:
            position = p.get("position", "Unknown")
            # Estimate overall based on position and team level
            base_overall = 72
            if position == "Goalkeeper":
                base_overall = 74
            elif position == "Defender":
                base_overall = 73
            elif position == "Midfielder":
                base_overall = 75
            elif position == "Attacker":
                base_overall = 76
            
            # Add some variation
            import random
            overall = base_overall + random.randint(-3, 5)
            
            player_list.append({
                "name": p["name"],
                "position": cls._map_position(position),
                "overall": min(88, max(65, overall)),
                "number": p.get("number"),
                "age": p.get("age"),
                "photo": p.get("photo"),
            })
        
        return {
            "team": team,
            "players": player_list,
        }
    
    @staticmethod
    def _map_position(api_position: str) -> str:
        """Map API-Football positions to our format"""
        position_map = {
            "Goalkeeper": "GK",
            "Defender": "CB",
            "Midfielder": "CM",
            "Attacker": "FW",
        }
        return position_map.get(api_position, "CM")
    
    @classmethod
    async def get_country_teams(cls, country: str = "Ecuador") -> List[dict]:
        """Get all teams from a specific country"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/teams",
                    headers=cls._get_headers(),
                    params={"country": country}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", [])
                    
        except Exception as e:
            print(f"❌ API-Football country teams error: {e}")
        
        return []
    
    @classmethod
    async def get_fixtures(cls, league_id: int = 242, season: int = 2024) -> List[dict]:
        """
        Get fixtures for a league
        
        Ecuador Liga Pro ID: 242
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/fixtures",
                    headers=cls._get_headers(),
                    params={
                        "league": league_id,
                        "season": season,
                        "next": 10,  # Next 10 matches
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", [])
                    
        except Exception as e:
            print(f"❌ API-Football fixtures error: {e}")
        
        return []


# Ecuadorian teams reference (for fallback)
ECUADORIAN_TEAMS = {
    "emelec": {"id": 1146, "name": "Emelec", "city": "Guayaquil"},
    "barcelona sc": {"id": 1145, "name": "Barcelona SC", "city": "Guayaquil"},
    "ldu quito": {"id": 1149, "name": "LDU Quito", "city": "Quito"},
    "independiente del valle": {"id": 2283, "name": "Independiente del Valle", "city": "Sangolquí"},
    "deportivo cuenca": {"id": 1151, "name": "Deportivo Cuenca", "city": "Cuenca"},
    "el nacional": {"id": 1147, "name": "El Nacional", "city": "Quito"},
    "aucas": {"id": 1148, "name": "Aucas", "city": "Quito"},
    "macara": {"id": 1150, "name": "Macará", "city": "Ambato"},
    "mushuc runa": {"id": 2284, "name": "Mushuc Runa", "city": "Ambato"},
    "delfin": {"id": 2282, "name": "Delfín", "city": "Manta"},
    "universidad catolica": {"id": 1152, "name": "Universidad Católica", "city": "Quito"},
    "orense": {"id": 3640, "name": "Orense", "city": "Machala"},
    "tecnico universitario": {"id": 1153, "name": "Técnico Universitario", "city": "Ambato"},
}
