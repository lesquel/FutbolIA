"""
Stats API Routes
Dixie statistics and analytics endpoints
"""
from fastapi import APIRouter, Query
from typing import Optional

from src.infrastructure.db.dixie_stats import DixieStats
from src.core.fuzzy_search import suggest_corrections, auto_complete, get_team_info
from src.infrastructure.chromadb.player_store import PlayerVectorStore
from src.infrastructure.db.team_repository import TeamRepository


router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/dixie")
async def get_dixie_stats():
    """
    📊 Get Dixie's overall prediction statistics
    
    Returns accuracy percentage, total predictions, and confidence breakdown
    """
    stats = await DixieStats.get_overall_stats()
    
    return {
        "success": True,
        "data": {
            "dixie": {
                "name": "Dixie",
                "role": "AI Football Oracle",
                "personality": "Sarcastic but accurate",
                **stats
            }
        }
    }


@router.get("/dixie/team/{team_name}")
async def get_team_prediction_stats(team_name: str):
    """
    📊 Get Dixie's prediction stats for a specific team
    """
    stats = await DixieStats.get_team_stats(team_name)
    
    return {
        "success": True,
        "data": stats
    }


@router.get("/dixie/recent")
async def get_recent_predictions(
    limit: int = Query(10, le=50),
    user_id: Optional[str] = None
):
    """
    📜 Get recent predictions
    """
    predictions = await DixieStats.get_recent_predictions(limit=limit, user_id=user_id)
    
    return {
        "success": True,
        "data": {
            "predictions": predictions,
            "count": len(predictions)
        }
    }


@router.get("/dixie/leaderboard")
async def get_leaderboard(limit: int = Query(10, le=100)):
    """
    🏆 Get user prediction accuracy leaderboard
    """
    leaderboard = await DixieStats.get_leaderboard(limit=limit)
    
    return {
        "success": True,
        "data": {
            "leaderboard": leaderboard
        }
    }


@router.get("/dixie/daily")
async def get_daily_stats(days: int = Query(7, le=30)):
    """
    📈 Get daily prediction statistics
    """
    daily = await DixieStats.get_daily_stats(days=days)
    
    return {
        "success": True,
        "data": {
            "daily_stats": daily,
            "days": days
        }
    }


# ==================== Fuzzy Search Endpoints ====================

@router.get("/teams/suggest")
async def suggest_team_names(q: str = Query(..., min_length=2)):
    """
    🔍 Suggest team names based on fuzzy matching
    
    Use this when user types something that doesn't match exactly.
    Example: "brcelona" -> suggests "Barcelona", "Barcelona SC"
    """
    # Get known teams from database
    db_teams = await TeamRepository.get_all(limit=500)
    known_teams = [t.name for t in db_teams]
    
    # Also add teams from ChromaDB
    major_teams = [
        "Real Madrid", "Manchester City", "Barcelona", "Bayern Munich",
        "Liverpool", "Arsenal", "Paris Saint-Germain", "Inter Milan",
        "Juventus", "Atletico Madrid", "Chelsea", "Tottenham",
        "Napoli", "AC Milan", "Borussia Dortmund"
    ]
    known_teams.extend(major_teams)
    
    suggestions = suggest_corrections(q, list(set(known_teams)))
    
    return {
        "success": True,
        "data": suggestions
    }


@router.get("/teams/autocomplete")
async def autocomplete_team_names(
    prefix: str = Query(..., min_length=1),
    limit: int = Query(10, le=20)
):
    """
    ⌨️ Autocomplete team names as user types
    
    Returns team names that start with the given prefix
    """
    # Get known teams
    db_teams = await TeamRepository.get_all(limit=500)
    known_teams = [t.name for t in db_teams]
    
    results = auto_complete(prefix, known_teams, limit=limit)
    
    return {
        "success": True,
        "data": {
            "prefix": prefix,
            "suggestions": results
        }
    }


@router.get("/teams/info/{team_name}")
async def get_team_metadata(team_name: str):
    """
    ℹ️ Get metadata about a team (country, league, aliases)
    """
    info = get_team_info(team_name)
    
    # Also get player count from ChromaDB
    players = PlayerVectorStore.search_by_team(team_name, limit=30)
    info["player_count"] = len(players)
    info["has_data"] = len(players) > 0
    
    return {
        "success": True,
        "data": info
    }
