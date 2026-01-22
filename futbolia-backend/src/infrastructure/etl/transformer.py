"""
Data Transformer Module
Fase TRANSFORM del pipeline ETL
Limpieza, normalización y transformación de datos
"""
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.core.logger import get_logger

logger = get_logger(__name__)


class DataQuality(Enum):
    """Niveles de calidad de datos"""
    HIGH = "high"          # >95% completitud, sin anomalías
    MEDIUM = "medium"      # 80-95% completitud, algunas anomalías
    LOW = "low"            # <80% completitud, muchas anomalías
    INVALID = "invalid"    # Datos no utilizables


@dataclass
class TransformationResult:
    """Resultado de una transformación"""
    data: Any
    quality: DataQuality
    rows_input: int
    rows_output: int
    rows_dropped: int
    nulls_filled: int
    outliers_detected: int
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "quality": self.quality.value,
            "rows_input": self.rows_input,
            "rows_output": self.rows_output,
            "rows_dropped": self.rows_dropped,
            "nulls_filled": self.nulls_filled,
            "outliers_detected": self.outliers_detected,
            "warnings": self.warnings,
        }


class DataTransformer:
    """
    Transformador de datos con técnicas de minería de datos
    
    Operaciones de transformación:
    1. Limpieza de datos (nulls, duplicados, inconsistencias)
    2. Normalización (StandardScaler, MinMaxScaler)
    3. Detección de outliers (IQR, Z-score)
    4. Imputación de valores faltantes
    5. Feature engineering
    6. Agregaciones y cálculos derivados
    """
    
    # =========================================================================
    # TRANSFORMACIÓN DE STANDINGS (TABLA DE POSICIONES)
    # =========================================================================
    
    @staticmethod
    def transform_standings(
        raw_data: List[Dict],
        source: str = "thesportsdb"
    ) -> TransformationResult:
        """
        Transformar datos raw de standings al formato estándar
        
        Incluye:
        - Normalización de campos
        - Cálculo de métricas derivadas
        - Detección de anomalías
        - Validación de integridad
        """
        warnings = []
        nulls_filled = 0
        outliers = 0
        
        if not raw_data:
            return TransformationResult(
                data=[],
                quality=DataQuality.INVALID,
                rows_input=0,
                rows_output=0,
                rows_dropped=0,
                nulls_filled=0,
                outliers_detected=0,
                warnings=["No hay datos para transformar"]
            )
        
        transformed = []
        
        for idx, entry in enumerate(raw_data):
            try:
                # Mapeo de campos según fuente
                if source == "thesportsdb":
                    record = DataTransformer._transform_thesportsdb_standing(entry, idx)
                elif source == "football_data":
                    record = DataTransformer._transform_footballdata_standing(entry, idx)
                else:
                    record = entry  # Pasar sin transformar
                
                # Validar campos requeridos
                required_fields = ["position", "team", "playedGames", "points"]
                missing = [f for f in required_fields if f not in record or record[f] is None]
                
                if missing:
                    warnings.append(f"Fila {idx}: campos faltantes {missing}")
                    continue
                
                # Imputar valores nulos
                numeric_defaults = {
                    "won": 0, "draw": 0, "lost": 0,
                    "goalsFor": 0, "goalsAgainst": 0, "goalDifference": 0
                }
                
                for field, default in numeric_defaults.items():
                    if record.get(field) is None:
                        record[field] = default
                        nulls_filled += 1
                
                # Calcular métricas derivadas
                played = max(record.get("playedGames", 1), 1)
                record["metrics"] = {
                    "points_per_game": round(record["points"] / played, 3),
                    "goals_per_game": round(record["goalsFor"] / played, 3),
                    "goals_against_per_game": round(record["goalsAgainst"] / played, 3),
                    "goal_diff_per_game": round(record["goalDifference"] / played, 3),
                    "win_rate": round(record["won"] / played * 100, 2),
                    "draw_rate": round(record["draw"] / played * 100, 2),
                    "loss_rate": round(record["lost"] / played * 100, 2),
                }
                
                # Detectar anomalías
                if record["points"] > played * 3:
                    warnings.append(f"Fila {idx}: puntos ({record['points']}) > máximo posible ({played * 3})")
                    outliers += 1
                
                if record["won"] + record["draw"] + record["lost"] != played:
                    diff = played - (record["won"] + record["draw"] + record["lost"])
                    warnings.append(f"Fila {idx}: W+D+L no coincide con partidos jugados (diff: {diff})")
                    # Intentar corregir
                    if diff > 0:
                        record["draw"] += diff
                        nulls_filled += 1
                
                transformed.append(record)
                
            except Exception as e:
                warnings.append(f"Fila {idx}: Error de transformación - {str(e)}")
        
        # Determinar calidad de datos
        completeness = len(transformed) / len(raw_data) if raw_data else 0
        
        if completeness >= 0.95 and outliers == 0:
            quality = DataQuality.HIGH
        elif completeness >= 0.80:
            quality = DataQuality.MEDIUM
        elif completeness >= 0.50:
            quality = DataQuality.LOW
        else:
            quality = DataQuality.INVALID
        
        return TransformationResult(
            data=transformed,
            quality=quality,
            rows_input=len(raw_data),
            rows_output=len(transformed),
            rows_dropped=len(raw_data) - len(transformed),
            nulls_filled=nulls_filled,
            outliers_detected=outliers,
            warnings=warnings
        )
    
    @staticmethod
    def _transform_thesportsdb_standing(entry: Dict, idx: int) -> Dict:
        """Transformar entrada de TheSportsDB al formato estándar"""
        return {
            "position": int(entry.get("intRank", idx + 1)),
            "team": {
                "id": entry.get("idTeam"),
                "name": entry.get("strTeam", "Unknown"),
                "logo": entry.get("strTeamBadge", ""),
            },
            "playedGames": int(entry.get("intPlayed", 0)),
            "won": int(entry.get("intWin", 0)),
            "draw": int(entry.get("intDraw", 0)),
            "lost": int(entry.get("intLoss", 0)),
            "points": int(entry.get("intPoints", 0)),
            "goalsFor": int(entry.get("intGoalsFor", 0)),
            "goalsAgainst": int(entry.get("intGoalsAgainst", 0)),
            "goalDifference": int(entry.get("intGoalDifference", 0)),
            "form": entry.get("strForm", ""),
        }
    
    @staticmethod
    def _transform_footballdata_standing(entry: Dict, idx: int) -> Dict:
        """Transformar entrada de Football-Data.org al formato estándar"""
        team_info = entry.get("team", {})
        return {
            "position": entry.get("position", idx + 1),
            "team": {
                "id": team_info.get("id"),
                "name": team_info.get("name", "Unknown"),
                "logo": team_info.get("crest", ""),
            },
            "playedGames": entry.get("playedGames", 0),
            "won": entry.get("won", 0),
            "draw": entry.get("draw", 0),
            "lost": entry.get("lost", 0),
            "points": entry.get("points", 0),
            "goalsFor": entry.get("goalsFor", 0),
            "goalsAgainst": entry.get("goalsAgainst", 0),
            "goalDifference": entry.get("goalDifference", 0),
            "form": entry.get("form", ""),
        }
    
    # =========================================================================
    # TRANSFORMACIÓN DE PARTIDOS
    # =========================================================================
    
    @staticmethod
    def transform_matches(
        raw_data: List[Dict],
        source: str = "thesportsdb"
    ) -> TransformationResult:
        """
        Transformar datos raw de partidos al formato estándar
        """
        warnings = []
        nulls_filled = 0
        
        if not raw_data:
            return TransformationResult(
                data=[],
                quality=DataQuality.INVALID,
                rows_input=0,
                rows_output=0,
                rows_dropped=0,
                nulls_filled=0,
                outliers_detected=0,
                warnings=["No hay datos para transformar"]
            )
        
        transformed = []
        
        for idx, entry in enumerate(raw_data):
            try:
                if source == "thesportsdb":
                    record = DataTransformer._transform_thesportsdb_match(entry)
                elif source == "football_data":
                    record = DataTransformer._transform_footballdata_match(entry)
                else:
                    record = entry
                
                # Validar campos básicos
                if not record.get("homeTeam") or not record.get("awayTeam"):
                    warnings.append(f"Partido {idx}: equipos faltantes")
                    continue
                
                # Normalizar fecha
                if record.get("date"):
                    try:
                        # Intentar parsear varios formatos
                        date_str = record["date"]
                        if "T" in date_str:
                            date_str = date_str.split("T")[0]
                        record["date"] = date_str
                        record["datetime_parsed"] = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        record["datetime_parsed"] = None
                
                # Determinar estado del partido
                score = record.get("score", {})
                if score.get("home") is not None and score.get("away") is not None:
                    record["status"] = "FINISHED"
                    
                    # Calcular resultado
                    home_goals = score["home"]
                    away_goals = score["away"]
                    
                    if home_goals > away_goals:
                        record["result"] = "HOME_WIN"
                    elif away_goals > home_goals:
                        record["result"] = "AWAY_WIN"
                    else:
                        record["result"] = "DRAW"
                    
                    record["total_goals"] = home_goals + away_goals
                else:
                    record["status"] = record.get("status", "SCHEDULED")
                    record["result"] = None
                    record["total_goals"] = None
                
                transformed.append(record)
                
            except Exception as e:
                warnings.append(f"Partido {idx}: Error - {str(e)}")
        
        completeness = len(transformed) / len(raw_data) if raw_data else 0
        quality = DataQuality.HIGH if completeness >= 0.95 else \
                  DataQuality.MEDIUM if completeness >= 0.80 else \
                  DataQuality.LOW if completeness >= 0.50 else DataQuality.INVALID
        
        return TransformationResult(
            data=transformed,
            quality=quality,
            rows_input=len(raw_data),
            rows_output=len(transformed),
            rows_dropped=len(raw_data) - len(transformed),
            nulls_filled=nulls_filled,
            outliers_detected=0,
            warnings=warnings
        )
    
    @staticmethod
    def _transform_thesportsdb_match(entry: Dict) -> Dict:
        """Transformar partido de TheSportsDB"""
        home_score = entry.get("intHomeScore")
        away_score = entry.get("intAwayScore")
        
        return {
            "id": entry.get("idEvent"),
            "date": entry.get("dateEvent"),
            "time": entry.get("strTime", "00:00"),
            "round": entry.get("intRound"),
            "homeTeam": {
                "id": entry.get("idHomeTeam"),
                "name": entry.get("strHomeTeam"),
                "logo": entry.get("strHomeTeamBadge"),
            },
            "awayTeam": {
                "id": entry.get("idAwayTeam"),
                "name": entry.get("strAwayTeam"),
                "logo": entry.get("strAwayTeamBadge"),
            },
            "score": {
                "home": int(home_score) if home_score is not None else None,
                "away": int(away_score) if away_score is not None else None,
            },
            "venue": entry.get("strVenue"),
            "status": "FINISHED" if home_score is not None else "SCHEDULED",
        }
    
    @staticmethod
    def _transform_footballdata_match(entry: Dict) -> Dict:
        """Transformar partido de Football-Data.org"""
        score = entry.get("score", {}).get("fullTime", {})
        home_team = entry.get("homeTeam", {})
        away_team = entry.get("awayTeam", {})
        
        return {
            "id": entry.get("id"),
            "date": entry.get("utcDate", "").split("T")[0] if entry.get("utcDate") else None,
            "time": entry.get("utcDate", "").split("T")[1][:5] if "T" in entry.get("utcDate", "") else "00:00",
            "round": entry.get("matchday"),
            "homeTeam": {
                "id": home_team.get("id"),
                "name": home_team.get("name"),
                "logo": home_team.get("crest"),
            },
            "awayTeam": {
                "id": away_team.get("id"),
                "name": away_team.get("name"),
                "logo": away_team.get("crest"),
            },
            "score": {
                "home": score.get("home"),
                "away": score.get("away"),
            },
            "venue": None,  # Football-Data no incluye venue en matches
            "status": entry.get("status", "SCHEDULED"),
        }
    
    # =========================================================================
    # TRANSFORMACIÓN DE EQUIPOS
    # =========================================================================
    
    @staticmethod
    def transform_teams(
        raw_data: List[Dict],
        source: str = "thesportsdb"
    ) -> TransformationResult:
        """Transformar datos de equipos"""
        warnings = []
        
        if not raw_data:
            return TransformationResult(
                data=[],
                quality=DataQuality.INVALID,
                rows_input=0,
                rows_output=0,
                rows_dropped=0,
                nulls_filled=0,
                outliers_detected=0,
                warnings=["No hay datos"]
            )
        
        transformed = []
        
        for entry in raw_data:
            if source == "thesportsdb":
                record = {
                    "id": entry.get("idTeam"),
                    "name": entry.get("strTeam"),
                    "short_name": entry.get("strTeamShort"),
                    "logo": entry.get("strTeamBadge"),
                    "country": entry.get("strCountry"),
                    "league": entry.get("strLeague"),
                    "stadium": entry.get("strStadium"),
                    "stadium_capacity": DataTransformer._safe_int(entry.get("intStadiumCapacity")),
                    "founded": DataTransformer._safe_int(entry.get("intFormedYear")),
                    "website": entry.get("strWebsite"),
                    "description": entry.get("strDescriptionEN"),
                }
            else:
                record = entry
            
            if record.get("name"):
                transformed.append(record)
            else:
                warnings.append(f"Equipo sin nombre: {entry.get('id', 'unknown')}")
        
        completeness = len(transformed) / len(raw_data) if raw_data else 0
        quality = DataQuality.HIGH if completeness >= 0.95 else DataQuality.MEDIUM
        
        return TransformationResult(
            data=transformed,
            quality=quality,
            rows_input=len(raw_data),
            rows_output=len(transformed),
            rows_dropped=len(raw_data) - len(transformed),
            nulls_filled=0,
            outliers_detected=0,
            warnings=warnings
        )
    
    @staticmethod
    def _safe_int(value) -> Optional[int]:
        """Convertir a int de forma segura"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    # =========================================================================
    # NORMALIZACIÓN Y FEATURE ENGINEERING
    # =========================================================================
    
    @staticmethod
    def normalize_features(
        data: List[Dict],
        features: List[str],
        method: str = "standard"  # 'standard', 'minmax', 'robust'
    ) -> Tuple[List[Dict], Dict[str, Dict]]:
        """
        Normalizar features numéricas para ML
        
        Args:
            data: Lista de diccionarios con datos
            features: Lista de nombres de features a normalizar
            method: Método de normalización
            
        Returns:
            Tuple con datos normalizados y estadísticas de normalización
        """
        if not data:
            return [], {}
        
        stats = {}
        
        for feature in features:
            values = [d.get(feature) for d in data if d.get(feature) is not None]
            
            if not values:
                continue
            
            values_array = np.array(values, dtype=float)
            
            if method == "standard":
                mean = np.mean(values_array)
                std = np.std(values_array)
                std = std if std > 0 else 1
                
                stats[feature] = {"mean": mean, "std": std, "method": "standard"}
                
                for d in data:
                    if d.get(feature) is not None:
                        d[f"{feature}_normalized"] = (d[feature] - mean) / std
                        
            elif method == "minmax":
                min_val = np.min(values_array)
                max_val = np.max(values_array)
                range_val = max_val - min_val if max_val != min_val else 1
                
                stats[feature] = {"min": min_val, "max": max_val, "method": "minmax"}
                
                for d in data:
                    if d.get(feature) is not None:
                        d[f"{feature}_normalized"] = (d[feature] - min_val) / range_val
                        
            elif method == "robust":
                median = np.median(values_array)
                q1 = np.percentile(values_array, 25)
                q3 = np.percentile(values_array, 75)
                iqr = q3 - q1 if q3 != q1 else 1
                
                stats[feature] = {"median": median, "iqr": iqr, "method": "robust"}
                
                for d in data:
                    if d.get(feature) is not None:
                        d[f"{feature}_normalized"] = (d[feature] - median) / iqr
        
        return data, stats
    
    @staticmethod
    def detect_outliers(
        data: List[Dict],
        features: List[str],
        method: str = "iqr",  # 'iqr', 'zscore'
        threshold: float = 1.5
    ) -> Tuple[List[Dict], List[int]]:
        """
        Detectar outliers en features numéricas
        
        Returns:
            Tuple con datos marcados y lista de índices con outliers
        """
        outlier_indices = []
        
        for feature in features:
            values = [d.get(feature) for d in data if d.get(feature) is not None]
            
            if not values:
                continue
            
            values_array = np.array(values, dtype=float)
            
            if method == "iqr":
                q1 = np.percentile(values_array, 25)
                q3 = np.percentile(values_array, 75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                
                for idx, d in enumerate(data):
                    val = d.get(feature)
                    if val is not None and (val < lower or val > upper):
                        d[f"{feature}_is_outlier"] = True
                        if idx not in outlier_indices:
                            outlier_indices.append(idx)
                    else:
                        d[f"{feature}_is_outlier"] = False
                        
            elif method == "zscore":
                mean = np.mean(values_array)
                std = np.std(values_array)
                
                for idx, d in enumerate(data):
                    val = d.get(feature)
                    if val is not None and std > 0:
                        zscore = abs((val - mean) / std)
                        d[f"{feature}_zscore"] = zscore
                        if zscore > threshold:
                            d[f"{feature}_is_outlier"] = True
                            if idx not in outlier_indices:
                                outlier_indices.append(idx)
                        else:
                            d[f"{feature}_is_outlier"] = False
        
        return data, outlier_indices
    
    @staticmethod
    def create_prediction_features(
        standings: List[Dict],
        home_team: str,
        away_team: str
    ) -> Optional[Dict]:
        """
        Crear features para modelo de predicción de partidos
        """
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
        
        metrics_home = home_data.get("metrics", {})
        metrics_away = away_data.get("metrics", {})
        
        return {
            # Features del equipo local
            "home_position": home_data.get("position", 0),
            "home_points": home_data.get("points", 0),
            "home_ppg": metrics_home.get("points_per_game", 0),
            "home_gpg": metrics_home.get("goals_per_game", 0),
            "home_gapg": metrics_home.get("goals_against_per_game", 0),
            "home_win_rate": metrics_home.get("win_rate", 0),
            "home_goal_diff": home_data.get("goalDifference", 0),
            
            # Features del equipo visitante
            "away_position": away_data.get("position", 0),
            "away_points": away_data.get("points", 0),
            "away_ppg": metrics_away.get("points_per_game", 0),
            "away_gpg": metrics_away.get("goals_per_game", 0),
            "away_gapg": metrics_away.get("goals_against_per_game", 0),
            "away_win_rate": metrics_away.get("win_rate", 0),
            "away_goal_diff": away_data.get("goalDifference", 0),
            
            # Features comparativas
            "position_diff": home_data.get("position", 0) - away_data.get("position", 0),
            "points_diff": home_data.get("points", 0) - away_data.get("points", 0),
            "goal_diff_diff": home_data.get("goalDifference", 0) - away_data.get("goalDifference", 0),
            "ppg_diff": metrics_home.get("points_per_game", 0) - metrics_away.get("points_per_game", 0),
            
            # Ventaja de local (feature binaria)
            "home_advantage": 1,
        }
