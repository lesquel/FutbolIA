"""
Metrics Tracker Module
Seguimiento persistente de métricas de predicciones a lo largo del tiempo
"""
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import aiofiles

from src.core.logger import get_logger
from src.infrastructure.metrics.prediction_metrics import PredictionMetrics, MetricsReport

logger = get_logger(__name__)


class MetricsTracker:
    """
    Tracker persistente de métricas de predicción
    
    Funcionalidades:
    - Registro de predicciones y resultados
    - Cálculo de métricas en tiempo real
    - Estadísticas por liga, modelo, período
    - Alertas de degradación de performance
    - Exportación de métricas históricas
    """
    
    def __init__(self, data_dir: str = "./data/metrics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.predictions_file = self.data_dir / "predictions_log.json"
        self.metrics_file = self.data_dir / "metrics_history.json"
        
        # Cache en memoria
        self._predictions_cache: List[Dict] = []
        self._daily_metrics: Dict[str, Dict] = {}
    
    async def _load_predictions(self) -> List[Dict]:
        """Cargar predicciones desde archivo"""
        if not self.predictions_file.exists():
            return []
        
        try:
            async with aiofiles.open(self.predictions_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content else []
        except Exception as e:
            logger.error(f"Error cargando predicciones: {e}")
            return []
    
    async def _save_predictions(self, predictions: List[Dict]):
        """Guardar predicciones a archivo"""
        try:
            async with aiofiles.open(self.predictions_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(predictions, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.error(f"Error guardando predicciones: {e}")
    
    async def log_prediction(
        self,
        prediction: Dict,
        home_team: str,
        away_team: str,
        league_code: str,
        match_date: str,
        model_name: str = "hybrid"
    ) -> Dict:
        """
        Registrar una nueva predicción
        
        Args:
            prediction: Resultado de predicción con probabilities y confidence
            home_team: Equipo local
            away_team: Equipo visitante
            league_code: Código de la liga
            match_date: Fecha del partido
            model_name: Nombre del modelo usado
            
        Returns:
            Registro de predicción creado
        """
        predictions = await self._load_predictions()
        
        record = {
            "id": f"{league_code}_{home_team}_{away_team}_{match_date}".replace(" ", "_"),
            "home_team": home_team,
            "away_team": away_team,
            "league_code": league_code,
            "match_date": match_date,
            "predicted_at": datetime.now().isoformat(),
            "model_name": model_name,
            "predicted_result": prediction.get("predicted_result", prediction.get("predicted")),
            "confidence": prediction.get("confidence", 0.5),
            "probabilities": prediction.get("probabilities", {}),
            "actual_result": None,  # Se llena cuando se verifica
            "is_correct": None,
            "verified_at": None,
        }
        
        predictions.append(record)
        await self._save_predictions(predictions)
        
        logger.info(f"📝 Predicción registrada: {home_team} vs {away_team}")
        return record
    
    async def verify_prediction(
        self,
        prediction_id: str,
        actual_result: str,
        actual_score: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Verificar resultado de una predicción
        
        Args:
            prediction_id: ID de la predicción
            actual_result: Resultado real (HOME_WIN, DRAW, AWAY_WIN)
            actual_score: Marcador real {"home": 2, "away": 1}
            
        Returns:
            Predicción actualizada o None si no se encuentra
        """
        predictions = await self._load_predictions()
        
        for pred in predictions:
            if pred["id"] == prediction_id:
                pred["actual_result"] = actual_result
                pred["actual_score"] = actual_score
                pred["is_correct"] = pred["predicted_result"] == actual_result
                pred["verified_at"] = datetime.now().isoformat()
                
                await self._save_predictions(predictions)
                
                status = "✅" if pred["is_correct"] else "❌"
                logger.info(f"{status} Predicción verificada: {prediction_id}")
                
                return pred
        
        return None
    
    async def batch_verify_from_results(
        self,
        results: List[Dict]
    ) -> Dict[str, Any]:
        """
        Verificar múltiples predicciones con resultados reales
        
        Args:
            results: Lista de resultados con formato:
                    [{"home_team": "...", "away_team": "...", "result": "HOME_WIN", "score": {...}}]
        
        Returns:
            Resumen de verificaciones
        """
        predictions = await self._load_predictions()
        
        verified = 0
        not_found = 0
        
        for result in results:
            home = result.get("home_team", "").lower()
            away = result.get("away_team", "").lower()
            
            for pred in predictions:
                if pred["actual_result"] is not None:
                    continue  # Ya verificada
                
                if home in pred["home_team"].lower() and away in pred["away_team"].lower():
                    pred["actual_result"] = result.get("result")
                    pred["actual_score"] = result.get("score")
                    pred["is_correct"] = pred["predicted_result"] == result.get("result")
                    pred["verified_at"] = datetime.now().isoformat()
                    verified += 1
                    break
            else:
                not_found += 1
        
        await self._save_predictions(predictions)
        
        return {
            "verified": verified,
            "not_found": not_found,
            "total_processed": len(results)
        }
    
    async def get_metrics_summary(
        self,
        league_code: Optional[str] = None,
        model_name: Optional[str] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Obtener resumen de métricas
        
        Args:
            league_code: Filtrar por liga
            model_name: Filtrar por modelo
            days_back: Días hacia atrás a considerar
            
        Returns:
            Resumen de métricas
        """
        predictions = await self._load_predictions()
        
        # Filtrar predicciones verificadas
        cutoff = datetime.now() - timedelta(days=days_back)
        
        filtered = []
        for pred in predictions:
            if pred.get("actual_result") is None:
                continue
            
            if league_code and pred.get("league_code") != league_code:
                continue
            
            if model_name and pred.get("model_name") != model_name:
                continue
            
            pred_date = datetime.fromisoformat(pred["predicted_at"])
            if pred_date < cutoff:
                continue
            
            filtered.append(pred)
        
        if not filtered:
            return {
                "status": "no_data",
                "message": "No hay predicciones verificadas en el período seleccionado",
                "filters": {
                    "league_code": league_code,
                    "model_name": model_name,
                    "days_back": days_back
                }
            }
        
        # Preparar datos para métricas
        preds_for_metrics = [
            {
                "predicted": p["predicted_result"],
                "confidence": p["confidence"],
                "probabilities": p["probabilities"],
            }
            for p in filtered
        ]
        
        actuals = [p["actual_result"] for p in filtered]
        
        # Calcular métricas
        report = PredictionMetrics.calculate_metrics(preds_for_metrics, actuals)
        
        # Estadísticas adicionales
        by_league = defaultdict(lambda: {"total": 0, "correct": 0})
        by_confidence = defaultdict(lambda: {"total": 0, "correct": 0})
        
        for pred in filtered:
            league = pred.get("league_code", "unknown")
            by_league[league]["total"] += 1
            if pred["is_correct"]:
                by_league[league]["correct"] += 1
            
            conf = pred.get("confidence", 0.5)
            conf_bin = "high" if conf > 0.7 else "medium" if conf > 0.5 else "low"
            by_confidence[conf_bin]["total"] += 1
            if pred["is_correct"]:
                by_confidence[conf_bin]["correct"] += 1
        
        return {
            "period": {
                "days_back": days_back,
                "start_date": cutoff.isoformat(),
                "end_date": datetime.now().isoformat(),
            },
            "summary": report.to_dict(),
            "by_league": {
                k: {
                    "accuracy": round(v["correct"] / v["total"] * 100, 1) if v["total"] > 0 else 0,
                    "total": v["total"]
                }
                for k, v in by_league.items()
            },
            "by_confidence": {
                k: {
                    "accuracy": round(v["correct"] / v["total"] * 100, 1) if v["total"] > 0 else 0,
                    "total": v["total"]
                }
                for k, v in by_confidence.items()
            },
            "filters": {
                "league_code": league_code,
                "model_name": model_name,
            }
        }
    
    async def get_pending_verifications(self) -> List[Dict]:
        """Obtener predicciones pendientes de verificación"""
        predictions = await self._load_predictions()
        
        pending = [
            {
                "id": p["id"],
                "home_team": p["home_team"],
                "away_team": p["away_team"],
                "league_code": p["league_code"],
                "match_date": p["match_date"],
                "predicted_result": p["predicted_result"],
                "confidence": p["confidence"],
            }
            for p in predictions
            if p.get("actual_result") is None
        ]
        
        # Ordenar por fecha de partido
        pending.sort(key=lambda x: x["match_date"])
        
        return pending
    
    async def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """
        Obtener ranking de modelos por accuracy
        
        Returns:
            Lista ordenada de modelos con sus métricas
        """
        predictions = await self._load_predictions()
        
        # Agrupar por modelo
        by_model = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for pred in predictions:
            if pred.get("actual_result") is None:
                continue
            
            model = pred.get("model_name", "unknown")
            by_model[model]["total"] += 1
            if pred["is_correct"]:
                by_model[model]["correct"] += 1
        
        # Calcular accuracy y ordenar
        leaderboard = [
            {
                "model_name": model,
                "accuracy": round(data["correct"] / data["total"] * 100, 1) if data["total"] > 0 else 0,
                "total_predictions": data["total"],
                "correct_predictions": data["correct"],
            }
            for model, data in by_model.items()
        ]
        
        leaderboard.sort(key=lambda x: x["accuracy"], reverse=True)
        
        return leaderboard[:top_n]
    
    async def check_performance_alerts(
        self,
        accuracy_threshold: float = 0.4,
        min_predictions: int = 10
    ) -> List[Dict]:
        """
        Verificar alertas de degradación de performance
        
        Args:
            accuracy_threshold: Umbral mínimo de accuracy
            min_predictions: Mínimo de predicciones para generar alerta
            
        Returns:
            Lista de alertas activas
        """
        predictions = await self._load_predictions()
        alerts = []
        
        # Agrupar por liga
        by_league = defaultdict(lambda: {"correct": 0, "total": 0})
        
        # Solo últimos 30 días
        cutoff = datetime.now() - timedelta(days=30)
        
        for pred in predictions:
            if pred.get("actual_result") is None:
                continue
            
            pred_date = datetime.fromisoformat(pred["predicted_at"])
            if pred_date < cutoff:
                continue
            
            league = pred.get("league_code", "unknown")
            by_league[league]["total"] += 1
            if pred["is_correct"]:
                by_league[league]["correct"] += 1
        
        # Verificar alertas
        for league, data in by_league.items():
            if data["total"] < min_predictions:
                continue
            
            accuracy = data["correct"] / data["total"]
            if accuracy < accuracy_threshold:
                alerts.append({
                    "type": "low_accuracy",
                    "severity": "warning" if accuracy > 0.3 else "critical",
                    "league_code": league,
                    "accuracy": round(accuracy * 100, 1),
                    "predictions_count": data["total"],
                    "message": f"Accuracy baja en {league}: {round(accuracy * 100, 1)}%",
                    "recommendation": "Considera reentrenar el modelo o revisar datos de entrada"
                })
        
        return alerts
    
    async def export_metrics_history(
        self,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exportar historial completo de métricas
        
        Returns:
            Datos exportados o ruta del archivo
        """
        predictions = await self._load_predictions()
        
        # Agrupar por día
        by_date = defaultdict(lambda: {"predictions": [], "actuals": []})
        
        for pred in predictions:
            if pred.get("actual_result") is None:
                continue
            
            date = pred.get("match_date", "unknown")
            by_date[date]["predictions"].append({
                "predicted": pred["predicted_result"],
                "confidence": pred["confidence"],
            })
            by_date[date]["actuals"].append(pred["actual_result"])
        
        # Calcular métricas por día
        daily_metrics = []
        
        for date, data in sorted(by_date.items()):
            if len(data["predictions"]) < 1:
                continue
            
            report = PredictionMetrics.calculate_metrics(
                data["predictions"],
                data["actuals"]
            )
            
            daily_metrics.append({
                "date": date,
                "total_predictions": report.total_predictions,
                "accuracy": round(report.accuracy * 100, 1),
            })
        
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "total_predictions": len(predictions),
            "verified_predictions": sum(1 for p in predictions if p.get("actual_result")),
            "daily_metrics": daily_metrics,
        }
        
        if output_path:
            path = Path(output_path)
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(export_data, ensure_ascii=False, indent=2))
            return {"status": "exported", "path": str(path)}
        
        return export_data
