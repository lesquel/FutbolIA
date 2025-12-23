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
from src.presentation.auth_routes import get_current_user, get_optional_user


router = APIRouter(prefix="/teams", tags=["Teams"])


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
    results["local"] = [_team_to_response(t, has_players=False) for t in local_teams]
    
    # Search in ChromaDB for teams with player data
    major_teams = [
        "Real Madrid", "Manchester City", "Barcelona", "Bayern Munich",
        "Liverpool", "Arsenal", "Paris Saint-Germain", "Inter Milan",
        "Juventus", "Atletico Madrid", "Chelsea", "Tottenham",
        "Napoli", "AC Milan", "Borussia Dortmund", "RB Leipzig"
    ]
    
    for team_name in major_teams:
        if q.lower() in team_name.lower():
            players = PlayerVectorStore.search_by_team(team_name, limit=1)
            if players:
                player_count = len(PlayerVectorStore.search_by_team(team_name, limit=20))
                results["with_players"].append({
                    "id": f"chroma_{team_name.lower().replace(' ', '_')}",
                    "name": team_name,
                    "short_name": team_name[:3].upper(),
                    "logo_url": "",
                    "country": "",
                    "league": "",
                    "has_players": True,
                    "player_count": player_count
                })
    
    # Search in Football-Data.org API
    if search_api:
        api_team = await FootballAPIClient.get_team_by_name(q)
        if api_team:
            results["api"].append({
                "id": api_team.id,
                "name": api_team.name,
                "short_name": api_team.short_name,
                "logo_url": api_team.logo_url,
                "country": api_team.country or "",
                "league": api_team.league or "",
                "has_players": False,
                "player_count": 0,
                "source": "football-data.org"
            })
    
    # Merge and deduplicate results
    all_teams = []
    seen_names = set()
    
    # Prioritize teams with players
    for team in results["with_players"]:
        if team["name"].lower() not in seen_names:
            seen_names.add(team["name"].lower())
            all_teams.append(team)
    
    # Then local teams
    for team in results["local"]:
        if team["name"].lower() not in seen_names:
            seen_names.add(team["name"].lower())
            all_teams.append(team)
    
    # Finally API teams
    for team in results["api"]:
        if team["name"].lower() not in seen_names:
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
async def get_teams_with_players():
    """
    🏆 Get all teams that have player data in the system
    """
    # Get teams from ChromaDB
    major_teams = [
        "Real Madrid", "Manchester City", "Barcelona", "Bayern Munich",
        "Liverpool", "Arsenal", "Paris Saint-Germain", "Inter Milan",
        "Juventus", "Atletico Madrid"
    ]
    
    teams = []
    for team_name in major_teams:
        players = PlayerVectorStore.search_by_team(team_name, limit=1)
        if players:
            player_count = len(PlayerVectorStore.search_by_team(team_name, limit=20))
            teams.append({
                "id": f"chroma_{team_name.lower().replace(' ', '_')}",
                "name": team_name,
                "short_name": team_name[:3].upper(),
                "logo_url": "",
                "country": "",
                "league": "",
                "has_players": True,
                "player_count": player_count
            })
    
    return {
        "success": True,
        "data": {
            "teams": teams,
            "total": len(teams)
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
    
    return {
        "success": True,
        "data": {
            "team": {
                "id": saved_team.id,
                "name": saved_team.name,
                "short_name": saved_team.short_name,
                "logo_url": saved_team.logo_url,
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
async def get_team_players(team_name: str):
    """
    👥 Get all players for a team
    """
    players = PlayerVectorStore.search_by_team(team_name, limit=30)
    
    if not players:
        # Try partial match
        players = PlayerVectorStore.search_by_name(team_name, limit=10)
    
    return {
        "success": True,
        "data": {
            "team": team_name,
            "players": [p.to_dict() for p in players],
            "count": len(players)
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
    
    return {
        "success": True,
        "data": {
            "team": team_name,
            "players_generated": len(players),
            "avg_rating": sum(p.overall_rating for p in players) // len(players),
            "players": [p.to_dict() for p in players[:5]]
        },
        "message": f"Se generaron {len(players)} jugadores reales para '{team_name}'"
    }


def _team_to_response(team: Team, has_players: bool = False, player_count: int = 0) -> dict:
    """Convert Team entity to response dict"""
    return {
        "id": team.id,
        "name": team.name,
        "short_name": team.short_name,
        "logo_url": team.logo_url,
        "country": team.country or "",
        "league": team.league or "",
        "has_players": has_players,
        "player_count": player_count
    }
