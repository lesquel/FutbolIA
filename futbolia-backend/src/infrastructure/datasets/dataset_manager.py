"""
Dataset Manager Module
Acceso rápido a datos locales para minería de datos y predicciones
Evita llamadas API en tiempo real usando datasets pre-descargados
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from src.core.logger import get_logger
from src.infrastructure.datasets.league_registry import (
    GLOBAL_LEAGUES,
    LeagueRegistry,
)

logger = get_logger(__name__)


class DatasetManager:
    """
    Gestor de datasets locales para acceso ultrarrápido

    Beneficios:
    - Acceso en <10ms vs 500ms+ de APIs
    - Sin rate limits
    - Sin dependencia de conectividad
    - Datos consistentes para minería

    Uso típico:
        manager = DatasetManager()
        standings = await manager.get_standings("PL")
        teams = await manager.get_teams("ECU")
        matches = await manager.get_recent_matches("ARG", days=30)
    """

    def __init__(self, data_dir: str = "./data/datasets"):
        self.data_dir = Path(data_dir)
        self.leagues_dir = self.data_dir / "leagues"
        self.teams_dir = self.data_dir / "teams"
        self.players_dir = self.data_dir / "players"

        # Cache en memoria para acceso ultrarrápido
        self._memory_cache: dict[str, tuple[Any, datetime]] = {}
        self._cache_ttl = timedelta(minutes=30)  # TTL de cache en memoria

    def _cache_key(self, *args) -> str:
        """Generar clave de cache"""
        return ":".join(str(a) for a in args)

    def _get_from_cache(self, key: str) -> Any | None:
        """Obtener de cache en memoria si no expiró"""
        if key in self._memory_cache:
            data, cached_at = self._memory_cache[key]
            if datetime.now() - cached_at < self._cache_ttl:
                return data
            del self._memory_cache[key]
        return None

    def _set_cache(self, key: str, data: Any):
        """Guardar en cache en memoria"""
        self._memory_cache[key] = (data, datetime.now())

    def _load_json_sync(self, filepath: Path) -> Any | None:
        """Cargar JSON de forma síncrona (más rápido para archivos pequeños)"""
        if not filepath.exists():
            return None
        try:
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error cargando {filepath}: {e}")
            return None

    # =========================================================================
    # ACCESO A DATOS DE LIGAS
    # =========================================================================

    async def get_standings(self, league_code: str, season: str | None = None) -> list[dict] | None:
        """
        Obtener tabla de posiciones de una liga

        Args:
            league_code: Código de la liga (ej: 'PL', 'ECU', 'ARG')
            season: Temporada específica (ej: '2025-2026'), usa actual si None

        Returns:
            Lista de equipos con estadísticas de tabla
        """
        league = LeagueRegistry.get_league(league_code)
        if not league:
            logger.warning(f"⚠️ Liga no encontrada: {league_code}")
            return None

        season = season or league.get_current_season()
        cache_key = self._cache_key("standings", league_code, season)

        # Verificar cache en memoria
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # Cargar de archivo
        filepath = self.leagues_dir / league_code / f"standings_{season.replace('-', '_')}.json"
        data = self._load_json_sync(filepath)

        if data and "standings" in data:
            # Para Football-Data, extraer la tabla correcta
            standings = data["standings"]
            if (
                isinstance(standings, list)
                and len(standings) > 0
                and isinstance(standings[0], dict)
                and "table" in standings[0]
            ):
                standings = standings[0]["table"]

            self._set_cache(cache_key, standings)
            return standings

        return None

    async def get_teams(self, league_code: str) -> list[dict] | None:
        """
        Obtener todos los equipos de una liga

        Args:
            league_code: Código de la liga

        Returns:
            Lista de equipos con información básica
        """
        cache_key = self._cache_key("teams", league_code)

        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        filepath = self.leagues_dir / league_code / "teams.json"
        data = self._load_json_sync(filepath)

        if data and "teams" in data:
            self._set_cache(cache_key, data["teams"])
            return data["teams"]

        return None

    async def get_matches(
        self,
        league_code: str,
        season: str | None = None,
        status: str | None = None,  # 'FINISHED', 'SCHEDULED', None=todos
        days_back: int | None = None,
        days_forward: int | None = None,
    ) -> list[dict] | None:
        """
        Obtener partidos de una liga con filtros

        Args:
            league_code: Código de la liga
            season: Temporada específica
            status: Filtrar por estado del partido
            days_back: Partidos de los últimos N días
            days_forward: Partidos de los próximos N días

        Returns:
            Lista de partidos filtrados
        """
        league = LeagueRegistry.get_league(league_code)
        if not league:
            return None

        season = season or league.get_current_season()
        filepath = self.leagues_dir / league_code / f"matches_{season.replace('-', '_')}.json"
        data = self._load_json_sync(filepath)

        if not data or "matches" not in data:
            return None

        matches = data["matches"]

        # Aplicar filtros
        if status:
            matches = [m for m in matches if m.get("status") == status]

        today = datetime.now().date()

        if days_back is not None:
            cutoff = today - timedelta(days=days_back)
            matches = [
                m
                for m in matches
                if m.get("date") and datetime.strptime(m["date"], "%Y-%m-%d").date() >= cutoff
            ]

        if days_forward is not None:
            cutoff = today + timedelta(days=days_forward)
            matches = [
                m
                for m in matches
                if m.get("date") and datetime.strptime(m["date"], "%Y-%m-%d").date() <= cutoff
            ]

        return matches

    async def get_upcoming_matches(self, league_code: str, limit: int = 10) -> list[dict] | None:
        """Obtener próximos partidos programados"""
        matches = await self.get_matches(league_code, status="SCHEDULED", days_forward=30)

        if matches:
            # Ordenar por fecha
            matches.sort(key=lambda m: m.get("date", "9999-12-31"))
            return matches[:limit]

        return None

    async def get_recent_results(self, league_code: str, limit: int = 10) -> list[dict] | None:
        """Obtener resultados recientes"""
        matches = await self.get_matches(league_code, status="FINISHED", days_back=30)

        if matches:
            # Ordenar por fecha descendente
            matches.sort(key=lambda m: m.get("date", "0000-01-01"), reverse=True)
            return matches[:limit]

        return None

    # =========================================================================
    # ACCESO A DATOS DE EQUIPOS
    # =========================================================================

    async def get_team_by_name(self, team_name: str, league_code: str | None = None) -> dict | None:
        """
        Buscar equipo por nombre en los datasets locales

        Args:
            team_name: Nombre del equipo (búsqueda fuzzy)
            league_code: Opcional - limitar búsqueda a una liga

        Returns:
            Información del equipo encontrado
        """
        team_name_lower = team_name.lower()

        # Si se especifica liga, buscar solo ahí
        if league_code:
            teams = await self.get_teams(league_code)
            if teams:
                for team in teams:
                    if team_name_lower in team.get("name", "").lower():
                        return team
        else:
            # Buscar en todas las ligas
            for code in GLOBAL_LEAGUES:
                teams = await self.get_teams(code)
                if teams:
                    for team in teams:
                        if team_name_lower in team.get("name", "").lower():
                            team["league_code"] = code
                            return team

        return None

    async def get_team_squad(self, team_name: str) -> list[dict] | None:
        """Obtener plantilla de un equipo"""
        safe_name = team_name.lower().replace(" ", "_").replace(".", "")
        filepath = self.teams_dir / f"{safe_name}_squad.json"
        data = self._load_json_sync(filepath)

        if data and "players" in data:
            return data["players"]

        return None

    async def get_team_form(self, team_name: str, league_code: str, last_n: int = 5) -> dict | None:
        """
        Calcular forma reciente de un equipo

        Returns:
            Dict con: form_string (ej: 'WWDLW'), points, wins, draws, losses
        """
        matches = await self.get_matches(league_code, status="FINISHED", days_back=60)

        if not matches:
            return None

        team_name_lower = team_name.lower()
        team_matches = []

        for match in matches:
            home = match.get("homeTeam", {}).get("name", "").lower()
            away = match.get("awayTeam", {}).get("name", "").lower()

            if team_name_lower in home or team_name_lower in away:
                team_matches.append(match)

        # Ordenar por fecha descendente y tomar los últimos N
        team_matches.sort(key=lambda m: m.get("date", "0000-01-01"), reverse=True)
        team_matches = team_matches[:last_n]

        if not team_matches:
            return None

        form_string = ""
        wins, draws, losses = 0, 0, 0

        for match in team_matches:
            score = match.get("score", {})
            home_score = score.get("home")
            away_score = score.get("away")

            if home_score is None or away_score is None:
                continue

            home_name = match.get("homeTeam", {}).get("name", "").lower()
            is_home = team_name_lower in home_name

            if is_home:
                if home_score > away_score:
                    form_string += "W"
                    wins += 1
                elif home_score < away_score:
                    form_string += "L"
                    losses += 1
                else:
                    form_string += "D"
                    draws += 1
            else:
                if away_score > home_score:
                    form_string += "W"
                    wins += 1
                elif away_score < home_score:
                    form_string += "L"
                    losses += 1
                else:
                    form_string += "D"
                    draws += 1

        return {
            "form_string": form_string,
            "matches_analyzed": len(team_matches),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "points": wins * 3 + draws,
            "form_rating": round((wins * 3 + draws) / (len(team_matches) * 3) * 100, 1)
            if team_matches
            else 0,
        }

    # =========================================================================
    # DATOS PARA MINERÍA DE DATOS
    # =========================================================================

    async def get_clustering_data(self, league_code: str) -> list[dict] | None:
        """
        Obtener datos preparados para clustering de equipos

        Returns:
            Lista de equipos con features para clustering
        """
        standings = await self.get_standings(league_code)

        if not standings:
            return None

        # Asegurar que todos los campos necesarios existen
        clustering_data = []

        for entry in standings:
            team_info = entry.get("team", {})
            played = max(entry.get("playedGames", 1), 1)

            clustering_data.append(
                {
                    "team": team_info,
                    "position": entry.get("position", 0),
                    "playedGames": played,
                    "won": entry.get("won", 0),
                    "draw": entry.get("draw", 0),
                    "lost": entry.get("lost", 0),
                    "points": entry.get("points", 0),
                    "goalsFor": entry.get("goalsFor", 0),
                    "goalsAgainst": entry.get("goalsAgainst", 0),
                    "goalDifference": entry.get("goalDifference", 0),
                    # Features derivadas
                    "points_per_game": round(entry.get("points", 0) / played, 2),
                    "goals_per_game": round(entry.get("goalsFor", 0) / played, 2),
                    "goals_against_per_game": round(entry.get("goalsAgainst", 0) / played, 2),
                    "win_rate": round(entry.get("won", 0) / played * 100, 1),
                }
            )

        return clustering_data

    async def get_prediction_features(
        self, home_team: str, away_team: str, league_code: str
    ) -> dict | None:
        """
        Obtener features para modelo de predicción

        Returns:
            Dict con features de ambos equipos para ML
        """
        standings = await self.get_standings(league_code)

        if not standings:
            return None

        home_data = None
        away_data = None

        for entry in standings:
            team_name = entry.get("team", {}).get("name", "").lower()

            if home_team.lower() in team_name:
                home_data = entry
            elif away_team.lower() in team_name:
                away_data = entry

        if not home_data or not away_data:
            return None

        # Obtener forma reciente
        home_form = await self.get_team_form(home_team, league_code)
        away_form = await self.get_team_form(away_team, league_code)

        def extract_features(data: dict, form: dict | None, prefix: str) -> dict:
            played = max(data.get("playedGames", 1), 1)
            return {
                f"{prefix}_position": data.get("position", 0),
                f"{prefix}_points": data.get("points", 0),
                f"{prefix}_points_per_game": round(data.get("points", 0) / played, 2),
                f"{prefix}_goal_diff": data.get("goalDifference", 0),
                f"{prefix}_goals_per_game": round(data.get("goalsFor", 0) / played, 2),
                f"{prefix}_conceded_per_game": round(data.get("goalsAgainst", 0) / played, 2),
                f"{prefix}_win_rate": round(data.get("won", 0) / played * 100, 1),
                f"{prefix}_form_rating": form.get("form_rating", 50) if form else 50,
                f"{prefix}_recent_wins": form.get("wins", 0) if form else 0,
            }

        features = {
            **extract_features(home_data, home_form, "home"),
            **extract_features(away_data, away_form, "away"),
            # Features comparativas
            "position_diff": home_data.get("position", 0) - away_data.get("position", 0),
            "points_diff": home_data.get("points", 0) - away_data.get("points", 0),
            "goal_diff_diff": home_data.get("goalDifference", 0)
            - away_data.get("goalDifference", 0),
        }

        return features

    async def get_historical_h2h(
        self, team1: str, team2: str, league_code: str, seasons: int = 3
    ) -> dict | None:
        """
        Obtener historial head-to-head entre dos equipos

        Returns:
            Estadísticas de enfrentamientos directos
        """
        league = LeagueRegistry.get_league(league_code)
        if not league:
            return None

        current_season = league.get_current_season()
        start_year = int(current_season.split("-")[0])

        h2h_matches = []
        team1_lower = team1.lower()
        team2_lower = team2.lower()

        # Buscar en las últimas N temporadas
        for offset in range(seasons):
            year = start_year - offset
            season = f"{year}-{year + 1}"

            matches = await self.get_matches(league_code, season=season)
            if not matches:
                continue

            for match in matches:
                home = match.get("homeTeam", {}).get("name", "").lower()
                away = match.get("awayTeam", {}).get("name", "").lower()

                if (team1_lower in home and team2_lower in away) or (
                    team2_lower in home and team1_lower in away
                ):
                    h2h_matches.append(match)

        if not h2h_matches:
            return None

        # Calcular estadísticas
        team1_wins, team2_wins, draws = 0, 0, 0
        team1_goals, team2_goals = 0, 0

        for match in h2h_matches:
            score = match.get("score", {})
            home_score = score.get("home")
            away_score = score.get("away")

            if home_score is None or away_score is None:
                continue

            home_name = match.get("homeTeam", {}).get("name", "").lower()

            if team1_lower in home_name:
                team1_goals += home_score
                team2_goals += away_score
                if home_score > away_score:
                    team1_wins += 1
                elif home_score < away_score:
                    team2_wins += 1
                else:
                    draws += 1
            else:
                team2_goals += home_score
                team1_goals += away_score
                if home_score > away_score:
                    team2_wins += 1
                elif home_score < away_score:
                    team1_wins += 1
                else:
                    draws += 1

        return {
            "team1": team1,
            "team2": team2,
            "total_matches": len(h2h_matches),
            "team1_wins": team1_wins,
            "team2_wins": team2_wins,
            "draws": draws,
            "team1_goals": team1_goals,
            "team2_goals": team2_goals,
            "matches": h2h_matches,
        }

    # =========================================================================
    # ESTADÍSTICAS Y UTILIDADES
    # =========================================================================

    def get_available_leagues(self) -> list[str]:
        """Listar ligas con datos descargados"""
        if not self.leagues_dir.exists():
            return []

        return [d.name for d in self.leagues_dir.iterdir() if d.is_dir() and list(d.glob("*.json"))]

    async def get_league_summary(self, league_code: str) -> dict | None:
        """Obtener resumen de datos disponibles para una liga"""
        league = LeagueRegistry.get_league(league_code)
        if not league:
            return None

        league_dir = self.leagues_dir / league_code
        if not league_dir.exists():
            return {"league": league_code, "status": "no_data"}

        files = list(league_dir.glob("*.json"))
        standings = await self.get_standings(league_code)
        teams = await self.get_teams(league_code)

        return {
            "league_code": league_code,
            "league_name": league.name,
            "country": league.country,
            "tier": league.tier.name,
            "data_files": [f.name for f in files],
            "teams_count": len(teams) if teams else 0,
            "standings_count": len(standings) if standings else 0,
            "current_season": league.get_current_season(),
        }

    def clear_memory_cache(self):
        """Limpiar cache en memoria"""
        self._memory_cache.clear()
        logger.info("🧹 Cache en memoria limpiado")
