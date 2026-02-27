"""
Football-Data.org API Client (GRATUITA)
Fetches live match data, team stats, and fixtures
Documentación: https://www.football-data.org/documentation/api
"""
import httpx
from typing import List, Optional
from datetime import datetime, timedelta

from src.core.config import settings
from src.core.cache import team_cache, api_cache
from src.domain.entities import Team, Match, MatchStatus


class FootballAPIClient:
    """
    Client for Football-Data.org API (FREE)
    
    Ligas disponibles en el tier gratuito:
    - PL: Premier League (Inglaterra)
    - PD: La Liga (España)
    - SA: Serie A (Italia)
    - BL1: Bundesliga (Alemania)
    - FL1: Ligue 1 (Francia)
    - CL: UEFA Champions League
    - EC: Campeonato Europeo
    - WC: Copa del Mundo
    """
    
    BASE_URL = "https://api.football-data.org/v4"
    
    # Códigos de ligas disponibles en tier gratuito
    LEAGUES = {
        "premier_league": "PL",
        "la_liga": "PD",
        "serie_a": "SA",
        "bundesliga": "BL1",
        "ligue_1": "FL1",
        "champions_league": "CL",
        "euro": "EC",
        "world_cup": "WC",
    }
    
    @classmethod
    def _get_headers(cls) -> dict:
        """Get API headers"""
        return {
            "X-Auth-Token": settings.FOOTBALL_DATA_API_KEY,
        }
    
    @classmethod
    async def get_team_by_name(cls, team_name: str) -> Optional[Team]:
        """Search for a team by name with caching"""
        if not settings.FOOTBALL_DATA_API_KEY:
            return cls._mock_team(team_name)
        
        cache_key = f"football_data_team:{team_name.lower()}"
        
        # Check cache first
        cached_team = await team_cache.get(cache_key)
        if cached_team is not None:
            return cached_team
        
        try:
            # Try to get teams list from cache
            teams_cache_key = "football_data_teams_list"
            teams = await api_cache.get(teams_cache_key)
            
            if not teams:
                async with httpx.AsyncClient() as client:
                    # Buscar en todas las competiciones
                    response = await client.get(
                        f"{cls.BASE_URL}/teams",
                        headers=cls._get_headers(),
                        params={"limit": 100}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        teams = data.get("teams", [])
                        # Cache teams list for 1 hour
                        await api_cache.set(teams_cache_key, teams, ttl=3600)
                    elif response.status_code == 429:
                        print("⚠️ Football-Data.org: Rate limit alcanzado (10 req/min en tier gratuito)")
                        return cls._mock_team(team_name)
                    else:
                        # Handle other error status codes (403, 500, etc.)
                        print(f"⚠️ Football-Data.org: Error {response.status_code} al obtener equipos")
                        return cls._mock_team(team_name)
            
            # Verificar que teams no sea None antes de iterar
            if teams is None:
                return cls._mock_team(team_name)
            
            # Buscar coincidencia por nombre
            for team_data in teams:
                if team_name.lower() in team_data["name"].lower() or \
                   team_name.lower() in team_data.get("shortName", "").lower():
                    # Try to get league from running competitions
                    league = ""
                    try:
                        running_competitions = team_data.get("runningCompetitions", [])
                        if running_competitions:
                            # Get the first active league (usually the main one)
                            league = running_competitions[0].get("name", "")
                    except Exception:
                        pass
                    
                    # Extract coach/manager info
                    manager = ""
                    try:
                        coach = team_data.get("coach")
                        if coach and isinstance(coach, dict):
                            manager = coach.get("name", "")
                    except Exception:
                        pass
                    
                    team = Team(
                        id=str(team_data["id"]),
                        name=team_data["name"],
                        short_name=team_data.get("tla", "")[:3],
                        logo_url=team_data.get("crest", ""),
                        country=team_data.get("area", {}).get("name", ""),
                        league=league,  # ✅ Incluir liga si está disponible
                        manager=manager,  # ✅ Extraer DT actual
                    )
                    # Cache individual team for 2 hours
                    await team_cache.set(cache_key, team, ttl=7200)
                    return team
        except Exception as e:
            print(f"Football-Data.org error: {e}")
        
        return cls._mock_team(team_name)
    
    @classmethod
    async def get_upcoming_fixtures(cls, league: str = "CL", limit: int = 10) -> List[Match]:
        """
        Get upcoming fixtures for a league
        
        Args:
            league: Código de liga (PL, PD, SA, BL1, FL1, CL, EC, WC)
            limit: Número máximo de partidos
        """
        if not settings.FOOTBALL_DATA_API_KEY:
            return cls._mock_fixtures()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{cls.BASE_URL}/competitions/{league}/matches",
                    headers=cls._get_headers(),
                    params={
                        "status": "SCHEDULED",
                        "limit": limit,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    matches = []
                    
                    for match_data in data.get("matches", [])[:limit]:
                        home = match_data["homeTeam"]
                        away = match_data["awayTeam"]
                        competition = match_data.get("competition", {})
                        
                        match = Match(
                            id=str(match_data["id"]),
                            home_team=Team(
                                id=str(home["id"]),
                                name=home["name"],
                                short_name=home.get("tla", "")[:3] if home.get("tla") else "",
                                logo_url=home.get("crest", ""),
                            ),
                            away_team=Team(
                                id=str(away["id"]),
                                name=away["name"],
                                short_name=away.get("tla", "")[:3] if away.get("tla") else "",
                                logo_url=away.get("crest", ""),
                            ),
                            date=datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")),
                            venue=match_data.get("venue", ""),
                            league=competition.get("name", league),
                            status=MatchStatus.SCHEDULED,
                        )
                        matches.append(match)
                    
                    return matches if matches else cls._mock_fixtures()
                    
                elif response.status_code == 429:
                    print("⚠️ Football-Data.org: Rate limit (10 req/min). Usando datos mock.")
                    
        except Exception as e:
            print(f"Football-Data.org fixtures error: {e}")
        
        return cls._mock_fixtures()
    
    @classmethod
    async def get_team_form(cls, team_id: str) -> str:
        """Get recent form (last 5 matches) for a team"""
        if not settings.FOOTBALL_DATA_API_KEY:
            return "WDWLW"  # Mock form
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{cls.BASE_URL}/teams/{team_id}/matches",
                    headers=cls._get_headers(),
                    params={
                        "status": "FINISHED",
                        "limit": 5,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    form = ""
                    
                    for match in data.get("matches", []):
                        home = match["homeTeam"]
                        away = match["awayTeam"]
                        score = match.get("score", {}).get("fullTime", {})
                        
                        home_goals = score.get("home", 0) or 0
                        away_goals = score.get("away", 0) or 0
                        
                        if str(home["id"]) == team_id:
                            if home_goals > away_goals:
                                form += "W"
                            elif home_goals < away_goals:
                                form += "L"
                            else:
                                form += "D"
                        else:
                            if away_goals > home_goals:
                                form += "W"
                            elif away_goals < home_goals:
                                form += "L"
                            else:
                                form += "D"
                    
                    return form or "DDDDD"
        except Exception as e:
            print(f"Football-Data.org form error: {e}")
        
        return "WDWLW"
    
    @classmethod
    async def get_standings(cls, league: str = "PL") -> List[dict]:
        """Get current standings for a league"""
        if not settings.FOOTBALL_DATA_API_KEY:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{cls.BASE_URL}/competitions/{league}/standings",
                    headers=cls._get_headers(),
                )
                
                if response.status_code == 200:
                    data = response.json()
                    standings = data.get("standings", [])
                    if standings:
                        return standings[0].get("table", [])
        except Exception as e:
            print(f"Football-Data.org standings error: {e}")
        
        return []
    
    @staticmethod
    def _mock_team(name: str) -> Team:
        """Return a team object when API is not available or team not found"""
        return Team(
            id=f"ext_{name.lower().replace(' ', '_')}",
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
            Match(
                id="mock_5",
                home_team=Team(id="juv", name="Juventus", short_name="JUV", logo_url=""),
                away_team=Team(id="atm", name="Atlético Madrid", short_name="ATM", logo_url=""),
                date=datetime.now() + timedelta(days=6),
                venue="Allianz Stadium",
                league="UEFA Champions League",
                status=MatchStatus.SCHEDULED,
            ),
        ]
