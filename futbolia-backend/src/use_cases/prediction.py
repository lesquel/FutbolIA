"""
Prediction Use Cases
Core business logic for match predictions using RAG + DeepSeek
"""

import asyncio

import httpx

from src.domain.entities import Match, Prediction, Team
from src.infrastructure.chromadb.player_store import PlayerVectorStore
from src.infrastructure.db.prediction_repository import PredictionRepository
from src.infrastructure.external_api.api_selector import UnifiedAPIClient
from src.infrastructure.external_api.football_api import FootballAPIClient
from src.infrastructure.llm.dixie import DixieAI


class PredictionUseCase:
    """Use case for generating match predictions"""

    @classmethod
    async def predict_match(
        cls, home_team_name: str, away_team_name: str, user_id: str, language: str = "es"
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
            TeamRepository.find_by_name(home_team_name), TeamRepository.find_by_name(away_team_name)
        )

        # If not in local DB, try external API with fallback (Parallelized)
        async def get_team_or_fetch(team_name: str, existing_team: Team | None) -> Team | None:
            """Helper to return existing team or fetch from API"""
            if existing_team:
                return existing_team
            return await UnifiedAPIClient.get_team_by_name(team_name)

        home_team, away_team = await asyncio.gather(
            get_team_or_fetch(home_team_name, home_team),
            get_team_or_fetch(away_team_name, away_team),
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
                for p in home_players_raw
                if isinstance(p, dict)
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
                for p in away_players_raw
                if isinstance(p, dict)
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
                },
            },
        }

    @classmethod
    async def get_prediction_by_id(cls, prediction_id: str, user_id: str) -> dict:
        """Get a single prediction by ID"""
        prediction = await PredictionRepository.find_by_id(prediction_id)

        if not prediction:
            return {"success": False, "error": "Predicción no encontrada"}

        if prediction.user_id != user_id:
            return {"success": False, "error": "No tienes permiso para ver esta predicción"}

        return {"success": True, "data": prediction.to_dict()}

    @classmethod
    async def get_available_matches(cls) -> dict:
        """
        Get next 5 upcoming matches from Premier League only.

        Fetches matches exclusively from Premier League (first division).
        Returns next 5 matches sorted by date.
        """
        from datetime import datetime, timedelta

        from src.infrastructure.external_api.football_api import FootballAPIClient

        # Solo Premier League
        top_leagues = {
            "Premier League": "PL",
        }

        all_matches = []
        current_date = datetime.now()

        # Helper function to parse dates with time
        def parse_match_date(date_str: str, time_str: str = None) -> datetime | None:
            """Parse match date and time, returning a datetime object"""
            if not date_str:
                return None
            try:
                # Si ya tiene formato ISO completo con hora (ej: "2025-01-16T20:00:00Z")
                if "T" in date_str:
                    # Remover Z y cualquier offset de zona horaria
                    clean_date = date_str.replace("Z", "").split("+")[0]
                    try:
                        dt = datetime.fromisoformat(clean_date)
                        return dt
                    except ValueError:
                        # Si falla, intentar parsear manualmente
                        date_part, time_part = clean_date.split("T")
                        year, month, day = map(int, date_part.split("-"))
                        hour, minute = map(int, time_part.split(":")[:2])
                        return datetime(year, month, day, hour, minute)

                # Si solo tiene fecha, combinar con hora si está disponible
                date_part = datetime.strptime(date_str, "%Y-%m-%d")
                if time_str:
                    try:
                        # Parsear hora (formato HH:MM o HH:MM:SS)
                        time_parts = time_str.split(":")
                        hour = int(time_parts[0])
                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                        return date_part.replace(hour=hour, minute=minute)
                    except (ValueError, IndexError):
                        pass
                # Si no hay hora, usar mediodía como default (mejor que medianoche)
                return date_part.replace(hour=12, minute=0)
            except Exception as e:
                print(f"⚠️ Error parsing date: {date_str}, time: {time_str}, error: {e}")
                return None

        # Helper para crear un ID único del partido (evitar duplicados)
        def get_match_key(match: dict) -> str:
            """Generate unique key for a match to detect duplicates"""
            home = match.get("home_team", {}).get("name", "").lower().strip()
            away = match.get("away_team", {}).get("name", "").lower().strip()
            date = match.get("date", "")[:10]  # Solo la fecha (YYYY-MM-DD)
            return f"{home}_{away}_{date}"

        seen_matches = set()  # Para eliminar duplicados

        # Try to get matches from TheSportsDB first (FREE, no API key)
        try:
            # TheSportsDB league ID solo para Premier League
            # ID: (display_name, expected_strLeague_values)
            tsdb_league_ids = {
                "4328": ("Premier League", ["English Premier League", "Premier League"]),
            }

            for tsdb_id, (display_name, valid_league_names) in tsdb_league_ids.items():
                try:
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        response = await client.get(
                            "https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php",
                            params={"id": tsdb_id},
                        )

                        if response.status_code == 200:
                            data = response.json()
                            events = data.get("events") or []
                            print(
                                f"📊 TheSportsDB returned {len(events)} events for {display_name}"
                            )

                            events_checked = 0
                            events_filtered_league = 0
                            events_filtered_past = 0
                            events_added = 0

                            for event in events[:20]:  # Revisar más eventos para tener opciones
                                events_checked += 1

                                # Validar que el partido sea realmente de la liga esperada
                                event_league = event.get("strLeague", "")
                                if not any(valid in event_league for valid in valid_league_names):
                                    # Saltear partidos que no son de la liga correcta
                                    events_filtered_league += 1
                                    continue

                                # Parsear fecha y hora correctamente
                                date_str = event.get("dateEvent", "")
                                time_str = event.get("strTime", "00:00:00")

                                # Asegurar formato correcto de hora
                                if time_str and len(time_str) == 5:  # "19:00"
                                    time_str = f"{time_str}:00"

                                # Parsear fecha completa con hora
                                event_datetime = parse_match_date(date_str, time_str)

                                # Solo incluir partidos FUTUROS (solo verificar que sea futuro, no necesariamente 1 hora)
                                if event_datetime and event_datetime > current_date:
                                    # Crear datetime completo en formato ISO con zona UTC
                                    datetime_iso = f"{date_str}T{time_str}Z" if date_str else ""

                                    match_data = {
                                        "id": f"tsdb_{event.get('idEvent', '')}",
                                        "home_team": {
                                            "name": event.get("strHomeTeam", ""),
                                            "logo_url": event.get("strHomeTeamBadge", ""),
                                        },
                                        "away_team": {
                                            "name": event.get("strAwayTeam", ""),
                                            "logo_url": event.get("strAwayTeamBadge", ""),
                                        },
                                        "date": datetime_iso,  # Formato ISO completo con zona UTC
                                        "time": time_str,
                                        "status": "scheduled",
                                        "league": display_name,  # Usar nombre display normalizado
                                        "venue": event.get("strVenue", ""),
                                    }

                                    # Verificar duplicados antes de agregar
                                    match_key = get_match_key(match_data)
                                    if match_key not in seen_matches:
                                        seen_matches.add(match_key)
                                        all_matches.append(match_data)
                                        events_added += 1
                                else:
                                    events_filtered_past += 1

                            print(
                                f"✅ TheSportsDB: {events_checked} checked, {events_filtered_league} filtered (league), {events_filtered_past} filtered (past), {events_added} added"
                            )
                        else:
                            print(f"⚠️ TheSportsDB returned status {response.status_code}")
                except Exception as e:
                    print(f"⚠️ Error getting {display_name} matches from TheSportsDB: {e}")
                    continue
        except Exception as e:
            print(f"⚠️ TheSportsDB failed: {e}")

        # Fallback to Football-Data.org if TheSportsDB didn't return enough matches
        if len(all_matches) < 5:
            try:
                for league_name, league_code in top_leagues.items():
                    try:
                        matches = await asyncio.wait_for(
                            FootballAPIClient.get_upcoming_fixtures(league_code, limit=10),
                            timeout=3.0,
                        )

                        for match in matches:
                            match_dict = match.to_dict()
                            match_dict["league"] = league_name
                            # Ensure logo_url key consistency
                            if "home_team" in match_dict:
                                match_dict["home_team"]["logo_url"] = match_dict["home_team"].get(
                                    "logo_url", ""
                                )
                            if "away_team" in match_dict:
                                match_dict["away_team"]["logo_url"] = match_dict["away_team"].get(
                                    "logo_url", ""
                                )

                            # Verificar que sea futuro y no duplicado
                            match_date = parse_match_date(match_dict.get("date", ""))
                            if match_date and match_date > current_date:
                                match_key = get_match_key(match_dict)
                                if match_key not in seen_matches:
                                    seen_matches.add(match_key)
                                    all_matches.append(match_dict)
                    except (TimeoutError, Exception) as e:
                        print(f"⚠️ Error getting {league_name} from Football-Data.org: {e}")
                        continue
            except Exception as e:
                print(f"⚠️ Football-Data.org failed: {e}")

        # Sort by date and get only the next 5 matches
        # Filtrar solo partidos futuros y solo Premier League
        future_matches = []
        for m in all_matches:
            match_date = parse_match_date(m.get("date", ""))
            league = m.get("league", "").lower()

            # Verificar que sea futuro y Premier League
            if (
                match_date
                and match_date > current_date
                and league in ["premier league", "english premier league"]
            ):
                future_matches.append(m)

        # Ordenar por fecha (más cercanos primero)
        future_matches.sort(key=lambda x: parse_match_date(x.get("date", "")) or datetime.max)

        # Retornar solo los próximos 5 partidos únicos
        all_matches = future_matches[:5]

        # Debug: mostrar información sobre los partidos obtenidos
        print(
            f"📊 Total matches after filtering: {len(future_matches)} (returning {len(all_matches)})"
        )
        if future_matches:
            print(f"📅 First match date: {future_matches[0].get('date', 'N/A')}")
            print(f"📅 Last match date: {future_matches[-1].get('date', 'N/A')}")

        # If we still don't have matches, generate realistic mock data
        if not all_matches:
            print(
                f"⚠️ No matches from APIs (checked {len(seen_matches)} unique matches), using mock data with realistic dates (Premier League only)"
            )

            # Generate dates for next week - Solo Premier League
            mock_matches = [
                ("Manchester City", "Liverpool", "Premier League"),
                ("Arsenal", "Chelsea", "Premier League"),
                ("Tottenham Hotspur", "Manchester United", "Premier League"),
                ("Newcastle United", "Brighton & Hove Albion", "Premier League"),
                ("Aston Villa", "West Ham United", "Premier League"),
            ]

            for i, (home, away, league) in enumerate(mock_matches):
                match_date = current_date + timedelta(days=i + 1)
                # Formato ISO completo con hora UTC
                datetime_iso = match_date.strftime("%Y-%m-%dT20:00:00Z")
                all_matches.append(
                    {
                        "id": f"mock_{i + 1}",
                        "home_team": {"name": home, "logo_url": ""},
                        "away_team": {"name": away, "logo_url": ""},
                        "date": datetime_iso,  # Formato ISO completo
                        "time": "20:00:00",
                        "status": "scheduled",
                        "league": league,
                        "venue": f"Estadio de {home}",
                    }
                )

        print(f"✅ Returning {len(all_matches)} matches for frontend")

        return {
            "success": True,
            "data": {
                "matches": all_matches,
            },
        }

    @classmethod
    async def get_player_comparison(cls, team_a: str, team_b: str) -> dict:
        """Get player comparison data for two teams"""
        comparison = PlayerVectorStore.get_player_comparison(team_a, team_b)

        return {
            "success": True,
            "data": comparison,
        }
