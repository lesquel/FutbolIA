"""
Prediction API Routes
Handles match predictions and history
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from src.core.logger import log_info, log_warning, log_error, log_prediction
from src.use_cases.prediction import PredictionUseCase
from src.presentation.auth_routes import get_current_user
from src.infrastructure.db.dixie_stats import DixieStats


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
    log_info("Prediction request received",
             home_team=request.home_team,
             away_team=request.away_team,
             user_id=current_user.id)
    
    result = await PredictionUseCase.predict_match(
        home_team_name=request.home_team,
        away_team_name=request.away_team,
        user_id=current_user.id,
        language=request.language,
    )
    
    if not result["success"]:
        log_warning("Prediction failed",
                    home_team=request.home_team,
                    away_team=request.away_team,
                    error=result.get("error", "Unknown error"))
        raise HTTPException(status_code=400, detail=result.get("error", "Error generating prediction"))
    
    # Record prediction stats for Dixie
    try:
        predicted_winner = result.get("data", {}).get("prediction", {}).get("winner", "")
        confidence = result.get("data", {}).get("prediction", {}).get("confidence", 0)
        
        await DixieStats.record_prediction(
            home_team=request.home_team,
            away_team=request.away_team,
            predicted_winner=predicted_winner,
            confidence=confidence,
            user_id=current_user.id
        )
        
        log_prediction(
            home_team=request.home_team,
            away_team=request.away_team,
            winner=predicted_winner,
            confidence=confidence,
            user_id=current_user.id
        )
    except Exception as e:
        log_warning("Failed to record prediction stats", error=str(e))
    
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


@router.get("/{prediction_id}")
async def get_prediction_detail(
    prediction_id: str,
    current_user = Depends(get_current_user)
):
    """🔍 Get detailed information for a specific prediction"""
    result = await PredictionUseCase.get_prediction_by_id(
        prediction_id=prediction_id,
        user_id=current_user.id
    )
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
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
