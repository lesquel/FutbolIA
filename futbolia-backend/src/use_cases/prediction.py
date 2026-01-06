"""
Prediction Use Cases
Core business logic for match predictions using RAG + DeepSeek
"""
import asyncio
from typing import Optional

from src.domain.entities import Team, Match, Prediction, PredictionResult
from src.infrastructure.chromadb.player_store import PlayerVectorStore
from src.infrastructure.llm.dixie import DixieAI
from src.infrastructure.external_api.football_api import FootballAPIClient
from src.infrastructure.external_api.api_selector import UnifiedAPIClient
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
        # Try local DB first (for user-added teams like Emelec, Boca)
        from src.infrastructure.db.team_repository import TeamRepository
        
        # Parallelize local DB lookup
        home_team, away_team = await asyncio.gather(
            TeamRepository.find_by_name(home_team_name),
            TeamRepository.find_by_name(away_team_name)
        )
        
        # If not in local DB, try external API with fallback (Parallelized)
        async def get_team_or_fetch(team_name: str, existing_team: Optional[Team]) -> Optional[Team]:
            """Helper to return existing team or fetch from API"""
            if existing_team:
                return existing_team
            return await UnifiedAPIClient.get_team_by_name(team_name)
        
        home_team, away_team = await asyncio.gather(
            get_team_or_fetch(home_team_name, home_team),
            get_team_or_fetch(away_team_name, away_team)
        )
        
        if not home_team or not away_team:
            return {
                "success": False,
                "error": "No se encontraron los equipos" if language == "es" else "Teams not found",
            }
        
        # Get team form (Parallelized)
        home_form_task = FootballAPIClient.get_team_form(home_team.id)
        away_form_task = FootballAPIClient.get_team_form(away_team.id)
        
        home_team.form, away_team.form = await asyncio.gather(home_form_task, away_form_task)
        
        # Step 2: Get player attributes from ChromaDB (RAG context)
        # These are synchronous calls in the current implementation, but we can still call them sequentially
        # as they are usually fast (local vector DB)
        home_players = PlayerVectorStore.search_by_team(home_team.name, limit=15)
        away_players = PlayerVectorStore.search_by_team(away_team.name, limit=15)
        
        # If no players in ChromaDB, generate with AI (Parallelized)
        player_gen_tasks = []
        
        if not home_players:
            print(f"🔄 Generating players for {home_team.name} with AI...")
            player_gen_tasks.append(DixieAI.generate_team_players(home_team.name))
        else:
            player_gen_tasks.append(asyncio.sleep(0, result=None))
            
        if not away_players:
            print(f"🔄 Generating players for {away_team.name} with AI...")
            player_gen_tasks.append(DixieAI.generate_team_players(away_team.name))
        else:
            player_gen_tasks.append(asyncio.sleep(0, result=None))
            
        home_players_raw, away_players_raw = await asyncio.gather(*player_gen_tasks)
        
        # Process generated players if any
        from src.domain.entities import PlayerAttributes
        if home_players_raw:
            home_players = [
                PlayerAttributes(
                    name=p.get("name", "Unknown"),
                    position=p.get("position", "CM"),
                    overall_rating=p.get("overall_rating", p.get("overall", 75)),
                    pace=p.get("pace", 70),
                    shooting=p.get("shooting", 65),
                    passing=p.get("passing", 70),
                    dribbling=p.get("dribbling", 68),
                    defending=p.get("defending", 50),
                    physical=p.get("physical", 70),
                )
                for p in home_players_raw if isinstance(p, dict)
            ]
            
        if away_players_raw:
            away_players = [
                PlayerAttributes(
                    name=p.get("name", "Unknown"),
                    position=p.get("position", "CM"),
                    overall_rating=p.get("overall_rating", p.get("overall", 75)),
                    pace=p.get("pace", 70),
                    shooting=p.get("shooting", 65),
                    passing=p.get("passing", 70),
                    dribbling=p.get("dribbling", 68),
                    defending=p.get("defending", 50),
                    physical=p.get("physical", 70),
                )
                for p in away_players_raw if isinstance(p, dict)
            ]
        
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
    async def get_prediction_by_id(cls, prediction_id: str, user_id: str) -> dict:
        """Get a single prediction by ID"""
        prediction = await PredictionRepository.find_by_id(prediction_id)
        
        if not prediction:
            return {"success": False, "error": "Predicción no encontrada"}
            
        if prediction.user_id != user_id:
            return {"success": False, "error": "No tienes permiso para ver esta predicción"}
            
        return {
            "success": True,
            "data": prediction.to_dict()
        }
    
    @classmethod
    async def get_available_matches(cls, league_id: int = 39) -> dict:
        """
        Get upcoming matches for a league
        Optimized: Returns cached/mock data quickly to avoid slow API calls on home screen
        """
        try:
            # Try to get real fixtures (with timeout to avoid blocking)
            matches = await asyncio.wait_for(
                FootballAPIClient.get_upcoming_fixtures(league_id, limit=10),
                timeout=3.0  # 3 second timeout
            )
            
            if matches:
                return {
                    "success": True,
                    "data": {
                        "matches": [m.to_dict() for m in matches],
                    }
                }
        except (asyncio.TimeoutError, Exception) as e:
            print(f"⚠️ Slow API call for matches, using mock data: {e}")
        
        # Fallback: Return mock/featured matches quickly
        # This ensures home screen loads fast even if external API is slow
        mock_matches = [
            {
                "id": "mock_1",
                "home_team": {"name": "Real Madrid", "logo": ""},
                "away_team": {"name": "Barcelona", "logo": ""},
                "date": "2024-12-20T20:00:00Z",
                "status": "scheduled",
                "league": "La Liga"
            },
            {
                "id": "mock_2",
                "home_team": {"name": "Manchester City", "logo": ""},
                "away_team": {"name": "Liverpool", "logo": ""},
                "date": "2024-12-21T15:00:00Z",
                "status": "scheduled",
                "league": "Premier League"
            },
            {
                "id": "mock_3",
                "home_team": {"name": "Bayern Munich", "logo": ""},
                "away_team": {"name": "Borussia Dortmund", "logo": ""},
                "date": "2024-12-22T18:00:00Z",
                "status": "scheduled",
                "league": "Bundesliga"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "matches": mock_matches,
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
