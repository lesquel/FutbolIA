"""
Data Downloader Module
Descarga masiva de datos desde múltiples APIs y almacenamiento local
Optimizado para minimizar llamadas API y maximizar velocidad de acceso
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiofiles
import httpx

from src.core.logger import get_logger
from src.infrastructure.datasets.league_registry import (
    LeagueRegistry, 
    LeagueInfo, 
    LeagueTier,
    GLOBAL_LEAGUES
)

logger = get_logger(__name__)


class DataDownloader:
    """
    Descargador de datos optimizado para almacenamiento local
    
    Estrategia:
    1. Descargar datos históricos completos una vez
    2. Actualizar incrementalmente solo datos nuevos
    3. Almacenar en formato JSON optimizado para lectura rápida
    
    Estructura de archivos:
    data/
    ├── datasets/
    │   ├── leagues/
    │   │   ├── PL/
    │   │   │   ├── standings_2024.json
    │   │   │   ├── matches_2024.json
    │   │   │   ├── teams.json
    │   │   │   └── metadata.json
    │   │   ├── ECU/
    │   │   └── ...
    │   ├── teams/
    │   │   ├── manchester_city.json
    │   │   └── ...
    │   └── players/
    │       └── ...
    """
    
    # APIs base URLs
    THESPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"
    FOOTBALL_DATA_BASE = "https://api.football-data.org/v4"
    
    def __init__(self, data_dir: str = "./data/datasets"):
        self.data_dir = Path(data_dir)
        self.leagues_dir = self.data_dir / "leagues"
        self.teams_dir = self.data_dir / "teams"
        self.players_dir = self.data_dir / "players"
        self.cache_dir = self.data_dir / "cache"
        
        # Crear directorios
        for dir_path in [self.leagues_dir, self.teams_dir, self.players_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.request_delay = 0.1  # 100ms entre requests
        self.last_request_time: Dict[str, datetime] = {}
    
    async def _rate_limit(self, api_name: str):
        """Aplicar rate limiting por API"""
        delays = {
            "thesportsdb": 0.01,    # 100 req/sec permitidos
            "football_data": 6.0,   # 10 req/min = 6 sec delay
            "api_football": 1.0,    # 100 req/día = conservador
        }
        
        delay = delays.get(api_name, 0.5)
        last_time = self.last_request_time.get(api_name)
        
        if last_time:
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)
        
        self.last_request_time[api_name] = datetime.now()
    
    async def _save_json(self, filepath: Path, data: Any):
        """Guardar datos JSON de forma asíncrona"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(f"✅ Guardado: {filepath}")
    
    async def _load_json(self, filepath: Path) -> Optional[Any]:
        """Cargar datos JSON de forma asíncrona"""
        if not filepath.exists():
            return None
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"❌ Error cargando {filepath}: {e}")
            return None
    
    async def _fetch_thesportsdb(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Realizar request a TheSportsDB con rate limiting"""
        await self._rate_limit("thesportsdb")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.THESPORTSDB_BASE}/{endpoint}",
                    params=params or {}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"⚠️ TheSportsDB {endpoint}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ TheSportsDB error: {e}")
        
        return None
    
    async def _fetch_football_data(self, endpoint: str, api_key: str) -> Optional[Dict]:
        """Realizar request a Football-Data.org con rate limiting"""
        await self._rate_limit("football_data")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.FOOTBALL_DATA_BASE}/{endpoint}",
                    headers={"X-Auth-Token": api_key}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"⚠️ Football-Data {endpoint}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ Football-Data error: {e}")
        
        return None
    
    # =========================================================================
    # DESCARGA DE DATOS DE LIGAS
    # =========================================================================
    
    async def download_league_standings(
        self, 
        league: LeagueInfo, 
        season: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Descargar tabla de posiciones de una liga
        Intenta múltiples fuentes en orden de preferencia
        """
        season = season or league.get_current_season()
        league_dir = self.leagues_dir / league.code
        filepath = league_dir / f"standings_{season.replace('-', '_')}.json"
        
        # Verificar cache local (válido por 1 hora)
        cached = await self._load_json(filepath)
        if cached:
            cached_time = datetime.fromisoformat(cached.get("_downloaded_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(hours=1):
                logger.info(f"📦 Cache hit: {league.code} standings")
                return cached
        
        standings_data = None
        
        # Intento 1: Football-Data.org (más confiable para standings)
        if league.football_data_id and api_key:
            data = await self._fetch_football_data(
                f"competitions/{league.football_data_id}/standings",
                api_key
            )
            if data and "standings" in data:
                standings_data = {
                    "source": "football_data",
                    "league_code": league.code,
                    "league_name": league.name,
                    "season": season,
                    "standings": data["standings"],
                    "_downloaded_at": datetime.now().isoformat(),
                }
        
        # Intento 2: TheSportsDB
        if not standings_data and league.thesportsdb_id:
            # TheSportsDB usa IDs de temporada específicos
            year = int(season.split('-')[0])
            data = await self._fetch_thesportsdb(
                "lookuptable.php",
                {"l": league.thesportsdb_id, "s": str(year)}
            )
            if data and data.get("table"):
                standings_data = {
                    "source": "thesportsdb",
                    "league_code": league.code,
                    "league_name": league.name,
                    "season": season,
                    "standings": self._transform_thesportsdb_standings(data["table"]),
                    "_downloaded_at": datetime.now().isoformat(),
                }
        
        if standings_data:
            await self._save_json(filepath, standings_data)
            return standings_data
        
        logger.warning(f"⚠️ No se pudo descargar standings para {league.code}")
        return None
    
    def _transform_thesportsdb_standings(self, raw_standings: List[Dict]) -> List[Dict]:
        """Transformar formato TheSportsDB al formato estándar"""
        return [
            {
                "position": int(entry.get("intRank", idx + 1)),
                "team": {
                    "id": entry.get("idTeam"),
                    "name": entry.get("strTeam", ""),
                    "crest": entry.get("strTeamBadge", ""),
                },
                "playedGames": int(entry.get("intPlayed", 0)),
                "won": int(entry.get("intWin", 0)),
                "draw": int(entry.get("intDraw", 0)),
                "lost": int(entry.get("intLoss", 0)),
                "points": int(entry.get("intPoints", 0)),
                "goalsFor": int(entry.get("intGoalsFor", 0)),
                "goalsAgainst": int(entry.get("intGoalsAgainst", 0)),
                "goalDifference": int(entry.get("intGoalDifference", 0)),
            }
            for idx, entry in enumerate(raw_standings)
        ]
    
    async def download_league_matches(
        self,
        league: LeagueInfo,
        season: Optional[str] = None,
        include_finished: bool = True,
        include_scheduled: bool = True,
    ) -> Optional[Dict]:
        """
        Descargar partidos de una liga (históricos y programados)
        """
        season = season or league.get_current_season()
        league_dir = self.leagues_dir / league.code
        filepath = league_dir / f"matches_{season.replace('-', '_')}.json"
        
        # Verificar cache (15 min para partidos)
        cached = await self._load_json(filepath)
        if cached:
            cached_time = datetime.fromisoformat(cached.get("_downloaded_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(minutes=15):
                logger.info(f"📦 Cache hit: {league.code} matches")
                return cached
        
        matches_data = None
        
        # Usar TheSportsDB para partidos (mejor cobertura gratuita)
        if league.thesportsdb_id:
            year = int(season.split('-')[0])
            
            all_matches = []
            
            # Partidos terminados
            if include_finished:
                data = await self._fetch_thesportsdb(
                    "eventsseason.php",
                    {"id": league.thesportsdb_id, "s": str(year)}
                )
                if data and data.get("events"):
                    all_matches.extend(data["events"])
            
            # Próximos partidos por ronda
            if include_scheduled:
                next_data = await self._fetch_thesportsdb(
                    "eventsnextleague.php",
                    {"id": league.thesportsdb_id}
                )
                if next_data and next_data.get("events"):
                    all_matches.extend(next_data["events"])
            
            if all_matches:
                matches_data = {
                    "source": "thesportsdb",
                    "league_code": league.code,
                    "league_name": league.name,
                    "season": season,
                    "matches": self._transform_thesportsdb_matches(all_matches),
                    "total_matches": len(all_matches),
                    "_downloaded_at": datetime.now().isoformat(),
                }
        
        if matches_data:
            await self._save_json(filepath, matches_data)
            return matches_data
        
        return None
    
    def _transform_thesportsdb_matches(self, raw_matches: List[Dict]) -> List[Dict]:
        """Transformar formato de partidos TheSportsDB al formato estándar"""
        transformed = []
        
        for match in raw_matches:
            home_score = match.get("intHomeScore")
            away_score = match.get("intAwayScore")
            
            transformed.append({
                "id": match.get("idEvent"),
                "date": match.get("dateEvent"),
                "time": match.get("strTime", "00:00"),
                "status": "FINISHED" if home_score is not None else "SCHEDULED",
                "matchday": match.get("intRound"),
                "homeTeam": {
                    "id": match.get("idHomeTeam"),
                    "name": match.get("strHomeTeam"),
                    "logo": match.get("strHomeTeamBadge"),
                },
                "awayTeam": {
                    "id": match.get("idAwayTeam"),
                    "name": match.get("strAwayTeam"),
                    "logo": match.get("strAwayTeamBadge"),
                },
                "score": {
                    "home": int(home_score) if home_score else None,
                    "away": int(away_score) if away_score else None,
                },
                "venue": match.get("strVenue"),
            })
        
        return transformed
    
    async def download_league_teams(self, league: LeagueInfo) -> Optional[Dict]:
        """Descargar todos los equipos de una liga"""
        league_dir = self.leagues_dir / league.code
        filepath = league_dir / "teams.json"
        
        # Cache válido por 24 horas
        cached = await self._load_json(filepath)
        if cached:
            cached_time = datetime.fromisoformat(cached.get("_downloaded_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(hours=24):
                logger.info(f"📦 Cache hit: {league.code} teams")
                return cached
        
        if league.thesportsdb_id:
            data = await self._fetch_thesportsdb(
                "lookup_all_teams.php",
                {"id": league.thesportsdb_id}
            )
            
            if data and data.get("teams"):
                teams_data = {
                    "source": "thesportsdb",
                    "league_code": league.code,
                    "league_name": league.name,
                    "teams": [
                        {
                            "id": t.get("idTeam"),
                            "name": t.get("strTeam"),
                            "short_name": t.get("strTeamShort"),
                            "logo": t.get("strTeamBadge"),
                            "stadium": t.get("strStadium"),
                            "stadium_capacity": t.get("intStadiumCapacity"),
                            "country": t.get("strCountry"),
                            "founded": t.get("intFormedYear"),
                            "description": t.get("strDescriptionEN"),
                        }
                        for t in data["teams"]
                    ],
                    "total_teams": len(data["teams"]),
                    "_downloaded_at": datetime.now().isoformat(),
                }
                
                await self._save_json(filepath, teams_data)
                return teams_data
        
        return None
    
    # =========================================================================
    # DESCARGA DE DATOS DE EQUIPOS Y JUGADORES
    # =========================================================================
    
    async def download_team_squad(self, team_id: str, team_name: str) -> Optional[Dict]:
        """Descargar plantilla completa de un equipo"""
        safe_name = team_name.lower().replace(" ", "_").replace(".", "")
        filepath = self.teams_dir / f"{safe_name}_squad.json"
        
        # Cache válido por 7 días
        cached = await self._load_json(filepath)
        if cached:
            cached_time = datetime.fromisoformat(cached.get("_downloaded_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(days=7):
                logger.info(f"📦 Cache hit: {team_name} squad")
                return cached
        
        data = await self._fetch_thesportsdb(
            "lookup_all_players.php",
            {"id": team_id}
        )
        
        if data and data.get("player"):
            squad_data = {
                "source": "thesportsdb",
                "team_id": team_id,
                "team_name": team_name,
                "players": [
                    {
                        "id": p.get("idPlayer"),
                        "name": p.get("strPlayer"),
                        "position": p.get("strPosition"),
                        "nationality": p.get("strNationality"),
                        "birth_date": p.get("dateBorn"),
                        "height": p.get("strHeight"),
                        "weight": p.get("strWeight"),
                        "photo": p.get("strThumb"),
                        "description": p.get("strDescriptionEN"),
                    }
                    for p in data["player"]
                ],
                "total_players": len(data["player"]),
                "_downloaded_at": datetime.now().isoformat(),
            }
            
            await self._save_json(filepath, squad_data)
            return squad_data
        
        return None
    
    # =========================================================================
    # DESCARGA MASIVA
    # =========================================================================
    
    async def download_all_tier1_leagues(
        self, 
        api_key: Optional[str] = None,
        include_squads: bool = False
    ) -> Dict[str, Any]:
        """
        Descargar datos completos de todas las ligas Tier 1
        
        Returns:
            Resumen de la descarga con estadísticas
        """
        tier1_leagues = LeagueRegistry.get_leagues_by_tier(LeagueTier.TIER_1)
        
        results = {
            "started_at": datetime.now().isoformat(),
            "leagues_processed": 0,
            "leagues_failed": [],
            "total_teams": 0,
            "total_matches": 0,
        }
        
        logger.info(f"🚀 Iniciando descarga de {len(tier1_leagues)} ligas Tier 1...")
        
        for league in tier1_leagues:
            try:
                logger.info(f"📥 Descargando {league.name} ({league.code})...")
                
                # Descargar standings
                standings = await self.download_league_standings(league, api_key=api_key)
                
                # Descargar partidos
                matches = await self.download_league_matches(league)
                
                # Descargar equipos
                teams = await self.download_league_teams(league)
                
                # Descargar plantillas si se solicita
                if include_squads and teams:
                    for team in teams.get("teams", [])[:5]:  # Limitar a 5 por liga
                        await self.download_team_squad(team["id"], team["name"])
                        await asyncio.sleep(0.1)  # Rate limiting suave
                
                results["leagues_processed"] += 1
                if teams:
                    results["total_teams"] += teams.get("total_teams", 0)
                if matches:
                    results["total_matches"] += matches.get("total_matches", 0)
                    
            except Exception as e:
                logger.error(f"❌ Error descargando {league.code}: {e}")
                results["leagues_failed"].append({"code": league.code, "error": str(e)})
        
        results["finished_at"] = datetime.now().isoformat()
        results["duration_seconds"] = (
            datetime.fromisoformat(results["finished_at"]) - 
            datetime.fromisoformat(results["started_at"])
        ).total_seconds()
        
        # Guardar resumen
        await self._save_json(
            self.data_dir / "download_summary.json",
            results
        )
        
        logger.info(f"✅ Descarga completada: {results['leagues_processed']} ligas, "
                   f"{results['total_teams']} equipos, {results['total_matches']} partidos")
        
        return results
    
    async def download_specific_leagues(
        self,
        league_codes: List[str],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Descargar datos de ligas específicas por código"""
        results = {
            "requested": league_codes,
            "successful": [],
            "failed": [],
        }
        
        for code in league_codes:
            league = LeagueRegistry.get_league(code)
            if not league:
                results["failed"].append({"code": code, "error": "Liga no encontrada"})
                continue
            
            try:
                await self.download_league_standings(league, api_key=api_key)
                await self.download_league_matches(league)
                await self.download_league_teams(league)
                results["successful"].append(code)
            except Exception as e:
                results["failed"].append({"code": code, "error": str(e)})
        
        return results
    
    def get_local_data_summary(self) -> Dict[str, Any]:
        """Obtener resumen de datos almacenados localmente"""
        summary = {
            "leagues": {},
            "teams_with_squads": 0,
            "total_size_mb": 0,
        }
        
        # Escanear directorios de ligas
        if self.leagues_dir.exists():
            for league_dir in self.leagues_dir.iterdir():
                if league_dir.is_dir():
                    files = list(league_dir.glob("*.json"))
                    summary["leagues"][league_dir.name] = {
                        "files": [f.name for f in files],
                        "size_kb": sum(f.stat().st_size for f in files) / 1024,
                    }
        
        # Contar equipos con plantillas
        if self.teams_dir.exists():
            summary["teams_with_squads"] = len(list(self.teams_dir.glob("*_squad.json")))
        
        # Calcular tamaño total
        total_bytes = sum(
            f.stat().st_size 
            for f in self.data_dir.rglob("*.json")
        )
        summary["total_size_mb"] = round(total_bytes / (1024 * 1024), 2)
        
        return summary
