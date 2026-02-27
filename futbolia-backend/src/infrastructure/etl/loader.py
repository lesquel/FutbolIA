"""
Data Loader Module
Fase LOAD del pipeline ETL
Carga de datos transformados a destinos (archivos, MongoDB, ChromaDB)
"""
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiofiles

from src.core.logger import get_logger
from src.infrastructure.etl.transformer import TransformationResult, DataQuality

logger = get_logger(__name__)


class DataLoader:
    """
    Cargador de datos a múltiples destinos
    
    Destinos soportados:
    1. Sistema de archivos (JSON) - Acceso ultrarrápido
    2. MongoDB - Persistencia y consultas complejas
    3. ChromaDB - Embeddings vectoriales para RAG
    
    Estrategia de carga:
    - Siempre guardar en archivos locales (backup)
    - Cargar a MongoDB para consultas de API
    - Generar embeddings para ChromaDB bajo demanda
    """
    
    def __init__(
        self,
        data_dir: str = "./data/datasets",
        mongodb_client: Optional[Any] = None,
        chromadb_client: Optional[Any] = None
    ):
        self.data_dir = Path(data_dir)
        self.leagues_dir = self.data_dir / "leagues"
        self.teams_dir = self.data_dir / "teams"
        self.processed_dir = self.data_dir / "processed"
        
        self.mongodb = mongodb_client
        self.chromadb = chromadb_client
        
        # Crear directorios
        for dir_path in [self.leagues_dir, self.teams_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Estadísticas de carga
        self._load_stats = {
            "files_written": 0,
            "mongodb_docs": 0,
            "chromadb_embeddings": 0,
            "errors": [],
        }
    
    async def _save_json(self, filepath: Path, data: Any, metadata: Dict = None):
        """Guardar datos JSON con metadatos"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Agregar metadatos
        output = {
            "_metadata": {
                "loaded_at": datetime.now().isoformat(),
                "version": "1.0",
                **(metadata or {})
            },
            "data": data
        }
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(output, ensure_ascii=False, indent=2))
        
        self._load_stats["files_written"] += 1
        logger.info(f"✅ Archivo guardado: {filepath}")
    
    # =========================================================================
    # CARGA DE STANDINGS
    # =========================================================================
    
    async def load_standings(
        self,
        league_code: str,
        season: str,
        result: TransformationResult,
        to_mongodb: bool = True
    ) -> Dict[str, Any]:
        """
        Cargar standings transformados
        
        Args:
            league_code: Código de la liga
            season: Temporada (ej: '2025-2026')
            result: Resultado de la transformación
            to_mongodb: Si cargar también a MongoDB
            
        Returns:
            Resumen de la carga
        """
        load_result = {
            "league_code": league_code,
            "season": season,
            "file_saved": False,
            "mongodb_saved": False,
            "quality": result.quality.value,
        }
        
        # Guardar en archivo local
        filepath = self.leagues_dir / league_code / f"standings_{season.replace('-', '_')}.json"
        
        try:
            await self._save_json(
                filepath,
                result.data,
                metadata={
                    "league_code": league_code,
                    "season": season,
                    "quality": result.quality.value,
                    "rows": result.rows_output,
                    "transformation_stats": result.to_dict()
                }
            )
            load_result["file_saved"] = True
        except Exception as e:
            logger.error(f"❌ Error guardando standings: {e}")
            self._load_stats["errors"].append(str(e))
        
        # Cargar a MongoDB
        if to_mongodb and self.mongodb:
            try:
                collection = self.mongodb.standings
                
                # Upsert por liga y temporada
                await collection.update_one(
                    {"league_code": league_code, "season": season},
                    {
                        "$set": {
                            "league_code": league_code,
                            "season": season,
                            "standings": result.data,
                            "quality": result.quality.value,
                            "updated_at": datetime.now(),
                        }
                    },
                    upsert=True
                )
                
                load_result["mongodb_saved"] = True
                self._load_stats["mongodb_docs"] += 1
                
            except Exception as e:
                logger.error(f"❌ Error MongoDB standings: {e}")
        
        return load_result
    
    # =========================================================================
    # CARGA DE PARTIDOS
    # =========================================================================
    
    async def load_matches(
        self,
        league_code: str,
        season: str,
        result: TransformationResult,
        to_mongodb: bool = True
    ) -> Dict[str, Any]:
        """Cargar partidos transformados"""
        load_result = {
            "league_code": league_code,
            "season": season,
            "file_saved": False,
            "mongodb_saved": False,
            "matches_count": result.rows_output,
        }
        
        # Guardar en archivo local
        filepath = self.leagues_dir / league_code / f"matches_{season.replace('-', '_')}.json"
        
        try:
            await self._save_json(
                filepath,
                result.data,
                metadata={
                    "league_code": league_code,
                    "season": season,
                    "total_matches": result.rows_output,
                    "transformation_stats": result.to_dict()
                }
            )
            load_result["file_saved"] = True
        except Exception as e:
            logger.error(f"❌ Error guardando matches: {e}")
        
        # Cargar a MongoDB
        if to_mongodb and self.mongodb:
            try:
                collection = self.mongodb.matches
                
                # Guardar partidos individuales
                for match in result.data:
                    await collection.update_one(
                        {"id": match.get("id"), "league_code": league_code},
                        {
                            "$set": {
                                **match,
                                "league_code": league_code,
                                "season": season,
                                "updated_at": datetime.now(),
                            }
                        },
                        upsert=True
                    )
                
                load_result["mongodb_saved"] = True
                self._load_stats["mongodb_docs"] += result.rows_output
                
            except Exception as e:
                logger.error(f"❌ Error MongoDB matches: {e}")
        
        return load_result
    
    # =========================================================================
    # CARGA DE EQUIPOS
    # =========================================================================
    
    async def load_teams(
        self,
        league_code: str,
        result: TransformationResult,
        to_mongodb: bool = True,
        to_chromadb: bool = False
    ) -> Dict[str, Any]:
        """Cargar equipos transformados"""
        load_result = {
            "league_code": league_code,
            "file_saved": False,
            "mongodb_saved": False,
            "chromadb_saved": False,
            "teams_count": result.rows_output,
        }
        
        # Guardar en archivo local
        filepath = self.leagues_dir / league_code / "teams.json"
        
        try:
            await self._save_json(
                filepath,
                result.data,
                metadata={
                    "league_code": league_code,
                    "total_teams": result.rows_output,
                    "transformation_stats": result.to_dict()
                }
            )
            load_result["file_saved"] = True
        except Exception as e:
            logger.error(f"❌ Error guardando teams: {e}")
        
        # Cargar a MongoDB
        if to_mongodb and self.mongodb:
            try:
                collection = self.mongodb.teams
                
                for team in result.data:
                    await collection.update_one(
                        {"id": team.get("id")},
                        {
                            "$set": {
                                **team,
                                "league_code": league_code,
                                "updated_at": datetime.now(),
                            }
                        },
                        upsert=True
                    )
                
                load_result["mongodb_saved"] = True
                self._load_stats["mongodb_docs"] += result.rows_output
                
            except Exception as e:
                logger.error(f"❌ Error MongoDB teams: {e}")
        
        # Cargar a ChromaDB para búsqueda semántica
        if to_chromadb and self.chromadb:
            try:
                for team in result.data:
                    # Crear documento para embedding
                    doc_text = f"{team.get('name', '')} {team.get('country', '')} {team.get('description', '')}"
                    
                    self.chromadb.add_or_update(
                        documents=[doc_text],
                        metadatas=[{
                            "team_id": team.get("id"),
                            "team_name": team.get("name"),
                            "league_code": league_code,
                            "type": "team"
                        }],
                        ids=[f"team_{team.get('id')}"]
                    )
                
                load_result["chromadb_saved"] = True
                self._load_stats["chromadb_embeddings"] += result.rows_output
                
            except Exception as e:
                logger.error(f"❌ Error ChromaDB teams: {e}")
        
        return load_result
    
    # =========================================================================
    # CARGA DE DATOS PARA ML
    # =========================================================================
    
    async def load_ml_features(
        self,
        league_code: str,
        features: List[Dict],
        feature_type: str = "prediction"
    ) -> Dict[str, Any]:
        """
        Cargar features procesados para entrenamiento ML
        
        Args:
            league_code: Código de la liga
            features: Lista de features por partido/equipo
            feature_type: Tipo de features ('prediction', 'clustering')
        """
        filepath = self.processed_dir / league_code / f"{feature_type}_features.json"
        
        try:
            await self._save_json(
                filepath,
                features,
                metadata={
                    "league_code": league_code,
                    "feature_type": feature_type,
                    "feature_count": len(features),
                }
            )
            
            return {
                "success": True,
                "filepath": str(filepath),
                "features_saved": len(features)
            }
            
        except Exception as e:
            logger.error(f"❌ Error guardando ML features: {e}")
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # CARGA BATCH
    # =========================================================================
    
    async def load_league_data(
        self,
        league_code: str,
        season: str,
        standings_result: Optional[TransformationResult] = None,
        matches_result: Optional[TransformationResult] = None,
        teams_result: Optional[TransformationResult] = None
    ) -> Dict[str, Any]:
        """
        Cargar todos los datos de una liga en batch
        """
        batch_result = {
            "league_code": league_code,
            "season": season,
            "standings": None,
            "matches": None,
            "teams": None,
            "total_files": 0,
            "total_mongodb_docs": 0,
        }
        
        if standings_result:
            batch_result["standings"] = await self.load_standings(
                league_code, season, standings_result
            )
            if batch_result["standings"]["file_saved"]:
                batch_result["total_files"] += 1
        
        if matches_result:
            batch_result["matches"] = await self.load_matches(
                league_code, season, matches_result
            )
            if batch_result["matches"]["file_saved"]:
                batch_result["total_files"] += 1
        
        if teams_result:
            batch_result["teams"] = await self.load_teams(league_code, teams_result)
            if batch_result["teams"]["file_saved"]:
                batch_result["total_files"] += 1
        
        return batch_result
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    
    def get_load_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de carga"""
        return {
            **self._load_stats,
            "data_dir": str(self.data_dir),
            "leagues_available": [
                d.name for d in self.leagues_dir.iterdir()
                if d.is_dir()
            ] if self.leagues_dir.exists() else []
        }
    
    def reset_stats(self):
        """Reiniciar estadísticas"""
        self._load_stats = {
            "files_written": 0,
            "mongodb_docs": 0,
            "chromadb_embeddings": 0,
            "errors": [],
        }
    
    async def verify_data_integrity(self, league_code: str) -> Dict[str, Any]:
        """Verificar integridad de datos cargados para una liga"""
        league_dir = self.leagues_dir / league_code
        
        if not league_dir.exists():
            return {"status": "not_found", "league_code": league_code}
        
        files = list(league_dir.glob("*.json"))
        
        integrity_report = {
            "league_code": league_code,
            "files_found": len(files),
            "files_status": {},
        }
        
        for filepath in files:
            try:
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    integrity_report["files_status"][filepath.name] = {
                        "valid_json": True,
                        "has_metadata": "_metadata" in data,
                        "has_data": "data" in data,
                        "records_count": len(data.get("data", [])) if isinstance(data.get("data"), list) else 1,
                    }
            except json.JSONDecodeError:
                integrity_report["files_status"][filepath.name] = {
                    "valid_json": False,
                    "error": "Invalid JSON"
                }
            except Exception as e:
                integrity_report["files_status"][filepath.name] = {
                    "valid_json": False,
                    "error": str(e)
                }
        
        return integrity_report
