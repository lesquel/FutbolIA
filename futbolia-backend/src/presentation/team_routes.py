"""
Team API Routes
Handles team search, creation, and player management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from src.domain.entities import Team, PlayerAttributes
from src.infrastructure.db.team_repository import TeamRepository
from src.infrastructure.chromadb.player_store import PlayerVectorStore
from src.infrastructure.external_api.football_api import FootballAPIClient
from src.infrastructure.external_api.api_selector import UnifiedAPIClient
from src.presentation.auth_routes import get_current_user, get_optional_user
from src.core.cache import api_cache
import asyncio


router = APIRouter(prefix="/teams", tags=["Teams"])


# ==================== League Mapping ====================
# Solo Premier League 2025-2026
ALLOWED_LEAGUES = {
    "Premier League",
    "English Premier League",  # Nombre usado por TheSportsDB
}

# Mapeo de equipos de Premier League 2025-2026 (todos los 20 equipos + variantes)
LEAGUE_MAPPING = {
    # Premier League 2025-2026 - Equipos actuales
    "Manchester City": "Premier League",
    "Liverpool": "Premier League",
    "Arsenal": "Premier League",
    "Chelsea": "Premier League",
    "Chelsea FC": "Premier League",
    "Tottenham": "Premier League",
    "Tottenham Hotspur": "Premier League",
    "Tottenham Hotspur FC": "Premier League",
    "Manchester United": "Premier League",
    "Manchester United FC": "Premier League",
    "Newcastle United": "Premier League",
    "Newcastle United FC": "Premier League",
    "Newcastle": "Premier League",
    "Brighton": "Premier League",
    "Brighton & Hove Albion": "Premier League",
    "Brighton & Hove Albion FC": "Premier League",
    "West Ham": "Premier League",
    "West Ham United": "Premier League",
    "West Ham United FC": "Premier League",
    "Aston Villa": "Premier League",
    "Aston Villa FC": "Premier League",
    "Crystal Palace": "Premier League",
    "Crystal Palace FC": "Premier League",
    "Wolverhampton Wanderers": "Premier League",
    "Wolverhampton Wanderers FC": "Premier League",
    "Wolves": "Premier League",
    "Fulham": "Premier League",
    "Fulham FC": "Premier League",
    "Brentford": "Premier League",
    "Brentford FC": "Premier League",
    "Nottingham Forest": "Premier League",
    "Nottingham Forest FC": "Premier League",
    "Everton": "Premier League",
    "Everton FC": "Premier League",
    "Bournemouth": "Premier League",
    "AFC Bournemouth": "Premier League",
    "Sheffield United": "Premier League",
    "Sheffield United FC": "Premier League",
    "Burnley": "Premier League",
    "Burnley FC": "Premier League",
    "Luton Town": "Premier League",
    "Luton Town FC": "Premier League",
    "Leicester City": "Premier League",
    "Leicester City FC": "Premier League",
    "Southampton": "Premier League",
    "Southampton FC": "Premier League",
    "Ipswich Town": "Premier League",
    "Ipswich Town FC": "Premier League",
    "Leeds United": "Premier League",
    "Leeds United FC": "Premier League",
    "Sunderland": "Premier League",
    "Sunderland AFC": "Premier League",
}


def is_team_in_allowed_league(team_name: str, team_league: str = "") -> bool:
    """Verifica si un equipo pertenece a una de las 5 ligas permitidas"""
    if team_league and team_league in ALLOWED_LEAGUES:
        return True
    mapped_league = LEAGUE_MAPPING.get(team_name, "")
    return mapped_league in ALLOWED_LEAGUES


def get_team_league(team_name: str) -> str:
    """Obtener la liga de un equipo usando el mapeo"""
    return LEAGUE_MAPPING.get(team_name, "")


# ==================== Request/Response Models ====================

class TeamResponse(BaseModel):
    id: str
    name: str
    short_name: str
    logo_url: str
    country: str = ""
    league: str = ""
    has_players: bool = False
    player_count: int = 0


class PlayerCreate(BaseModel):
    name: str
    position: str = "CM"
    overall_rating: int = Field(ge=1, le=99, default=75)
    pace: int = Field(ge=1, le=99, default=70)
    shooting: int = Field(ge=1, le=99, default=70)
    passing: int = Field(ge=1, le=99, default=70)
    dribbling: int = Field(ge=1, le=99, default=70)
    defending: int = Field(ge=1, le=99, default=70)
    physical: int = Field(ge=1, le=99, default=70)


class TeamCreate(BaseModel):
    name: str
    short_name: str = ""
    logo_url: str = ""
    country: str = ""
    league: str = ""
    players: Optional[List[PlayerCreate]] = None


class BulkTeamsCreate(BaseModel):
    teams: List[TeamCreate]


class SearchTeamsRequest(BaseModel):
    query: str
    search_api: bool = True  # Also search in Football-Data.org API


# ==================== Routes ====================

@router.get("/search")
async def search_teams(
    q: str = Query(..., min_length=2, description="Search query"),
    search_api: bool = Query(True, description="Also search in external API"),
    limit: int = Query(20, le=50)
):
    """
    🔍 Search teams in database and optionally in Football-Data.org API
    
    Returns teams from:
    1. Local database (teams added by users)
    2. ChromaDB (teams with player data)
    3. Football-Data.org API (if search_api=True)
    """
    results = {
        "local": [],
        "with_players": [],
        "api": [],
    }
    
    # Search in local database
    local_teams = await TeamRepository.search(q, limit=limit)
    
    # ✅ Usar el valor real de has_players y player_count del equipo
    results["local"] = [
        _team_to_response(
            t, 
            has_players=getattr(t, 'has_players', False), 
            player_count=getattr(t, 'player_count', 0)
        ) 
        for t in local_teams
    ]
    
    # Search in ChromaDB for teams with player data (Premier League 2025-2026)
    major_teams = [
        "Manchester City", "Liverpool", "Arsenal", "Chelsea",
        "Tottenham Hotspur", "Manchester United", "Newcastle United",
        "Brighton & Hove Albion", "West Ham United", "Aston Villa",
        "Crystal Palace", "Wolverhampton Wanderers", "Fulham", "Brentford",
        "Nottingham Forest", "Everton", "AFC Bournemouth", "Leicester City",
        "Southampton", "Ipswich Town", "Leeds United", "Sunderland"
    ]
    
    for team_name in major_teams:
        if q.lower() in team_name.lower():
            # Solo incluir equipos de las 5 ligas permitidas
            league = get_team_league(team_name)
            if league not in ALLOWED_LEAGUES:
                continue
                
            players = PlayerVectorStore.search_by_team(team_name, limit=1)
            if players:
                # Estimate player count to avoid slow full search
                player_count = 11  # Default estimate for major teams
                results["with_players"].append({
                    "id": f"chroma_{team_name.lower().replace(' ', '_')}",
                    "name": team_name,
                    "short_name": team_name[:3].upper(),
                    "logo_url": "",
                    "country": "",
                    "league": league,  # ✅ Incluir liga
                    "has_players": True,
                    "player_count": player_count
                })
    
    # Search in external APIs (Unified client with fallback) - with timeout
    if search_api:
        try:
            # Try unified client with 5 second timeout to avoid blocking
            api_team = await asyncio.wait_for(
                UnifiedAPIClient.get_team_by_name(q),
                timeout=5.0
            )
            if api_team:
                print(f"🔍 API returned team: {api_team.name} (ID: {api_team.id}) for search '{q}'")
                # Verificar que el nombre del equipo coincida con la búsqueda
                if q.lower() not in api_team.name.lower() and api_team.name.lower() not in q.lower():
                    print(f"⚠️ API returned wrong team '{api_team.name}' for search '{q}' - skipping")
                else:
                    # ✅ Si la liga está vacía, intentar obtenerla del mapeo
                    league = api_team.league or get_team_league(api_team.name)
                    # Solo incluir equipos de las 5 ligas permitidas
                    if league in ALLOWED_LEAGUES or is_team_in_allowed_league(api_team.name, league):
                        results["api"].append({
                            "id": api_team.id,
                            "name": api_team.name,
                            "short_name": api_team.short_name,
                            "logo_url": api_team.logo_url,
                            "country": api_team.country or "",
                            "league": league,  # ✅ Usar liga extraída o mapeada
                            "has_players": False,
                            "player_count": 0,
                            "source": "external_api"
                        })
        except (asyncio.TimeoutError, Exception) as e:
            # Silently fail - we already have local results
            print(f"⚠️ External API search timeout/error for '{q}': {e}")
    
    # Merge and deduplicate results (solo equipos de las 5 ligas)
    all_teams = []
    seen_names = set()
    
    # Función para verificar si un equipo está en las ligas permitidas
    def is_allowed_team(team_dict: dict) -> bool:
        team_league = team_dict.get("league", "")
        team_name = team_dict.get("name", "")
        # Verificar por liga directa
        if team_league and team_league in ALLOWED_LEAGUES:
            return True
        # Verificar por mapeo de nombre (incluyendo variantes con "FC", "AFC")
        mapped_league = get_team_league(team_name)
        if mapped_league in ALLOWED_LEAGUES:
            return True
        # Verificar sin sufijo FC/AFC
        clean_name = team_name.replace(" FC", "").replace(" AFC", "").strip()
        mapped_league = get_team_league(clean_name)
        return mapped_league in ALLOWED_LEAGUES
    
    # Prioritize teams with players (solo de las 5 ligas para equipos sin jugadores locales)
    for team in results["with_players"]:
        if team["name"].lower() not in seen_names and is_allowed_team(team):
            seen_names.add(team["name"].lower())
            all_teams.append(team)
    
    # Then local teams - SIEMPRE incluir equipos locales con jugadores (cualquier liga)
    for team in results["local"]:
        if team["name"].lower() not in seen_names:
            # Equipos locales con jugadores siempre se muestran
            # Equipos locales sin jugadores solo si están en ligas permitidas
            if team.get("has_players", False) or is_allowed_team(team):
                seen_names.add(team["name"].lower())
                all_teams.append(team)
    
    # Finally API teams (solo de las 5 ligas)
    for team in results["api"]:
        if team["name"].lower() not in seen_names and is_allowed_team(team):
            seen_names.add(team["name"].lower())
            all_teams.append(team)
    
    return {
        "success": True,
        "data": {
            "teams": all_teams[:limit],
            "total": len(all_teams)
        }
    }


@router.get("/with-players")
async def get_teams_with_players(
    include_all: bool = Query(default=False, description="Include teams from all leagues, not just Premier League")
):
    """
    🏆 Get all teams that have player data in the system
    Optimized with caching to avoid slow ChromaDB queries
    
    - By default: only Premier League teams
    - With include_all=true: all teams with players (for clustering)
    """
    cache_key = f"teams_with_players_list_{'all' if include_all else 'premier'}"
    
    # Check cache first (5 minute cache)
    cached_teams = await api_cache.get(cache_key)
    if cached_teams is not None:
        return {
            "success": True,
            "data": {
                "teams": cached_teams,
                "total": len(cached_teams)
            }
        }
    
    teams = []
    seen_names = set()
    
    try:
        # 1. Get teams from MongoDB that have players (fast)
        mongo_teams = await TeamRepository.get_teams_with_players()
        for team in mongo_teams:
            if team.name.lower() not in seen_names:
                seen_names.add(team.name.lower())
                # Use stored player_count if available, otherwise estimate
                # Avoid slow ChromaDB query here
                player_count = getattr(team, 'player_count', 11) or 11
                # Obtener liga del equipo (de la DB o del mapeo)
                league = team.league or get_team_league(team.name)
                
                # Filtrar por liga solo si no se pide todos
                if not include_all and league not in ALLOWED_LEAGUES:
                    continue
                    
                teams.append({
                    "id": team.id,
                    "name": team.name,
                    "short_name": team.short_name,
                    "logo_url": team.logo_url or "",
                    "country": team.country or "",
                    "league": league,  # Usar liga mapeada
                    "has_players": True,
                    "player_count": player_count,
                    "source": "mongodb"
                })
        
        # 2. Also check major European teams in ChromaDB (seed data)
        # Only check if we have few teams to avoid slow queries
        if len(teams) < 10:
            major_teams = [
                "Manchester City", "Liverpool", "Arsenal", "Chelsea",
                "Tottenham Hotspur", "Manchester United", "Newcastle United",
                "Brighton & Hove Albion", "West Ham United", "Aston Villa"
            ]
            
            for team_name in major_teams:
                if team_name.lower() not in seen_names:
                    # Solo incluir equipos de las 5 ligas permitidas
                    league = get_team_league(team_name)
                    if not include_all and league not in ALLOWED_LEAGUES:
                        continue
                        
                    # Quick check - only search for 1 player to see if team exists
                    players = PlayerVectorStore.search_by_team(team_name, limit=1)
                    if players:
                        # Estimate player count (avoid full search)
                        player_count = 11  # Default estimate
                        seen_names.add(team_name.lower())
                        teams.append({
                            "id": f"chroma_{team_name.lower().replace(' ', '_')}",
                            "name": team_name,
                            "short_name": team_name[:3].upper(),
                            "logo_url": "",
                            "country": "",
                            "league": league,  # ✅ Incluir liga
                            "has_players": True,
                            "player_count": player_count,
                            "source": "chromadb"
                        })
        
        # Sort by name
        teams.sort(key=lambda t: t["name"])
        
        # Cache for 5 minutes
        await api_cache.set(cache_key, teams, ttl=300)
        
    except Exception as e:
        print(f"⚠️ Error loading teams with players: {e}")
        # Return empty list on error instead of failing
        teams = []
    
    return {
        "success": True,
        "data": {
            "teams": teams,
            "total": len(teams)
        }
    }


@router.get("/all")
async def get_all_teams():
    """
    📋 Get ALL teams stored in MongoDB (solo de las 5 ligas permitidas)
    """
    all_teams = await TeamRepository.get_all(limit=500)
    
    teams_list = []
    for team in all_teams:
        # Solo incluir equipos de las 5 ligas permitidas
        if team.league and team.league not in ALLOWED_LEAGUES:
            # Verificar también por nombre si la liga no está definida
            if not is_team_in_allowed_league(team.name, team.league):
                continue
                
        # Get player count from ChromaDB
        player_count = len(PlayerVectorStore.search_by_team(team.name, limit=30))
        teams_list.append({
            "id": team.id,
            "name": team.name,
            "short_name": team.short_name,
            "logo_url": team.logo_url,
            "country": team.country,
            "league": team.league,
            "has_players": player_count > 0,
            "player_count": player_count
        })
    
    return {
        "success": True,
        "data": {
            "teams": teams_list,
            "total": len(teams_list)
        }
    }


@router.post("/add")
async def add_team(
    team_data: TeamCreate,
    current_user = Depends(get_optional_user)
):
    """
    ➕ Add a new team to the system with optional players
    
    Players can be added with estimated attributes based on:
    - Real player data if available
    - Generic attributes if not
    """
    # Create team
    team = Team(
        id=f"user_{team_data.name.lower().replace(' ', '_')}",
        name=team_data.name,
        short_name=team_data.short_name or team_data.name[:3].upper(),
        logo_url=team_data.logo_url,
        country=team_data.country,
        league=team_data.league,
    )
    
    user_id = current_user.id if current_user else "system"
    saved_team = await TeamRepository.create(team, added_by=user_id)
    
    # Add players if provided
    players_added = 0
    if team_data.players:
        players = []
        for i, player_data in enumerate(team_data.players):
            player = PlayerAttributes(
                player_id=f"{saved_team.id}_player_{i+1}",
                name=player_data.name,
                team=team_data.name,
                position=player_data.position,
                overall_rating=player_data.overall_rating,
                pace=player_data.pace,
                shooting=player_data.shooting,
                passing=player_data.passing,
                dribbling=player_data.dribbling,
                defending=player_data.defending,
                physical=player_data.physical,
            )
            players.append(player)
        
        if players:
            PlayerVectorStore.add_players_batch(players)
            players_added = len(players)
            await TeamRepository.update_player_status(team_data.name, players_added)
            # Invalidar ambas cachés de equipos con jugadores
            await api_cache.delete("teams_with_players_list_premier")
            await api_cache.delete("teams_with_players_list_all")

    return {
        "success": True,
        "data": {
            "team": {
                "id": saved_team.id,
                "name": saved_team.name,
                "short_name": saved_team.short_name,
                "logo_url": saved_team.logo_url,
                "league": saved_team.league or team_data.league or "",
                "has_players": players_added > 0,
                "player_count": players_added
            },
            "players_added": players_added
        },
        "message": f"Equipo '{team_data.name}' agregado exitosamente"
    }


@router.post("/add-players/{team_name}")
async def add_players_to_team(
    team_name: str,
    players: List[PlayerCreate],
    current_user = Depends(get_current_user)
):
    """
    👥 Add players to an existing team
    """
    if not players:
        raise HTTPException(status_code=400, detail="No players provided")
    
    player_objects = []
    for i, player_data in enumerate(players):
        player = PlayerAttributes(
            player_id=f"{team_name.lower().replace(' ', '_')}_player_{i+1}_{player_data.name.lower().replace(' ', '_')}",
            name=player_data.name,
            team=team_name,
            position=player_data.position,
            overall_rating=player_data.overall_rating,
            pace=player_data.pace,
            shooting=player_data.shooting,
            passing=player_data.passing,
            dribbling=player_data.dribbling,
            defending=player_data.defending,
            physical=player_data.physical,
        )
        player_objects.append(player)
    
    PlayerVectorStore.add_players_batch(player_objects)
    
    # Update team status
    total_players = len(PlayerVectorStore.search_by_team(team_name, limit=50))
    await TeamRepository.update_player_status(team_name, total_players)
    
    return {
        "success": True,
        "data": {
            "team": team_name,
            "players_added": len(player_objects),
            "total_players": total_players
        },
        "message": f"Se agregaron {len(player_objects)} jugadores a '{team_name}'"
    }


@router.post("/bulk-add")
async def bulk_add_teams(
    data: BulkTeamsCreate,
    current_user = Depends(get_current_user)
):
    """
    📦 Add multiple teams at once (bulk import)
    
    Useful for adding entire leagues or tournaments
    """
    teams_created = 0
    players_added = 0
    
    for team_data in data.teams:
        # Create team
        team = Team(
            id=f"bulk_{team_data.name.lower().replace(' ', '_')}",
            name=team_data.name,
            short_name=team_data.short_name or team_data.name[:3].upper(),
            logo_url=team_data.logo_url,
            country=team_data.country,
            league=team_data.league,
        )
        
        saved_team = await TeamRepository.create(team, added_by=current_user.id)
        teams_created += 1
        
        # Add players if provided
        if team_data.players:
            players = []
            for i, player_data in enumerate(team_data.players):
                player = PlayerAttributes(
                    player_id=f"{saved_team.id}_player_{i+1}",
                    name=player_data.name,
                    team=team_data.name,
                    position=player_data.position,
                    overall_rating=player_data.overall_rating,
                    pace=player_data.pace,
                    shooting=player_data.shooting,
                    passing=player_data.passing,
                    dribbling=player_data.dribbling,
                    defending=player_data.defending,
                    physical=player_data.physical,
                )
                players.append(player)
            
            if players:
                PlayerVectorStore.add_players_batch(players)
                players_added += len(players)
                await TeamRepository.update_player_status(team_data.name, len(players))
    
    return {
        "success": True,
        "data": {
            "teams_created": teams_created,
            "players_added": players_added
        },
        "message": f"Se agregaron {teams_created} equipos y {players_added} jugadores"
    }


@router.get("/{team_name}/players")
async def get_team_players(
    team_name: str,
    force_update: bool = Query(False, description="Force update players from API")
):
    """
    👥 Get all players for a team - generates with AI if not found and SAVES to DB
    
    Flow:
    1. If force_update=True, fetch fresh players from API first
    2. Check ChromaDB (fast, local)
    3. If not found, generate with AI (DeepSeek)
    4. SAVE generated players to ChromaDB for future queries
    5. SAVE team to MongoDB for persistence
    
    ✅ NEW: Also returns last 5 matches for the team
    ✅ NEW: Option to force update players from external APIs
    """
    # If force_update, try to get fresh players from API first
    if force_update:
        try:
            from src.infrastructure.external_api.api_selector import UnifiedAPIClient
            team_with_squad = await UnifiedAPIClient.get_team_with_squad(team_name)
            
            if team_with_squad and team_with_squad.get("players"):
                # Convert API players to our format
                api_players = team_with_squad.get("players", [])
                if api_players:
                    from src.domain.entities import PlayerAttributes
                    players = []
                    for i, p_data in enumerate(api_players):
                        player = PlayerAttributes(
                            player_id=f"api_{team_name.lower().replace(' ', '_')}_{i}_{p_data.get('name', 'unknown').lower().replace(' ', '_')}",
                            name=p_data.get("name", "Unknown"),
                            team=team_name,
                            position=p_data.get("position", "CM"),
                            overall_rating=p_data.get("overall_rating", p_data.get("overall", 75)),
                            pace=p_data.get("pace", 70),
                            shooting=p_data.get("shooting", 65),
                            passing=p_data.get("passing", 70),
                            dribbling=p_data.get("dribbling", 68),
                            defending=p_data.get("defending", 50),
                            physical=p_data.get("physical", 70),
                        )
                        players.append(player)
                    
                    # Update ChromaDB with fresh players
                    if players:
                        PlayerVectorStore.add_players_batch(players)
                        print(f"✅ Updated {len(players)} players for '{team_name}' from API")
        except Exception as e:
            print(f"⚠️ Error updating players from API for {team_name}: {e}")
            # Continue with ChromaDB lookup
    
    # First check ChromaDB
    players = PlayerVectorStore.search_by_team(team_name, limit=30)
    
    # If no players found, generate with AI and SAVE
    if not players:
        from src.infrastructure.llm.dixie import DixieAI
        from src.domain.entities import Team
        
        print(f"🔄 No players in ChromaDB for '{team_name}', generating with AI...")
        real_players = await DixieAI.generate_team_players(team_name, count=11)
        
        if real_players and len(real_players) > 0:
            from src.domain.entities import PlayerAttributes
            players = []
            for i, p_data in enumerate(real_players):
                if isinstance(p_data, dict):
                    player = PlayerAttributes(
                        player_id=f"ai_{team_name.lower().replace(' ', '_')}_{i}",
                        name=p_data.get("name", "Unknown"),
                        team=team_name,
                        position=p_data.get("position", "CM"),
                        overall_rating=p_data.get("overall_rating", p_data.get("overall", 75)),
                        pace=p_data.get("pace", 70),
                        shooting=p_data.get("shooting", 65),
                        passing=p_data.get("passing", 70),
                        dribbling=p_data.get("dribbling", 68),
                        defending=p_data.get("defending", 50),
                        physical=p_data.get("physical", 70),
                    )
                    players.append(player)
            
            # 🔥 SAVE to ChromaDB for future queries (no more AI calls needed)
            if players:
                PlayerVectorStore.add_players_batch(players)
                print(f"✅ Saved {len(players)} players for '{team_name}' to ChromaDB")
                
                # 🔥 SAVE team to MongoDB for persistence
                team = Team(
                    id=f"ai_{team_name.lower().replace(' ', '_')}",
                    name=team_name,
                    short_name=team_name[:3].upper(),
                    logo_url="",
                    country="",
                    league="",
                )
                await TeamRepository.create(team, added_by="ai_generated")
                await TeamRepository.update_player_status(team_name, len(players))
                print(f"✅ Saved team '{team_name}' to MongoDB")
    
    # Calculate team stats
    if players:
        avg_overall = sum(p.overall_rating for p in players) / len(players)
        avg_pace = sum(p.pace for p in players) / len(players)
        avg_shooting = sum(p.shooting for p in players) / len(players)
        avg_passing = sum(p.passing for p in players) / len(players)
        avg_defending = sum(p.defending for p in players) / len(players)
        avg_physical = sum(p.physical for p in players) / len(players)
        
        team_stats = {
            "overall": round(avg_overall, 1),
            "pace": round(avg_pace, 1),
            "shooting": round(avg_shooting, 1),
            "passing": round(avg_passing, 1),
            "defending": round(avg_defending, 1),
            "physical": round(avg_physical, 1),
        }
    else:
        team_stats = None
    
    # ✅ NEW: Get last 5 matches for the team
    last_matches = []
    try:
        # Try to get team ID from MongoDB or API
        team = await TeamRepository.find_by_name(team_name)
        team_id = None
        
        if team and team.id.startswith("tsdb_"):
            team_id = team.id.replace("tsdb_", "")
        else:
            # Try to get from TheSportsDB
            from src.infrastructure.external_api.thesportsdb import TheSportsDBClient
            team_data = await TheSportsDBClient.search_team(team_name)
            if team_data:
                team_id = team_data.get("idTeam")
        
        if team_id:
            from src.infrastructure.external_api.thesportsdb import TheSportsDBClient
            matches_raw = await TheSportsDBClient.get_last_matches(team_id, limit=5)
            
            # Format matches
            for match in matches_raw:
                last_matches.append({
                    "id": match.get("idEvent", ""),
                    "date": match.get("dateEvent", ""),
                    "home_team": match.get("strHomeTeam", ""),
                    "away_team": match.get("strAwayTeam", ""),
                    "home_score": match.get("intHomeScore"),
                    "away_score": match.get("intAwayScore"),
                    "result": match.get("strResult", ""),
                    "league": match.get("strLeague", ""),
                    "venue": match.get("strVenue", ""),
                })
    except Exception as e:
        print(f"⚠️ Error getting last matches for {team_name}: {e}")
        # Continue without matches if API fails
    
    return {
        "success": True,
        "data": {
            "team": team_name,
            "players": [p.to_dict() for p in players],
            "count": len(players),
            "stats": team_stats,
            "last_matches": last_matches,  # ✅ Últimos 5 partidos
        }
    }


@router.post("/generate-players/{team_name}")
async def generate_players_for_team(
    team_name: str,
    count: int = Query(11, ge=1, le=25, description="Number of players to generate"),
    avg_rating: int = Query(75, ge=50, le=90, description="Average team rating"),
    current_user = Depends(get_optional_user)
):
    """
    🤖 Auto-generate players for a team with AI-estimated attributes
    
    Uses Dixie AI to find REAL player names and positions if possible.
    """
    from src.infrastructure.llm.dixie import DixieAI
    import random
    
    # Try to get REAL players from AI first
    real_players = await DixieAI.generate_team_players(team_name, count=count)
    
    players = []
    
    if real_players and len(real_players) > 0:
        # Use real players found by AI
        for i, p_data in enumerate(real_players):
            player = PlayerAttributes(
                player_id=f"ai_{team_name.lower().replace(' ', '_')}_{i}_{p_data['name'].lower().replace(' ', '_')}",
                name=p_data["name"],
                team=team_name,
                position=p_data.get("position", "CM"),
                overall_rating=p_data.get("overall_rating", avg_rating),
                pace=p_data.get("pace", 70),
                shooting=p_data.get("shooting", 60),
                passing=p_data.get("passing", 70),
                dribbling=p_data.get("dribbling", 70),
                defending=p_data.get("defending", 60),
                physical=p_data.get("physical", 70),
            )
            players.append(player)
    else:
        # Fallback to generic generation if AI fails
        positions = {
            "GK": 1, "CB": 2, "LB": 1, "RB": 1, "CDM": 1, "CM": 2, "CAM": 1, "ST": 1, "RW": 1,
        }
        
        if count != 11:
            positions = {}
            pos_list = ["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"]
            for i in range(count):
                pos = pos_list[i % len(pos_list)]
                positions[pos] = positions.get(pos, 0) + 1
        
        player_names = ["García", "Martínez", "López", "González", "Rodríguez", "Hernández", "Pérez", "Sánchez", "Ramírez", "Torres"]
        
        player_idx = 0
        for position, num in positions.items():
            for _ in range(num):
                rating_variance = random.randint(-5, 10)
                base_rating = max(50, min(95, avg_rating + rating_variance))
                
                player = PlayerAttributes(
                    player_id=f"gen_{team_name.lower().replace(' ', '_')}_{player_idx}",
                    name=f"J. {player_names[player_idx % len(player_names)]}",
                    team=team_name,
                    position=position,
                    overall_rating=base_rating,
                    pace=70, shooting=60, passing=70, dribbling=70, defending=60, physical=70
                )
                players.append(player)
                player_idx += 1
    
    # Save to ChromaDB
    PlayerVectorStore.add_players_batch(players)
    await TeamRepository.update_player_status(team_name, len(players))
    
    # Invalidar ambas cachés de equipos con jugadores para que la UI se actualice
    await api_cache.delete("teams_with_players_list_premier")
    await api_cache.delete("teams_with_players_list_all")
    print(f"✅ Cache invalidado para teams_with_players_list_premier y _all")

    return {
        "success": True,
        "data": {
            "team": team_name,
            "players_generated": len(players),
            "avg_rating": sum(p.overall_rating for p in players) // len(players),
            "players": [p.to_dict() for p in players],
            "has_players": True,
            "player_count": len(players)
        },
        "message": f"Se generaron {len(players)} jugadores reales para '{team_name}'"
    }


@router.get("/custom-teams-for-clustering")
async def get_custom_teams_for_clustering():
    """
    🔬 Obtener equipos custom con estadísticas para clustering
    
    Retorna equipos agregados por usuarios con estadísticas derivadas
    de los atributos promedio de sus jugadores.
    """
    try:
        # Obtener equipos de MongoDB que tienen jugadores
        mongo_teams = await TeamRepository.get_teams_with_players()
        
        custom_teams = []
        for team in mongo_teams:
            # Obtener jugadores del equipo
            players = PlayerVectorStore.search_by_team(team.name, limit=30)
            
            if not players or len(players) < 5:
                continue
            
            # Calcular estadísticas promedio del equipo
            avg_overall = sum(p.get("overall_rating", 70) for p in players) / len(players)
            avg_pace = sum(p.get("pace", 70) for p in players) / len(players)
            avg_shooting = sum(p.get("shooting", 60) for p in players) / len(players)
            avg_passing = sum(p.get("passing", 70) for p in players) / len(players)
            avg_defending = sum(p.get("defending", 60) for p in players) / len(players)
            avg_physical = sum(p.get("physical", 70) for p in players) / len(players)
            
            # Crear estadísticas simuladas basadas en atributos
            # Esto permite comparar con equipos de la liga
            team_stats = {
                "name": team.name,
                "short_name": team.short_name or team.name[:3].upper(),
                "league": team.league or "Custom",
                "player_count": len(players),
                "avg_overall": round(avg_overall, 1),
                "stats": {
                    # Estadísticas derivadas de atributos de jugadores
                    "attack_rating": round((avg_shooting + avg_pace + avg_passing) / 3, 1),
                    "defense_rating": round((avg_defending + avg_physical) / 2, 1),
                    "overall_team_rating": round(avg_overall, 1),
                    # Para clustering comparativo con equipos de liga
                    "estimated_ppg": round(1.0 + (avg_overall - 65) / 20, 2),  # 1.0 a 2.5
                    "estimated_gf_pg": round(1.0 + (avg_shooting - 60) / 25, 2),  # Goles por partido
                    "estimated_ga_pg": round(1.8 - (avg_defending - 60) / 30, 2),  # Goles en contra
                }
            }
            custom_teams.append(team_stats)
        
        return {
            "success": True,
            "data": {
                "teams": custom_teams,
                "total": len(custom_teams)
            }
        }
    except Exception as e:
        print(f"⚠️ Error obteniendo equipos custom: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {"teams": [], "total": 0}
        }


@router.post("/refresh-cache")
async def refresh_teams_cache():
    """
    🔄 Forzar actualización del caché de equipos
    
    Útil después de agregar nuevos equipos o jugadores.
    """
    await api_cache.delete("teams_with_players_list_premier")
    await api_cache.delete("teams_with_players_list_all")
    print("✅ Caché de equipos invalidado manualmente (premier y all)")
    return {
        "success": True,
        "message": "Caché de equipos actualizado correctamente"
    }


def _team_to_response(team: Team, has_players: bool = False, player_count: int = 0) -> dict:
    """Convert Team entity to response dict"""
    # Obtener liga del equipo (de la entidad o del mapeo)
    league = team.league or get_team_league(team.name)
    return {
        "id": team.id,
        "name": team.name,
        "short_name": team.short_name,
        "logo_url": team.logo_url,
        "country": team.country or "",
        "league": league,
        "has_players": has_players,
        "player_count": player_count
    }
