"""
API-Football Client (RapidAPI)
Fetches live match data, team stats, and fixtures
"""
import httpx
from typing import List, Optional
from datetime import datetime, timedelta

from src.core.config import settings
from src.domain.entities import Team, Match, MatchStatus


class FootballAPIClient:
    """Client for API-Football (RapidAPI)"""
    
    BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    
    @classmethod
    def _get_headers(cls) -> dict:
        """Get API headers"""
        return {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
        }
    
    @classmethod
    async def get_team_by_name(cls, team_name: str) -> Optional[Team]:
        """Search for a team by name"""
        if not settings.RAPIDAPI_KEY:
            return cls._mock_team(team_name)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{cls.BASE_URL}/teams",
                    headers=cls._get_headers(),
                    params={"search": team_name}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("response"):
                        team_data = data["response"][0]["team"]
                        return Team(
                            id=str(team_data["id"]),
                            name=team_data["name"],
                            short_name=team_data.get("code", ""),
                            logo_url=team_data.get("logo", ""),
                            country=team_data.get("country", ""),
                        )
        except Exception as e:
            print(f"API-Football error: {e}")
        
        return cls._mock_team(team_name)
    
    @classmethod
    async def get_upcoming_fixtures(cls, league_id: int = 39, limit: int = 10) -> List[Match]:
        """Get upcoming fixtures for a league (default: Premier League)"""
        if not settings.RAPIDAPI_KEY:
            return cls._mock_fixtures()
        
        try:
            async with httpx.AsyncClient() as client:
                today = datetime.now().strftime("%Y-%m-%d")
                next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                
                response = await client.get(
                    f"{cls.BASE_URL}/fixtures",
                    headers=cls._get_headers(),
                    params={
                        "league": league_id,
                        "from": today,
                        "to": next_week,
                        "season": 2024,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    matches = []
                    
                    for fixture in data.get("response", [])[:limit]:
                        home = fixture["teams"]["home"]
                        away = fixture["teams"]["away"]
                        
                        match = Match(
                            id=str(fixture["fixture"]["id"]),
                            home_team=Team(
                                id=str(home["id"]),
                                name=home["name"],
                                logo_url=home.get("logo", ""),
                            ),
                            away_team=Team(
                                id=str(away["id"]),
                                name=away["name"],
                                logo_url=away.get("logo", ""),
                            ),
                            date=datetime.fromisoformat(fixture["fixture"]["date"].replace("Z", "+00:00")),
                            venue=fixture["fixture"]["venue"]["name"] if fixture["fixture"].get("venue") else "",
                            league=fixture["league"]["name"],
                            status=MatchStatus.SCHEDULED,
                        )
                        matches.append(match)
                    
                    return matches
        except Exception as e:
            print(f"API-Football fixtures error: {e}")
        
        return cls._mock_fixtures()
    
    @classmethod
    async def get_team_form(cls, team_id: str) -> str:
        """Get recent form (last 5 matches) for a team"""
        if not settings.RAPIDAPI_KEY:
            return "WDWLW"  # Mock form
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{cls.BASE_URL}/fixtures",
                    headers=cls._get_headers(),
                    params={
                        "team": team_id,
                        "last": 5,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    form = ""
                    
                    for fixture in data.get("response", []):
                        home = fixture["teams"]["home"]
                        away = fixture["teams"]["away"]
                        goals = fixture.get("goals", {})
                        
                        if str(home["id"]) == team_id:
                            if home.get("winner"):
                                form += "W"
                            elif away.get("winner"):
                                form += "L"
                            else:
                                form += "D"
                        else:
                            if away.get("winner"):
                                form += "W"
                            elif home.get("winner"):
                                form += "L"
                            else:
                                form += "D"
                    
                    return form or "DDDDD"
        except Exception as e:
            print(f"API-Football form error: {e}")
        
        return "WDWLW"
    
    @staticmethod
    def _mock_team(name: str) -> Team:
        """Return a mock team when API is not available"""
        return Team(
            id=f"mock_{name.lower().replace(' ', '_')}",
            name=name,
            short_name=name[:3].upper(),
            logo_url="",
            country="Unknown",
            form="WDWLW",
        )
    
    @staticmethod
    def _mock_fixtures() -> List[Match]:
        """Return mock fixtures when API is not available"""
        return [
            Match(
                id="mock_1",
                home_team=Team(id="rm", name="Real Madrid", short_name="RMA", logo_url=""),
                away_team=Team(id="mc", name="Manchester City", short_name="MCI", logo_url=""),
                date=datetime.now() + timedelta(days=2),
                venue="Santiago Bernabéu",
                league="UEFA Champions League",
                status=MatchStatus.SCHEDULED,
            ),
            Match(
                id="mock_2",
                home_team=Team(id="fcb", name="Barcelona", short_name="BAR", logo_url=""),
                away_team=Team(id="bay", name="Bayern Munich", short_name="BAY", logo_url=""),
                date=datetime.now() + timedelta(days=3),
                venue="Camp Nou",
                league="UEFA Champions League",
                status=MatchStatus.SCHEDULED,
            ),
            Match(
                id="mock_3",
                home_team=Team(id="liv", name="Liverpool", short_name="LIV", logo_url=""),
                away_team=Team(id="ars", name="Arsenal", short_name="ARS", logo_url=""),
                date=datetime.now() + timedelta(days=4),
                venue="Anfield",
                league="Premier League",
                status=MatchStatus.SCHEDULED,
            ),
            Match(
                id="mock_4",
                home_team=Team(id="psg", name="Paris Saint-Germain", short_name="PSG", logo_url=""),
                away_team=Team(id="int", name="Inter Milan", short_name="INT", logo_url=""),
                date=datetime.now() + timedelta(days=5),
                venue="Parc des Princes",
                league="UEFA Champions League",
                status=MatchStatus.SCHEDULED,
            ),
        ]
