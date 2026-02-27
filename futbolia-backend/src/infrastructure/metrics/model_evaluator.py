"""
Model Evaluator Module
Evaluación completa de modelos de ML para predicción de fútbol
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np

from src.core.logger import get_logger
from src.infrastructure.metrics.prediction_metrics import MetricsReport, PredictionMetrics

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    """Resultado de evaluación de modelo"""

    model_name: str
    metrics_report: MetricsReport
    brier_score: float
    log_loss: float
    roc_auc: dict[str, float] | None
    feature_importance: dict[str, float] | None
    cross_validation_scores: list[float] | None
    evaluation_time: str

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "metrics": self.metrics_report.to_dict(),
            "brier_score": round(self.brier_score, 4),
            "log_loss": round(self.log_loss, 4),
            "roc_auc": self.roc_auc,
            "feature_importance": self.feature_importance,
            "cv_scores": {
                "mean": round(np.mean(self.cross_validation_scores), 4)
                if self.cross_validation_scores
                else None,
                "std": round(np.std(self.cross_validation_scores), 4)
                if self.cross_validation_scores
                else None,
            }
            if self.cross_validation_scores
            else None,
            "evaluation_time": self.evaluation_time,
        }


class ModelEvaluator:
    """
    Evaluador completo de modelos de predicción

    Funcionalidades:
    - Evaluación con múltiples métricas
    - Validación cruzada
    - Análisis de curva ROC
    - Análisis de calibración
    - Comparación de modelos
    - Análisis temporal (performance a lo largo del tiempo)
    """

    @staticmethod
    def evaluate_model(
        predictions: list[dict],
        actuals: list[str],
        model_name: str = "unknown",
        feature_importance: dict[str, float] | None = None,
        cv_scores: list[float] | None = None,
    ) -> EvaluationResult:
        """
        Evaluación completa de un modelo

        Args:
            predictions: Predicciones con probabilidades
            actuals: Resultados reales
            model_name: Nombre del modelo
            feature_importance: Importancia de features (si disponible)
            cv_scores: Scores de validación cruzada (si disponible)

        Returns:
            Resultado de evaluación completo
        """
        # Métricas básicas
        metrics_report = PredictionMetrics.calculate_metrics(predictions, actuals)

        # Brier Score
        brier = PredictionMetrics.calculate_brier_score(predictions, actuals)

        # Log Loss
        log_loss = ModelEvaluator._calculate_log_loss(predictions, actuals)

        # ROC AUC (por clase)
        roc_auc = ModelEvaluator._calculate_roc_auc(predictions, actuals)

        return EvaluationResult(
            model_name=model_name,
            metrics_report=metrics_report,
            brier_score=brier,
            log_loss=log_loss,
            roc_auc=roc_auc,
            feature_importance=feature_importance,
            cross_validation_scores=cv_scores,
            evaluation_time=datetime.now().isoformat(),
        )

    @staticmethod
    def _calculate_log_loss(
        predictions: list[dict], actuals: list[str], eps: float = 1e-15
    ) -> float:
        """
        Calcular Log Loss (Cross-Entropy Loss)

        Log Loss = -Σ(y_i * log(p_i))
        Menor es mejor
        """
        if not predictions:
            return float("inf")

        log_loss_sum = 0.0
        classes = PredictionMetrics.RESULT_CLASSES

        for pred, actual in zip(predictions, actuals, strict=False):
            probabilities = pred.get("probabilities", {})

            for cls in classes:
                prob = probabilities.get(cls, 1 / len(classes))
                prob = max(min(prob, 1 - eps), eps)  # Clip para evitar log(0)

                y = 1 if cls == actual else 0
                log_loss_sum -= y * np.log(prob)

        return log_loss_sum / len(predictions)

    @staticmethod
    def _calculate_roc_auc(predictions: list[dict], actuals: list[str]) -> dict[str, float]:
        """
        Calcular AUC-ROC aproximado por clase

        Usa ranking-based AUC para evitar dependencia de sklearn
        """
        classes = PredictionMetrics.RESULT_CLASSES
        auc_by_class = {}

        for target_class in classes:
            # Obtener probabilidades para esta clase
            probs = []
            labels = []

            for pred, actual in zip(predictions, actuals, strict=False):
                probabilities = pred.get("probabilities", {})
                prob = probabilities.get(target_class, 1 / len(classes))
                probs.append(prob)
                labels.append(1 if actual == target_class else 0)

            # Calcular AUC usando ranking
            auc = ModelEvaluator._wilcoxon_mann_whitney_auc(probs, labels)
            auc_by_class[target_class] = round(auc, 4)

        return auc_by_class

    @staticmethod
    def _wilcoxon_mann_whitney_auc(probs: list[float], labels: list[int]) -> float:
        """
        Calcular AUC usando estadístico de Wilcoxon-Mann-Whitney

        AUC = P(score(positive) > score(negative))
        """
        positives = [p for p, label in zip(probs, labels, strict=False) if label == 1]
        negatives = [p for p, label in zip(probs, labels, strict=False) if label == 0]

        if not positives or not negatives:
            return 0.5  # No hay información

        n_correct = 0
        n_total = len(positives) * len(negatives)

        for pos in positives:
            for neg in negatives:
                if pos > neg:
                    n_correct += 1
                elif pos == neg:
                    n_correct += 0.5

        return n_correct / n_total if n_total > 0 else 0.5

    @staticmethod
    def temporal_analysis(
        predictions: list[dict], actuals: list[str], dates: list[str], window_size: int = 10
    ) -> list[dict]:
        """
        Análisis temporal del performance del modelo

        Args:
            predictions: Predicciones
            actuals: Resultados reales
            dates: Fechas de los partidos
            window_size: Tamaño de ventana móvil

        Returns:
            Performance a lo largo del tiempo
        """
        # Ordenar por fecha
        sorted_data = sorted(zip(dates, predictions, actuals, strict=False), key=lambda x: x[0])

        temporal_metrics = []

        for i in range(window_size, len(sorted_data) + 1):
            window = sorted_data[i - window_size : i]
            window_dates, window_preds, window_actuals = zip(*window, strict=False)

            report = PredictionMetrics.calculate_metrics(list(window_preds), list(window_actuals))

            temporal_metrics.append(
                {
                    "end_date": window_dates[-1],
                    "start_date": window_dates[0],
                    "window_size": window_size,
                    "accuracy": round(report.accuracy, 4),
                    "predictions_count": report.total_predictions,
                }
            )

        return temporal_metrics

    @staticmethod
    def league_analysis(
        predictions: list[dict], actuals: list[str], leagues: list[str]
    ) -> dict[str, dict]:
        """
        Análisis de performance por liga

        Returns:
            Métricas desglosadas por liga
        """
        # Agrupar por liga
        league_data = {}

        for pred, actual, league in zip(predictions, actuals, leagues, strict=False):
            if league not in league_data:
                league_data[league] = {"predictions": [], "actuals": []}

            league_data[league]["predictions"].append(pred)
            league_data[league]["actuals"].append(actual)

        # Calcular métricas por liga
        results = {}

        for league, data in league_data.items():
            report = PredictionMetrics.calculate_metrics(data["predictions"], data["actuals"])

            results[league] = {
                "total_predictions": report.total_predictions,
                "accuracy": round(report.accuracy, 4),
                "f1_macro": round(np.mean(list(report.f1_by_class.values())), 4),
            }

        # Ordenar por accuracy
        results = dict(sorted(results.items(), key=lambda x: x[1]["accuracy"], reverse=True))

        return results

    @staticmethod
    def confidence_analysis(predictions: list[dict], actuals: list[str]) -> dict[str, Any]:
        """
        Análisis detallado de relación confianza-accuracy

        Returns:
            Análisis de cuándo el modelo es más/menos confiable
        """
        # Agrupar por nivel de confianza
        confidence_bins = {
            "very_low": {"range": (0, 0.4), "correct": 0, "total": 0},
            "low": {"range": (0.4, 0.55), "correct": 0, "total": 0},
            "medium": {"range": (0.55, 0.70), "correct": 0, "total": 0},
            "high": {"range": (0.70, 0.85), "correct": 0, "total": 0},
            "very_high": {"range": (0.85, 1.0), "correct": 0, "total": 0},
        }

        overconfident = 0  # Confianza alta pero incorrecta
        underconfident = 0  # Confianza baja pero correcta

        for pred, actual in zip(predictions, actuals, strict=False):
            confidence = pred.get("confidence", 0.5)
            predicted = pred.get("predicted", pred.get("predicted_result", ""))
            is_correct = predicted == actual

            # Asignar a bin
            for _bin_name, bin_data in confidence_bins.items():
                low, high = bin_data["range"]
                if low <= confidence < high:
                    bin_data["total"] += 1
                    if is_correct:
                        bin_data["correct"] += 1
                    break

            # Detectar sobre/sub confianza
            if confidence > 0.75 and not is_correct:
                overconfident += 1
            elif confidence < 0.5 and is_correct:
                underconfident += 1

        # Calcular accuracy por bin
        for bin_data in confidence_bins.values():
            if bin_data["total"] > 0:
                bin_data["accuracy"] = round(bin_data["correct"] / bin_data["total"], 4)
            else:
                bin_data["accuracy"] = None

        # Calcular calibración esperada vs real
        calibration_gap = ModelEvaluator._calculate_calibration_gap(predictions, actuals)

        return {
            "confidence_bins": {
                name: {
                    "accuracy": data["accuracy"],
                    "sample_size": data["total"],
                }
                for name, data in confidence_bins.items()
            },
            "overconfident_predictions": overconfident,
            "underconfident_predictions": underconfident,
            "calibration_gap": calibration_gap,
            "recommendations": ModelEvaluator._generate_recommendations(
                confidence_bins, calibration_gap
            ),
        }

    @staticmethod
    def _calculate_calibration_gap(predictions: list[dict], actuals: list[str]) -> float:
        """
        Calcular gap de calibración (ECE - Expected Calibration Error)
        """
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)

        total_gap = 0.0

        for i in range(n_bins):
            low, high = bin_boundaries[i], bin_boundaries[i + 1]

            # Predicciones en este bin
            bin_preds = []
            bin_correct = []

            for pred, actual in zip(predictions, actuals, strict=False):
                conf = pred.get("confidence", 0.5)
                if low <= conf < high:
                    bin_preds.append(conf)
                    predicted = pred.get("predicted", pred.get("predicted_result", ""))
                    bin_correct.append(1 if predicted == actual else 0)

            if bin_preds:
                avg_conf = np.mean(bin_preds)
                avg_acc = np.mean(bin_correct)
                total_gap += abs(avg_conf - avg_acc) * len(bin_preds)

        return round(total_gap / len(predictions), 4) if predictions else 0

    @staticmethod
    def _generate_recommendations(confidence_bins: dict, calibration_gap: float) -> list[str]:
        """Generar recomendaciones basadas en el análisis"""
        recommendations = []

        if calibration_gap > 0.15:
            recommendations.append(
                "El modelo tiene un gap de calibración alto. Considera recalibrar probabilidades."
            )

        high_conf = confidence_bins.get("very_high", {})
        if high_conf.get("total", 0) > 0 and high_conf.get("accuracy", 0) < 0.7:
            recommendations.append(
                "Predicciones de alta confianza tienen accuracy bajo. El modelo es sobreconfiado."
            )

        low_conf = confidence_bins.get("low", {})
        if low_conf.get("total", 0) > 0 and low_conf.get("accuracy", 0) > 0.6:
            recommendations.append(
                "Predicciones de baja confianza rinden bien. El modelo es subconfiado."
            )

        if not recommendations:
            recommendations.append(
                "El modelo parece bien calibrado. Continúa monitoreando métricas."
            )

        return recommendations
