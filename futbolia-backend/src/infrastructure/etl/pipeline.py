"""
ETL Pipeline Module
Pipeline completo de Extract-Transform-Load para datos de fútbol
Orquesta todo el proceso de minería de datos
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from src.core.logger import get_logger
from src.core.config import settings
from src.infrastructure.datasets.league_registry import LeagueRegistry, LeagueInfo, LeagueTier, GLOBAL_LEAGUES
from src.infrastructure.etl.extractor import DataExtractor
from src.infrastructure.etl.transformer import DataTransformer, TransformationResult, DataQuality
from src.infrastructure.etl.loader import DataLoader

logger = get_logger(__name__)


@dataclass
class PipelineConfig:
    """Configuración del pipeline ETL"""
    football_data_key: str = ""
    api_football_key: str = ""
    data_dir: str = "./data/datasets"
    include_matches: bool = True
    include_teams: bool = True
    include_squads: bool = False
    parallel_extraction: bool = False
    save_to_mongodb: bool = True
    generate_ml_features: bool = True


@dataclass 
class PipelineResult:
    """Resultado de ejecución del pipeline"""
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    leagues_processed: int = 0
    leagues_failed: List[str] = field(default_factory=list)
    total_standings: int = 0
    total_matches: int = 0
    total_teams: int = 0
    data_quality: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": (self.finished_at - self.started_at).total_seconds() if self.finished_at else None,
            "leagues_processed": self.leagues_processed,
            "leagues_failed": self.leagues_failed,
            "total_standings": self.total_standings,
            "total_matches": self.total_matches,
            "total_teams": self.total_teams,
            "data_quality": self.data_quality,
            "errors": self.errors,
        }


class ETLPipeline:
    """
    Pipeline ETL completo para minería de datos de fútbol
    
    Flujo:
    1. EXTRACT: Obtener datos de APIs externas o archivos locales
    2. TRANSFORM: Limpiar, normalizar y crear features
    3. LOAD: Guardar en archivos, MongoDB y ChromaDB
    
    Características:
    - Soporta +50 ligas mundiales
    - Rate limiting automático
    - Fallback entre APIs
    - Detección de calidad de datos
    - Generación de features para ML
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig(
            football_data_key=settings.FOOTBALL_DATA_API_KEY
        )
        
        self.extractor = DataExtractor(
            football_data_key=self.config.football_data_key,
            api_football_key=self.config.api_football_key
        )
        
        self.transformer = DataTransformer()
        
        self.loader = DataLoader(
            data_dir=self.config.data_dir,
            mongodb_client=None,  # Se inyecta externamente si es necesario
            chromadb_client=None
        )
    
    def set_mongodb_client(self, client):
        """Inyectar cliente MongoDB"""
        self.loader.mongodb = client
    
    def set_chromadb_client(self, client):
        """Inyectar cliente ChromaDB"""
        self.loader.chromadb = client
    
    # =========================================================================
    # PIPELINE PARA UNA LIGA
    # =========================================================================
    
    async def process_league(
        self,
        league_code: str,
        season: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecutar pipeline completo para una liga
        
        Args:
            league_code: Código de la liga (ej: 'PL', 'ECU')
            season: Temporada específica (usa actual si None)
            
        Returns:
            Resultado detallado del procesamiento
        """
        league = LeagueRegistry.get_league(league_code)
        
        if not league:
            return {
                "success": False,
                "error": f"Liga no encontrada: {league_code}",
                "league_code": league_code
            }
        
        season = season or league.get_current_season()
        year = int(season.split('-')[0])
        
        result = {
            "league_code": league_code,
            "league_name": league.name,
            "season": season,
            "steps": {},
            "data_quality": {},
            "errors": [],
        }
        
        logger.info(f"🚀 Iniciando pipeline para {league.name} ({season})")
        
        # =====================================================================
        # PASO 1: EXTRACT
        # =====================================================================
        logger.info(f"📥 EXTRACT: Obteniendo datos de {league.name}...")
        
        extracted_data = {
            "standings": None,
            "matches": None,
            "teams": None,
        }
        
        # Extraer standings
        if league.thesportsdb_id:
            standings_raw = await self.extractor.extract_league_standings_thesportsdb(
                league.thesportsdb_id, year
            )
            if standings_raw:
                extracted_data["standings"] = standings_raw
                result["steps"]["extract_standings"] = "success"
            else:
                # Fallback a Football-Data
                if league.football_data_id:
                    standings_raw = await self.extractor.extract_league_standings_footballdata(
                        league.football_data_id
                    )
                    if standings_raw:
                        extracted_data["standings"] = standings_raw
                        result["steps"]["extract_standings"] = "success_fallback"
        
        # Extraer partidos
        if self.config.include_matches and league.thesportsdb_id:
            matches_raw = await self.extractor.extract_league_matches_thesportsdb(
                league.thesportsdb_id, year
            )
            if matches_raw:
                extracted_data["matches"] = matches_raw
                result["steps"]["extract_matches"] = "success"
        
        # Extraer equipos
        if self.config.include_teams and league.thesportsdb_id:
            teams_raw = await self.extractor.extract_league_teams_thesportsdb(
                league.thesportsdb_id
            )
            if teams_raw:
                extracted_data["teams"] = teams_raw
                result["steps"]["extract_teams"] = "success"
        
        # =====================================================================
        # PASO 2: TRANSFORM
        # =====================================================================
        logger.info(f"🔄 TRANSFORM: Limpiando y normalizando datos...")
        
        transformed_data = {
            "standings": None,
            "matches": None,
            "teams": None,
        }
        
        # Transformar standings
        if extracted_data["standings"]:
            source = extracted_data["standings"].get("source", "thesportsdb")
            raw_standings = extracted_data["standings"].get("raw_data", [])
            
            standings_result = DataTransformer.transform_standings(raw_standings, source)
            transformed_data["standings"] = standings_result
            result["data_quality"]["standings"] = standings_result.quality.value
            result["steps"]["transform_standings"] = "success"
            
            if standings_result.warnings:
                result["errors"].extend(standings_result.warnings[:5])  # Limitar warnings
        
        # Transformar partidos
        if extracted_data["matches"]:
            source = extracted_data["matches"].get("source", "thesportsdb")
            raw_matches = extracted_data["matches"].get("raw_data", [])
            
            matches_result = DataTransformer.transform_matches(raw_matches, source)
            transformed_data["matches"] = matches_result
            result["data_quality"]["matches"] = matches_result.quality.value
            result["steps"]["transform_matches"] = "success"
        
        # Transformar equipos
        if extracted_data["teams"]:
            source = extracted_data["teams"].get("source", "thesportsdb")
            raw_teams = extracted_data["teams"].get("raw_data", [])
            
            teams_result = DataTransformer.transform_teams(raw_teams, source)
            transformed_data["teams"] = teams_result
            result["data_quality"]["teams"] = teams_result.quality.value
            result["steps"]["transform_teams"] = "success"
        
        # =====================================================================
        # PASO 3: LOAD
        # =====================================================================
        logger.info(f"💾 LOAD: Guardando datos procesados...")
        
        load_result = await self.loader.load_league_data(
            league_code=league_code,
            season=season,
            standings_result=transformed_data["standings"],
            matches_result=transformed_data["matches"],
            teams_result=transformed_data["teams"]
        )
        
        result["steps"]["load"] = "success"
        result["load_summary"] = load_result
        
        # =====================================================================
        # PASO 4: GENERAR FEATURES ML (opcional)
        # =====================================================================
        if self.config.generate_ml_features and transformed_data["standings"]:
            logger.info(f"🧠 Generando features para ML...")
            
            standings_data = transformed_data["standings"].data
            
            # Crear features de predicción para cada par de equipos
            if len(standings_data) >= 2:
                ml_features = []
                teams_list = [entry.get("team", {}).get("name") for entry in standings_data]
                
                # Generar features para combinaciones de equipos
                for i, home in enumerate(teams_list[:10]):  # Limitar para demo
                    for j, away in enumerate(teams_list[:10]):
                        if i != j and home and away:
                            features = DataTransformer.create_prediction_features(
                                standings_data, home, away
                            )
                            if features:
                                features["home_team"] = home
                                features["away_team"] = away
                                ml_features.append(features)
                
                if ml_features:
                    await self.loader.load_ml_features(
                        league_code, ml_features, "prediction"
                    )
                    result["steps"]["generate_ml_features"] = "success"
                    result["ml_features_generated"] = len(ml_features)
        
        result["success"] = True
        logger.info(f"✅ Pipeline completado para {league.name}")
        
        return result
    
    # =========================================================================
    # PIPELINE BATCH
    # =========================================================================
    
    async def process_tier1_leagues(self) -> PipelineResult:
        """Procesar todas las ligas Tier 1"""
        tier1_leagues = LeagueRegistry.get_leagues_by_tier(LeagueTier.TIER_1)
        return await self.process_leagues([l.code for l in tier1_leagues])
    
    async def process_leagues(
        self,
        league_codes: List[str],
        parallel: bool = False
    ) -> PipelineResult:
        """
        Procesar múltiples ligas
        
        Args:
            league_codes: Lista de códigos de ligas
            parallel: Si True, procesa en paralelo (cuidado con rate limits)
        """
        result = PipelineResult()
        
        logger.info(f"🚀 Iniciando pipeline para {len(league_codes)} ligas...")
        
        if parallel:
            # Procesamiento paralelo (solo para fuentes sin rate limit severo)
            tasks = [self.process_league(code) for code in league_codes]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for code, res in zip(league_codes, results):
                if isinstance(res, Exception):
                    result.leagues_failed.append(code)
                    result.errors.append(f"{code}: {str(res)}")
                elif res.get("success"):
                    result.leagues_processed += 1
                    result.data_quality[code] = res.get("data_quality", {})
                else:
                    result.leagues_failed.append(code)
        else:
            # Procesamiento secuencial (más seguro)
            for code in league_codes:
                try:
                    res = await self.process_league(code)
                    
                    if res.get("success"):
                        result.leagues_processed += 1
                        result.data_quality[code] = res.get("data_quality", {})
                        
                        # Acumular totales
                        load_summary = res.get("load_summary", {})
                        if load_summary.get("standings"):
                            result.total_standings += 1
                        if load_summary.get("matches"):
                            match_result = load_summary.get("matches", {})
                            result.total_matches += match_result.get("matches_count", 0)
                        if load_summary.get("teams"):
                            team_result = load_summary.get("teams", {})
                            result.total_teams += team_result.get("teams_count", 0)
                    else:
                        result.leagues_failed.append(code)
                        result.errors.append(res.get("error", "Unknown error"))
                        
                except Exception as e:
                    result.leagues_failed.append(code)
                    result.errors.append(f"{code}: {str(e)}")
                    logger.error(f"❌ Error procesando {code}: {e}")
        
        result.finished_at = datetime.now()
        
        logger.info(f"✅ Pipeline batch completado: "
                   f"{result.leagues_processed}/{len(league_codes)} ligas procesadas")
        
        return result
    
    async def process_by_continent(self, continent: str) -> PipelineResult:
        """Procesar todas las ligas de un continente"""
        from src.infrastructure.datasets.league_registry import Continent
        
        continent_enum = Continent(continent.lower())
        leagues = LeagueRegistry.get_leagues_by_continent(continent_enum)
        
        return await self.process_leagues([l.code for l in leagues])
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    
    def get_available_leagues(self) -> Dict[str, List[Dict]]:
        """Obtener ligas disponibles agrupadas por tier"""
        result = {
            "tier_1": [],
            "tier_2": [],
            "tier_3": [],
        }
        
        for code, league in GLOBAL_LEAGUES.items():
            league_info = {
                "code": code,
                "name": league.name,
                "country": league.country,
                "has_thesportsdb": bool(league.thesportsdb_id),
                "has_football_data": bool(league.football_data_id),
            }
            
            tier_key = f"tier_{league.tier.value}"
            result[tier_key].append(league_info)
        
        return result
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del pipeline"""
        return {
            "config": {
                "data_dir": self.config.data_dir,
                "include_matches": self.config.include_matches,
                "include_teams": self.config.include_teams,
                "generate_ml_features": self.config.generate_ml_features,
            },
            "loader_stats": self.loader.get_load_stats(),
            "extractor_stats": self.extractor.get_extraction_stats(),
        }
    
    async def quick_update(self, league_code: str) -> Dict:
        """
        Actualización rápida de una liga (solo standings y próximos partidos)
        Útil para actualizaciones frecuentes sin recargar todo
        """
        league = LeagueRegistry.get_league(league_code)
        
        if not league or not league.thesportsdb_id:
            return {"success": False, "error": "Liga no soportada"}
        
        result = {"league_code": league_code, "updates": {}}
        
        # Solo extraer standings actuales
        standings = await self.extractor.extract_league_standings_thesportsdb(
            league.thesportsdb_id,
            int(league.get_current_season().split('-')[0])
        )
        
        if standings:
            transformed = DataTransformer.transform_standings(
                standings.get("raw_data", []),
                "thesportsdb"
            )
            await self.loader.load_standings(
                league_code,
                league.get_current_season(),
                transformed
            )
            result["updates"]["standings"] = True
        
        # Extraer próximos partidos
        next_matches = await self.extractor.extract_next_matches_thesportsdb(
            league.thesportsdb_id
        )
        
        if next_matches:
            transformed = DataTransformer.transform_matches(
                next_matches.get("raw_data", []),
                "thesportsdb"
            )
            result["updates"]["next_matches"] = transformed.rows_output
        
        result["success"] = True
        return result
