"""
Unified API Selector with Fallback Strategy
Tries multiple APIs in order of preference to ensure reliability and cost efficiency
"""
from typing import Optional, List
from src.infrastructure.external_api.thesportsdb import TheSportsDBClient
from src.infrastructure.external_api.api_football import APIFootballClient
from src.infrastructure.external_api.football_api import FootballAPIClient
from src.domain.entities import Team


class UnifiedAPIClient:
    """
    Unified client that tries multiple APIs with smart fallback
    
    Strategy:
    1. Try TheSportsDB first (FREE, 100k req/day, no API key)
    2. Fallback to Football-Data.org (FREE, 10 req/min)
    3. Fallback to API-Football (100 req/day free, better coverage)
    
    This ensures:
    - Maximum cost efficiency (prioritize free APIs)
    - High reliability (multiple fallbacks)
    - Better coverage (complementary APIs)
    """
    
    @classmethod
    async def get_team_by_name(cls, team_name: str) -> Optional[Team]:
        """
        Get team by name, trying multiple APIs with fallback
        """
        # Try 1: TheSportsDB (FREE, no API key needed)
        try:
            team_data = await TheSportsDBClient.search_team(team_name)
            if team_data:
                # Get detailed team info to ensure we have league data
                team_id = team_data.get("idTeam")
                if team_id:
                    detailed_team = await TheSportsDBClient.get_team_by_id(team_id)
                    if detailed_team:
                        team_data = detailed_team
                
                return Team(
                    id=f"tsdb_{team_data.get('idTeam')}",
                    name=team_data.get("strTeam", team_name),
                    short_name=team_data.get("strTeamShort", team_data.get("strTeam", team_name)[:3].upper()),
                    logo_url=team_data.get("strTeamBadge", ""),
                    country=team_data.get("strCountry", ""),
                    league=team_data.get("strLeague", ""),  # ✅ Extraer liga
                )
        except Exception as e:
            print(f"⚠️ TheSportsDB failed: {e}, trying fallback...")
        
        # Try 2: Football-Data.org (FREE, 10 req/min)
        try:
            team = await FootballAPIClient.get_team_by_name(team_name)
            if team:
                return team
        except Exception as e:
            print(f"⚠️ Football-Data.org failed: {e}, trying fallback...")
        
        # Try 3: API-Football (100 req/day free, better coverage)
        try:
            team_data = await APIFootballClient.search_team(team_name)
            if team_data:
                team_info = team_data.get("team", {})
                league_info = team_data.get("league", {})
                return Team(
                    id=f"apif_{team_info.get('id')}",
                    name=team_info.get("name", team_name),
                    short_name=team_info.get("code", team_info.get("name", team_name)[:3].upper()),
                    logo_url=team_info.get("logo", ""),
                    country=team_info.get("country", ""),
                    league=league_info.get("name", ""),  # ✅ Extraer liga de API-Football
                )
        except Exception as e:
            print(f"⚠️ API-Football failed: {e}")
        
        return None
    
    @classmethod
    async def get_team_squad(cls, team_name: str, team_id: Optional[str] = None) -> List[dict]:
        """
        Get team squad, trying multiple APIs with fallback
        """
        # Try 1: TheSportsDB first (FREE)
        try:
            if team_id and team_id.startswith("tsdb_"):
                actual_id = team_id.replace("tsdb_", "")
                players = await TheSportsDBClient.get_team_squad(actual_id)
                if players:
                    return players
        except Exception as e:
            print(f"⚠️ TheSportsDB squad failed: {e}, trying fallback...")
        
        # Try 2: API-Football (better squad data)
        try:
            if team_id and team_id.startswith("apif_"):
                actual_id = int(team_id.replace("apif_", ""))
                players = await APIFootballClient.get_team_squad(actual_id)
                if players:
                    return players
        except Exception as e:
            print(f"⚠️ API-Football squad failed: {e}")
        
        # Try 3: Search team first, then get squad
        try:
            team_data = await TheSportsDBClient.search_team(team_name)
            if team_data:
                team_id = team_data.get("idTeam")
                if team_id:
                    players = await TheSportsDBClient.get_team_squad(team_id)
                    if players:
                        return players
        except Exception as e:
            print(f"⚠️ TheSportsDB search+squad failed: {e}")
        
        return []
    
    @classmethod
    async def get_team_with_squad(cls, team_name: str) -> Optional[dict]:
        """
        Get team info AND squad, trying multiple APIs with fallback
        """
        # Try TheSportsDB first (FREE, good coverage)
        try:
            result = await TheSportsDBClient.get_team_with_squad(team_name)
            if result and result.get("team") and result.get("players"):
                return result
        except Exception as e:
            print(f"⚠️ TheSportsDB get_team_with_squad failed: {e}, trying fallback...")
        
        # Fallback to API-Football (better coverage, but limited free tier)
        try:
            result = await APIFootballClient.get_team_with_squad(team_name)
            if result:
                return result
        except Exception as e:
            print(f"⚠️ API-Football get_team_with_squad failed: {e}")
        
        return None

