"""
TheSportsDB API Client (100% GRATUITA)
Fetches team data, players, fixtures, and match information
No API key required! 100,000 requests/day free tier

API Docs: https://www.thesportsdb.com/api.php
Free tier: 100,000 requests/day (NO API KEY REQUIRED!)

Key endpoints:
- /searchteams.php?t={name} - Search teams
- /lookupteam.php?id={id} - Get team details
- /lookup_all_players.php?id={team_id} - Get team squad
- /eventsnext.php?id={team_id} - Get next fixtures
- /eventslast.php?id={team_id} - Get last matches
- /searchplayers.php?t={name} - Search players
"""

from datetime import datetime

import httpx

from src.core.cache import api_cache, squad_cache, team_cache
from src.domain.entities import Team


class TheSportsDBClient:
    """
    Client for TheSportsDB API (100% FREE, NO API KEY REQUIRED)

    Benefits:
    - ✅ Completely free (no API key needed)
    - ✅ 100,000 requests/day limit (very generous!)
    - ✅ Good coverage of major leagues
    - ✅ Team logos and player photos
    - ✅ Historical and upcoming matches
    - ✅ Perfect for development and production

    Covers:
    - Major European leagues (Premier League, La Liga, Serie A, etc.)
    - MLS, Liga MX
    - Some South American leagues
    - International competitions
    """

    BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

    @classmethod
    def _get_headers(cls) -> dict:
        """Get API headers (no authentication needed!)"""
        return {
            "Accept": "application/json",
        }

    @classmethod
    async def search_team(cls, team_name: str) -> dict | None:
        """
        Search for a team by name
        Returns raw API response with team data
        Uses TTL cache to reduce API calls
        """
        cache_key = f"thesportsdb_team_search:{team_name.lower()}"

        # Check cache first
        cached_result = await team_cache.get(cache_key)
        if cached_result is not None:
            cached_name = cached_result.get("strTeam", "").lower()
            # Validar que el cache coincide con la búsqueda
            if team_name.lower() in cached_name or cached_name in team_name.lower():
                print(f"✅ Cache hit for team: {team_name}")
                return cached_result
            else:
                print(
                    f"⚠️ Cache mismatch for search '{team_name}': got '{cached_name}', deleting corrupted cache"
                )
                await team_cache.delete(cache_key)

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/searchteams.php",
                    headers=cls._get_headers(),
                    params={"t": team_name},
                )

                if response.status_code == 200:
                    data = response.json()

                    teams = data.get("teams", [])
                    if teams and len(teams) > 0:
                        # Find the best match (prefer exact or partial match)
                        team_data = None
                        for t in teams:
                            t_name = t.get("strTeam", "").lower()
                            if team_name.lower() in t_name or t_name in team_name.lower():
                                team_data = t
                                break

                        # If no good match, use first result
                        if not team_data:
                            team_data = teams[0]

                        # Cache only if name matches reasonably
                        result_name = team_data.get("strTeam", "").lower()
                        if team_name.lower() in result_name or result_name in team_name.lower():
                            await team_cache.set(cache_key, team_data)

                        print(
                            f"✅ Found team: {team_data.get('strTeam', team_name)} (ID: {team_data.get('idTeam')})"
                        )
                        return team_data

                    print(f"⚠️ No teams found for: {team_name}")

        except Exception as e:
            print(f"❌ TheSportsDB search error: {e}")

        return None

    @classmethod
    async def get_team_by_id(cls, team_id: str) -> dict | None:
        """Get detailed team information by ID"""
        cache_key = f"thesportsdb_team:{team_id}"

        # Check cache first
        cached_result = await team_cache.get(cache_key)
        if cached_result is not None:
            # Validar que el cache tiene el ID correcto
            if str(cached_result.get("idTeam")) == str(team_id):
                return cached_result
            else:
                print(
                    f"⚠️ Cache mismatch for team {team_id}: got {cached_result.get('idTeam')}, deleting corrupted cache"
                )
                await team_cache.delete(cache_key)

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/lookupteam.php",
                    headers=cls._get_headers(),
                    params={"id": team_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    teams = data.get("teams", [])
                    if teams and len(teams) > 0:
                        team_data = teams[0]
                        # Validar que el equipo devuelto coincide con el ID solicitado
                        if str(team_data.get("idTeam")) == str(team_id):
                            # Cache for 2 hours (team_cache TTL is 7200 seconds)
                            await team_cache.set(cache_key, team_data)
                            return team_data
                        else:
                            print(
                                f"⚠️ API returned wrong team ID: expected {team_id}, got {team_data.get('idTeam')}"
                            )

        except Exception as e:
            print(f"❌ TheSportsDB get team error: {e}")

        return None

    @classmethod
    async def get_team_squad(cls, team_id: str) -> list[dict]:
        """
        Get current squad for a team
        Returns list of players with their info

        Response format per player:
        {
            "idPlayer": "123",
            "strPlayer": "Player Name",
            "strPosition": "Midfielder",
            "dateBorn": "1995-01-01",
            "strNationality": "Country",
            "strThumb": "photo_url"
        }
        Uses TTL cache (1 hour) since squads change less frequently
        """
        cache_key = f"thesportsdb_squad:{team_id}"

        # Check cache first
        cached_result = await squad_cache.get(cache_key)
        if cached_result is not None:
            print(f"✅ Cache hit for squad: {team_id}")
            return cached_result

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/lookup_all_players.php",
                    headers=cls._get_headers(),
                    params={"id": team_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    players = data.get("player", [])
                    if players:
                        # Cache for 30 minutes (squad_cache TTL is 1800 seconds)
                        await squad_cache.set(cache_key, players)
                        print(f"✅ Found {len(players)} players for team {team_id}")
                        return players

        except Exception as e:
            print(f"❌ TheSportsDB squad error: {e}")

        return []

    @classmethod
    async def get_team_with_squad(cls, team_name: str) -> dict | None:
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

        team_id = team_data.get("idTeam")
        if not team_id:
            return None

        # Get detailed team info
        detailed_team = await cls.get_team_by_id(team_id)
        if detailed_team:
            team_data = detailed_team

        # Then get the squad
        players_raw = await cls.get_team_squad(team_id)

        # Extract manager from squad (TheSportsDB lists manager as a player with position "Manager")
        manager_name = team_data.get("strManager", "")
        if not manager_name:
            for p in players_raw:
                if p.get("strPosition", "").lower() == "manager":
                    manager_name = p.get("strPlayer", "")
                    break

        # Update team entity with manager
        team = Team(
            id=f"tsdb_{team_id}",
            name=team_data.get("strTeam", team_name),
            short_name=team_data.get(
                "strTeamShort", team_data.get("strTeam", team_name)[:3].upper()
            ),
            logo_url=team_data.get("strTeamBadge", ""),
            country=team_data.get("strCountry", ""),
            league=team_data.get("strLeague", ""),
            manager=manager_name,  # ✅ DT extraído del squad o del team data
        )

        # Convert to our format with estimated overall ratings — skip the manager
        player_list = []
        for p in players_raw:
            position = p.get("strPosition", "Midfielder")
            # Skip manager entry — not a player
            if position.lower() == "manager":
                continue
            # Estimate overall based on position and team level
            base_overall = 72
            if position in ["Goalkeeper", "GK"]:
                base_overall = 74
            elif position in ["Defender", "CB", "LB", "RB"]:
                base_overall = 73
            elif position in ["Midfielder", "CM", "CDM", "CAM"]:
                base_overall = 75
            elif position in ["Attacker", "Forward", "FW", "ST", "LW", "RW"]:
                base_overall = 76

            # Add some variation
            import random

            overall = base_overall + random.randint(-3, 5)

            player_list.append(
                {
                    "name": p.get("strPlayer", "Unknown"),
                    "position": cls._map_position(position),
                    "overall": min(88, max(65, overall)),
                    "number": p.get("strNumber"),
                    "age": cls._calculate_age(p.get("dateBorn")),
                    "photo": p.get("strThumb", ""),
                }
            )

        return {
            "team": team,
            "players": player_list,
        }

    @classmethod
    async def get_upcoming_fixtures(cls, team_id: str, limit: int = 10) -> list[dict]:
        """Get upcoming fixtures for a team"""
        cache_key = f"thesportsdb_fixtures:{team_id}:next"

        # Check cache first
        cached_result = await api_cache.get(cache_key)
        if cached_result is not None:
            return cached_result[:limit] if cached_result else []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/eventsnext.php",
                    headers=cls._get_headers(),
                    params={"id": team_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    events = data.get("events", [])
                    if events:
                        # Cache for 1 hour (api_cache TTL is 3600 seconds)
                        await api_cache.set(cache_key, events)
                        return events[:limit]

        except Exception as e:
            print(f"❌ TheSportsDB fixtures error: {e}")

        return []

    @classmethod
    async def get_last_matches(cls, team_id: str, limit: int = 5) -> list[dict]:
        """Get last matches for a team (for form calculation)"""
        cache_key = f"thesportsdb_fixtures:{team_id}:last"

        # Check cache first
        cached_result = await api_cache.get(cache_key)
        if cached_result is not None:
            return cached_result[:limit] if cached_result else []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/eventslast.php",
                    headers=cls._get_headers(),
                    params={"id": team_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    events = data.get("results", [])
                    if events:
                        # Cache for 1 hour (api_cache TTL is 3600 seconds)
                        await api_cache.set(cache_key, events)
                        return events[:limit]

        except Exception as e:
            print(f"❌ TheSportsDB last matches error: {e}")

        return []

    @staticmethod
    def _map_position(api_position: str) -> str:
        """Map TheSportsDB positions to our format"""
        position_map = {
            "Goalkeeper": "GK",
            "GK": "GK",
            "Defender": "CB",
            "CB": "CB",
            "Centre-Back": "CB",
            "Left-Back": "LB",
            "LB": "LB",
            "Right-Back": "RB",
            "RB": "RB",
            "Midfielder": "CM",
            "CM": "CM",
            "Central Midfielder": "CM",
            "Defensive Midfielder": "CDM",
            "CDM": "CDM",
            "Attacking Midfielder": "CAM",
            "CAM": "CAM",
            "Forward": "FW",
            "FW": "FW",
            "Striker": "ST",
            "ST": "ST",
            "Left Wing": "LW",
            "LW": "LW",
            "Right Wing": "RW",
            "RW": "RW",
        }
        return position_map.get(api_position, "CM")

    @staticmethod
    def _calculate_age(birth_date: str | None) -> int | None:
        """Calculate age from birth date"""
        if not birth_date:
            return None

        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except Exception:
            return None

    @classmethod
    async def search_players(cls, player_name: str, limit: int = 20) -> list[dict]:
        """Search for players by name"""
        cache_key = f"thesportsdb_player_search:{player_name.lower()}"

        # Check cache first
        cached_result = await api_cache.get(cache_key)
        if cached_result is not None:
            return cached_result[:limit] if cached_result else []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/searchplayers.php",
                    headers=cls._get_headers(),
                    params={"p": player_name},
                )

                if response.status_code == 200:
                    data = response.json()
                    players = data.get("player", [])
                    if players:
                        # Cache for 1 hour (api_cache TTL is 3600 seconds)
                        await api_cache.set(cache_key, players)
                        return players[:limit]

        except Exception as e:
            print(f"❌ TheSportsDB player search error: {e}")

        return []
