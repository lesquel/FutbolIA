"""
Data Extractor Module
Fase EXTRACT del pipeline ETL
Extrae datos desde múltiples fuentes (APIs, archivos locales)
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import httpx

from src.core.logger import get_logger
from src.infrastructure.datasets.league_registry import LeagueRegistry, LeagueInfo, GLOBAL_LEAGUES

logger = get_logger(__name__)


class DataExtractor:
    """
    Extractor de datos desde múltiples fuentes
    
    Fuentes soportadas:
    - TheSportsDB (100k req/día, GRATUITA)
    - Football-Data.org (10 req/min, GRATUITA)
    - API-Football (100 req/día free tier)
    - Archivos locales JSON
    
    Estrategia de extracción:
    1. Verificar cache local primero
    2. Si cache expirado o no existe, extraer de API
    3. Priorizar APIs gratuitas
    4. Aplicar rate limiting automático
    """
    
    # API Base URLs
    THESPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"
    FOOTBALL_DATA_BASE = "https://api.football-data.org/v4"
    API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
    
    def __init__(self, football_data_key: str = "", api_football_key: str = ""):
        self.football_data_key = football_data_key
        self.api_football_key = api_football_key
        
        # Rate limiting state
        self._last_request: Dict[str, datetime] = {}
        self._request_counts: Dict[str, int] = {}
    
    async def _rate_limit(self, api_name: str) -> bool:
        """
        Aplicar rate limiting y verificar si se puede hacer request
        
        Returns:
            True si se puede hacer request, False si hay que esperar
        """
        limits = {
            "thesportsdb": {"delay": 0.01, "max_per_minute": 1000},
            "football_data": {"delay": 6.0, "max_per_minute": 10},
            "api_football": {"delay": 1.0, "max_per_minute": 30},
        }
        
        config = limits.get(api_name, {"delay": 1.0, "max_per_minute": 60})
        
        now = datetime.now()
        last = self._last_request.get(api_name)
        
        if last:
            elapsed = (now - last).total_seconds()
            if elapsed < config["delay"]:
                await asyncio.sleep(config["delay"] - elapsed)
        
        self._last_request[api_name] = datetime.now()
        return True
    
    async def _fetch(
        self,
        url: str,
        headers: Dict = None,
        params: Dict = None,
        timeout: float = 30.0
    ) -> Optional[Dict]:
        """Realizar HTTP GET request con manejo de errores"""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    url,
                    headers=headers or {},
                    params=params or {}
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    logger.warning(f"⚠️ Rate limit alcanzado: {url}")
                else:
                    logger.warning(f"⚠️ HTTP {response.status_code}: {url}")
                    
        except httpx.TimeoutException:
            logger.error(f"❌ Timeout: {url}")
        except Exception as e:
            logger.error(f"❌ Error fetching {url}: {e}")
        
        return None
    
    # =========================================================================
    # EXTRACCIÓN DESDE THESPORTSDB (GRATUITA - PRIORIDAD 1)
    # =========================================================================
    
    async def extract_league_standings_thesportsdb(
        self,
        league_id: str,
        season: int
    ) -> Optional[Dict]:
        """
        Extraer tabla de posiciones desde TheSportsDB
        
        Args:
            league_id: ID de la liga en TheSportsDB
            season: Año de la temporada (ej: 2025)
        """
        await self._rate_limit("thesportsdb")
        
        data = await self._fetch(
            f"{self.THESPORTSDB_BASE}/lookuptable.php",
            params={"l": league_id, "s": str(season)}
        )
        
        if data:
            return {
                "source": "thesportsdb",
                "league_id": league_id,
                "season": season,
                "raw_data": data.get("table", []),
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    async def extract_league_teams_thesportsdb(
        self,
        league_id: str
    ) -> Optional[Dict]:
        """Extraer equipos de una liga desde TheSportsDB"""
        await self._rate_limit("thesportsdb")
        
        data = await self._fetch(
            f"{self.THESPORTSDB_BASE}/lookup_all_teams.php",
            params={"id": league_id}
        )
        
        if data:
            return {
                "source": "thesportsdb",
                "league_id": league_id,
                "raw_data": data.get("teams", []),
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    async def extract_league_matches_thesportsdb(
        self,
        league_id: str,
        season: int
    ) -> Optional[Dict]:
        """Extraer partidos de una temporada desde TheSportsDB"""
        await self._rate_limit("thesportsdb")
        
        data = await self._fetch(
            f"{self.THESPORTSDB_BASE}/eventsseason.php",
            params={"id": league_id, "s": str(season)}
        )
        
        if data:
            return {
                "source": "thesportsdb",
                "league_id": league_id,
                "season": season,
                "raw_data": data.get("events", []),
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    async def extract_team_squad_thesportsdb(
        self,
        team_id: str
    ) -> Optional[Dict]:
        """Extraer plantilla de un equipo desde TheSportsDB"""
        await self._rate_limit("thesportsdb")
        
        data = await self._fetch(
            f"{self.THESPORTSDB_BASE}/lookup_all_players.php",
            params={"id": team_id}
        )
        
        if data:
            return {
                "source": "thesportsdb",
                "team_id": team_id,
                "raw_data": data.get("player", []),
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    async def extract_next_matches_thesportsdb(
        self,
        league_id: str
    ) -> Optional[Dict]:
        """Extraer próximos partidos de una liga"""
        await self._rate_limit("thesportsdb")
        
        data = await self._fetch(
            f"{self.THESPORTSDB_BASE}/eventsnextleague.php",
            params={"id": league_id}
        )
        
        if data:
            return {
                "source": "thesportsdb",
                "league_id": league_id,
                "raw_data": data.get("events", []),
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    async def extract_last_matches_thesportsdb(
        self,
        league_id: str
    ) -> Optional[Dict]:
        """Extraer últimos partidos de una liga"""
        await self._rate_limit("thesportsdb")
        
        data = await self._fetch(
            f"{self.THESPORTSDB_BASE}/eventspastleague.php",
            params={"id": league_id}
        )
        
        if data:
            return {
                "source": "thesportsdb",
                "league_id": league_id,
                "raw_data": data.get("events", []),
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    # =========================================================================
    # EXTRACCIÓN DESDE FOOTBALL-DATA.ORG (GRATUITA - PRIORIDAD 2)
    # =========================================================================
    
    async def extract_league_standings_footballdata(
        self,
        competition_code: str
    ) -> Optional[Dict]:
        """
        Extraer tabla de posiciones desde Football-Data.org
        
        Args:
            competition_code: Código de la competición (ej: 'PL', 'PD')
        """
        if not self.football_data_key:
            logger.warning("⚠️ Football-Data.org API key no configurada")
            return None
        
        await self._rate_limit("football_data")
        
        data = await self._fetch(
            f"{self.FOOTBALL_DATA_BASE}/competitions/{competition_code}/standings",
            headers={"X-Auth-Token": self.football_data_key}
        )
        
        if data:
            return {
                "source": "football_data",
                "competition_code": competition_code,
                "raw_data": data,
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    async def extract_league_matches_footballdata(
        self,
        competition_code: str,
        matchday: Optional[int] = None,
        status: Optional[str] = None  # 'SCHEDULED', 'FINISHED', 'IN_PLAY'
    ) -> Optional[Dict]:
        """Extraer partidos desde Football-Data.org"""
        if not self.football_data_key:
            return None
        
        await self._rate_limit("football_data")
        
        params = {}
        if matchday:
            params["matchday"] = matchday
        if status:
            params["status"] = status
        
        data = await self._fetch(
            f"{self.FOOTBALL_DATA_BASE}/competitions/{competition_code}/matches",
            headers={"X-Auth-Token": self.football_data_key},
            params=params
        )
        
        if data:
            return {
                "source": "football_data",
                "competition_code": competition_code,
                "raw_data": data,
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    async def extract_team_footballdata(
        self,
        team_id: int
    ) -> Optional[Dict]:
        """Extraer información de equipo desde Football-Data.org"""
        if not self.football_data_key:
            return None
        
        await self._rate_limit("football_data")
        
        data = await self._fetch(
            f"{self.FOOTBALL_DATA_BASE}/teams/{team_id}",
            headers={"X-Auth-Token": self.football_data_key}
        )
        
        if data:
            return {
                "source": "football_data",
                "team_id": team_id,
                "raw_data": data,
                "extracted_at": datetime.now().isoformat(),
            }
        
        return None
    
    # =========================================================================
    # EXTRACCIÓN MASIVA CON ESTRATEGIA DE FALLBACK
    # =========================================================================
    
    async def extract_league_data(
        self,
        league: LeagueInfo,
        include_matches: bool = True,
        include_teams: bool = True
    ) -> Dict[str, Any]:
        """
        Extraer todos los datos de una liga con fallback automático
        
        Estrategia:
        1. Intentar TheSportsDB primero (gratuita, sin límites severos)
        2. Si falla, intentar Football-Data.org
        3. Registrar fuente de cada dato
        """
        result = {
            "league_code": league.code,
            "league_name": league.name,
            "standings": None,
            "teams": None,
            "matches": None,
            "sources_used": [],
            "errors": [],
        }
        
        season = int(league.get_current_season().split('-')[0])
        
        # Extraer standings
        if league.thesportsdb_id:
            standings = await self.extract_league_standings_thesportsdb(
                league.thesportsdb_id, season
            )
            if standings:
                result["standings"] = standings
                result["sources_used"].append("thesportsdb")
        
        if not result["standings"] and league.football_data_id:
            standings = await self.extract_league_standings_footballdata(
                league.football_data_id
            )
            if standings:
                result["standings"] = standings
                result["sources_used"].append("football_data")
        
        # Extraer equipos
        if include_teams and league.thesportsdb_id:
            teams = await self.extract_league_teams_thesportsdb(league.thesportsdb_id)
            if teams:
                result["teams"] = teams
        
        # Extraer partidos
        if include_matches and league.thesportsdb_id:
            matches = await self.extract_league_matches_thesportsdb(
                league.thesportsdb_id, season
            )
            if matches:
                result["matches"] = matches
        
        return result
    
    async def extract_multiple_leagues(
        self,
        league_codes: List[str],
        parallel: bool = False
    ) -> Dict[str, Dict]:
        """
        Extraer datos de múltiples ligas
        
        Args:
            league_codes: Lista de códigos de ligas
            parallel: Si True, extrae en paralelo (cuidado con rate limits)
        """
        results = {}
        
        if parallel:
            # Extracción paralela (solo para TheSportsDB que permite alto volumen)
            tasks = []
            for code in league_codes:
                league = LeagueRegistry.get_league(code)
                if league:
                    tasks.append(self.extract_league_data(league))
            
            extracted = await asyncio.gather(*tasks, return_exceptions=True)
            
            for code, data in zip(league_codes, extracted):
                if isinstance(data, Exception):
                    results[code] = {"error": str(data)}
                else:
                    results[code] = data
        else:
            # Extracción secuencial (más segura para rate limits)
            for code in league_codes:
                league = LeagueRegistry.get_league(code)
                if league:
                    logger.info(f"📥 Extrayendo datos de {league.name}...")
                    results[code] = await self.extract_league_data(league)
                else:
                    results[code] = {"error": f"Liga no encontrada: {code}"}
        
        return results
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de extracción"""
        return {
            "last_requests": {
                api: time.isoformat() if time else None
                for api, time in self._last_request.items()
            },
            "apis_configured": {
                "thesportsdb": True,  # Siempre disponible
                "football_data": bool(self.football_data_key),
                "api_football": bool(self.api_football_key),
            }
        }
