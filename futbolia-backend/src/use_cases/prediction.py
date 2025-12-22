"""
Prediction Use Cases
Core business logic for match predictions using RAG + DeepSeek
"""
from typing import Optional

from src.domain.entities import Team, Match, Prediction, PredictionResult
from src.infrastructure.chromadb.player_store import PlayerVectorStore
from src.infrastructure.llm.dixie import DixieAI
from src.infrastructure.external_api.football_api import FootballAPIClient
from src.infrastructure.db.prediction_repository import PredictionRepository


class PredictionUseCase:
    """Use case for generating match predictions"""
    
    @classmethod
    async def predict_match(
        cls,
        home_team_name: str,
        away_team_name: str,
        user_id: str,
        language: str = "es"
    ) -> dict:
        """
        Generate a prediction for a match using the hybrid RAG approach:
        1. Fetch team data from API-Football (or mock)
        2. Get player attributes from ChromaDB
        3. Send context to Dixie (DeepSeek) for analysis
        4. Save prediction to MongoDB
        """
        
        # Step 1: Get team information
        home_team = await FootballAPIClient.get_team_by_name(home_team_name)
        away_team = await FootballAPIClient.get_team_by_name(away_team_name)
        
        if not home_team or not away_team:
            return {
                "success": False,
                "error": "No se encontraron los equipos" if language == "es" else "Teams not found",
            }
        
        # Get team form
        home_team.form = await FootballAPIClient.get_team_form(home_team.id)
        away_team.form = await FootballAPIClient.get_team_form(away_team.id)
        
        # Step 2: Get player attributes from ChromaDB (RAG context)
        home_players = PlayerVectorStore.get_star_players(home_team.name, top_n=5)
        away_players = PlayerVectorStore.get_star_players(away_team.name, top_n=5)
        
        # If no players found, try with partial name match
        if not home_players:
            home_players = PlayerVectorStore.search_by_name(home_team.name.split()[0], limit=5)
        if not away_players:
            away_players = PlayerVectorStore.search_by_name(away_team.name.split()[0], limit=5)
        
        # Step 3: Generate prediction with Dixie AI
        prediction_result = await DixieAI.predict_match(
            team_a=home_team,
            team_b=away_team,
            players_a=home_players,
            players_b=away_players,
            language=language,
        )
        
        # Step 4: Create match and prediction objects
        match = Match(
            id=f"{home_team.id}_vs_{away_team.id}",
            home_team=home_team,
            away_team=away_team,
            league=home_team.league or "International",
            venue=f"Estadio de {home_team.name}",
        )
        
        prediction = Prediction(
            user_id=user_id,
            match=match,
            result=prediction_result,
            language=language,
        )
        
        # Step 5: Save to database
        saved_prediction = await PredictionRepository.save(prediction)
        
        return {
            "success": True,
            "data": {
                "prediction": saved_prediction.to_dict(),
                "context": {
                    "home_players": [p.to_dict() for p in home_players],
                    "away_players": [p.to_dict() for p in away_players],
                }
            }
        }
    
    @classmethod
    async def get_user_history(cls, user_id: str, limit: int = 20) -> dict:
        """Get prediction history for a user"""
        predictions = await PredictionRepository.find_by_user(user_id, limit)
        stats = await PredictionRepository.get_stats(user_id)
        
        return {
            "success": True,
            "data": {
                "predictions": [p.to_dict() for p in predictions],
                "stats": stats,
            }
        }
    
    @classmethod
    async def get_available_matches(cls, league_id: int = 39) -> dict:
        """Get upcoming matches available for prediction"""
        matches = await FootballAPIClient.get_upcoming_fixtures(league_id, limit=10)
        
        return {
            "success": True,
            "data": {
                "matches": [m.to_dict() for m in matches],
            }
        }
    
    @classmethod
    async def get_player_comparison(cls, team_a: str, team_b: str) -> dict:
        """Get player comparison data for two teams"""
        comparison = PlayerVectorStore.get_player_comparison(team_a, team_b)
        
        return {
            "success": True,
            "data": comparison,
        }
