"""
Prediction Use Cases
Core business logic for match predictions using RAG + DeepSeek
"""
import asyncio
import httpx
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
        Get upcoming matches from the top 5 leagues (men's football)
        
        Top 5 Leagues:
        - Premier League (PL) - ID: 2021
        - La Liga (PD) - ID: 2014
        - Serie A (SA) - ID: 2019
        - Bundesliga (BL1) - ID: 2002
        - Ligue 1 (FL1) - ID: 2015
        
        Returns next 5 matches from each league (25 total, but limited to 25)
        """
        from src.infrastructure.external_api.thesportsdb import TheSportsDBClient
        from src.infrastructure.external_api.football_api import FootballAPIClient
        from datetime import datetime, timedelta
        
        # Top 5 leagues mapping (Football-Data.org codes)
        TOP_LEAGUES = {
            "Premier League": "PL",
            "La Liga": "PD",
            "Serie A": "SA",
            "Bundesliga": "BL1",
            "Ligue 1": "FL1",
        }
        
        all_matches = []
        current_date = datetime.now()
        
        # Helper function to parse dates
        def parse_match_date(date_str: str) -> Optional[datetime]:
            if not date_str:
                return None
            try:
                if "T" in date_str:
                    return datetime.fromisoformat(date_str.replace("Z", "").split("+")[0])
                return datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                return None
        
        # Try to get matches from TheSportsDB first (FREE, no API key)
        try:
            # TheSportsDB league IDs for top 5 leagues
            tsdb_league_ids = {
                "Premier League": "4328",
                "La Liga": "4335",
                "Serie A": "4332",
                "Bundesliga": "4331",
                "Ligue 1": "4334",
            }
            
            for league_name, league_id in tsdb_league_ids.items():
                try:
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        response = await client.get(
                            "https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php",
                            params={"id": league_id}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            events = data.get("events") or []
                            
                            for event in events[:5]:
                                event_date = parse_match_date(event.get("dateEvent", ""))
                                
                                # Only include future matches (within next 30 days)
                                if event_date and event_date >= current_date:
                                    all_matches.append({
                                        "id": f"tsdb_{event.get('idEvent', '')}",
                                        "home_team": {
                                            "name": event.get("strHomeTeam", ""),
                                            "logo_url": event.get("strHomeTeamBadge", ""),
                                        },
                                        "away_team": {
                                            "name": event.get("strAwayTeam", ""),
                                            "logo_url": event.get("strAwayTeamBadge", ""),
                                        },
                                        "date": event.get("dateEvent", ""),
                                        "time": event.get("strTime", ""),
                                        "status": "scheduled",
                                        "league": league_name,
                                        "venue": event.get("strVenue", ""),
                                    })
                except Exception as e:
                    print(f"⚠️ Error getting {league_name} matches from TheSportsDB: {e}")
                    continue
        except Exception as e:
            print(f"⚠️ TheSportsDB failed: {e}")
        
        # Fallback to Football-Data.org if TheSportsDB didn't return enough matches
        if len(all_matches) < 5:
            try:
                for league_name, league_code in TOP_LEAGUES.items():
                    try:
                        matches = await asyncio.wait_for(
                            FootballAPIClient.get_upcoming_fixtures(league_code, limit=5),
                            timeout=3.0
                        )
                        
                        for match in matches[:5]:
                            match_dict = match.to_dict()
                            match_dict["league"] = league_name
                            # Ensure logo_url key consistency
                            if "home_team" in match_dict:
                                match_dict["home_team"]["logo_url"] = match_dict["home_team"].get("logo_url", "")
                            if "away_team" in match_dict:
                                match_dict["away_team"]["logo_url"] = match_dict["away_team"].get("logo_url", "")
                            all_matches.append(match_dict)
                    except (asyncio.TimeoutError, Exception) as e:
                        print(f"⚠️ Error getting {league_name} from Football-Data.org: {e}")
                        continue
            except Exception as e:
                print(f"⚠️ Football-Data.org failed: {e}")
        
        # Sort by date
        all_matches.sort(key=lambda x: x.get("date", "9999-12-31"))
        all_matches = all_matches[:25]
        
        # If we still don't have matches, generate realistic mock data
        if not all_matches:
            print("⚠️ No matches from APIs, using mock data with realistic dates")
            
            # Generate dates for next week
            mock_matches = [
                ("Real Madrid", "Barcelona", "La Liga"),
                ("Manchester City", "Liverpool", "Premier League"),
                ("Bayern Munich", "Borussia Dortmund", "Bundesliga"),
                ("Inter Milan", "Juventus", "Serie A"),
                ("Paris Saint-Germain", "Marseille", "Ligue 1"),
            ]
            
            for i, (home, away, league) in enumerate(mock_matches):
                match_date = current_date + timedelta(days=i + 1)
                all_matches.append({
                    "id": f"mock_{i + 1}",
                    "home_team": {"name": home, "logo_url": ""},
                    "away_team": {"name": away, "logo_url": ""},
                    "date": match_date.strftime("%Y-%m-%d"),
                    "time": "20:00",
                    "status": "scheduled",
                    "league": league,
                    "venue": f"Estadio de {home}",
                })
        
        print(f"✅ Returning {len(all_matches)} matches for frontend")
        
        return {
            "success": True,
            "data": {
                "matches": all_matches,
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
