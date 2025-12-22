"""
Prediction API Routes
Handles match predictions and history
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from src.use_cases.prediction import PredictionUseCase
from src.presentation.auth_routes import get_current_user


router = APIRouter(prefix="/predictions", tags=["Predictions"])


# Request Models
class PredictMatchRequest(BaseModel):
    home_team: str
    away_team: str
    language: str = "es"


class CompareTeamsRequest(BaseModel):
    team_a: str
    team_b: str


# Routes
@router.post("/predict")
async def predict_match(
    request: PredictMatchRequest,
    current_user = Depends(get_current_user)
):
    """
    🔮 Generate a match prediction using Dixie AI
    
    This endpoint uses the hybrid RAG approach:
    - Fetches team data from API-Football
    - Gets player attributes from ChromaDB
    - Analyzes with DeepSeek (Dixie)
    """
    result = await PredictionUseCase.predict_match(
        home_team_name=request.home_team,
        away_team_name=request.away_team,
        user_id=current_user.id,
        language=request.language,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Error generating prediction"))
    
    return result


@router.get("/history")
async def get_history(
    limit: int = Query(default=20, le=100),
    current_user = Depends(get_current_user)
):
    """📊 Get user's prediction history and stats"""
    result = await PredictionUseCase.get_user_history(
        user_id=current_user.id,
        limit=limit,
    )
    return result


@router.get("/matches")
async def get_upcoming_matches(
    league_id: int = Query(default=39, description="League ID (39=Premier League, 140=La Liga)")
):
    """⚽ Get upcoming matches available for prediction"""
    result = await PredictionUseCase.get_available_matches(league_id)
    return result


@router.post("/compare")
async def compare_teams(request: CompareTeamsRequest):
    """📈 Get player comparison between two teams"""
    result = await PredictionUseCase.get_player_comparison(
        team_a=request.team_a,
        team_b=request.team_b,
    )
    return result


@router.get("/teams")
async def get_available_teams():
    """🏆 Get list of teams with player data in the system"""
    from src.infrastructure.chromadb.player_store import PlayerVectorStore
    
    # Get unique teams from our player database
    teams = set()
    
    # Search for players from major teams
    major_teams = [
        "Real Madrid", "Manchester City", "Barcelona", "Bayern Munich",
        "Liverpool", "Arsenal", "Paris Saint-Germain", "Inter Milan",
        "Juventus", "Atletico Madrid"
    ]
    
    available_teams = []
    for team_name in major_teams:
        players = PlayerVectorStore.search_by_team(team_name, limit=1)
        if players:
            available_teams.append({
                "name": team_name,
                "player_count": len(PlayerVectorStore.search_by_team(team_name, limit=20))
            })
    
    return {
        "success": True,
        "data": {
            "teams": available_teams
        }
    }
