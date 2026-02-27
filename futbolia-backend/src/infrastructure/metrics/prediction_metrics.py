"""
Prediction Metrics Module
Métricas para evaluar calidad de predicciones de partidos
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricsReport:
    """Reporte de métricas de predicción"""

    total_predictions: int = 0
    correct_predictions: int = 0
    accuracy: float = 0.0
    precision_by_class: dict[str, float] = field(default_factory=dict)
    recall_by_class: dict[str, float] = field(default_factory=dict)
    f1_by_class: dict[str, float] = field(default_factory=dict)
    confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)
    confidence_calibration: dict[str, float] = field(default_factory=dict)
    roi: float | None = None  # Return on Investment para apuestas
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "total_predictions": self.total_predictions,
            "correct_predictions": self.correct_predictions,
            "accuracy": round(self.accuracy * 100, 2),
            "precision_by_class": {
                k: round(v * 100, 2) for k, v in self.precision_by_class.items()
            },
            "recall_by_class": {k: round(v * 100, 2) for k, v in self.recall_by_class.items()},
            "f1_by_class": {k: round(v * 100, 2) for k, v in self.f1_by_class.items()},
            "confusion_matrix": self.confusion_matrix,
            "confidence_calibration": self.confidence_calibration,
            "roi": round(self.roi * 100, 2) if self.roi else None,
            "generated_at": self.generated_at,
        }


class PredictionMetrics:
    """
    Calculador de métricas de predicción

    Métricas calculadas:
    - Accuracy (precisión global)
    - Precision por clase (HOME_WIN, DRAW, AWAY_WIN)
    - Recall por clase
    - F1-Score por clase
    - Matriz de confusión
    - Calibración de confianza
    - Brier Score (para probabilidades)
    - ROI (Return on Investment)
    """

    RESULT_CLASSES = ["HOME_WIN", "DRAW", "AWAY_WIN"]

    @staticmethod
    def calculate_metrics(predictions: list[dict], actuals: list[str]) -> MetricsReport:
        """
        Calcular todas las métricas de predicción

        Args:
            predictions: Lista de predicciones con formato:
                        {"predicted": "HOME_WIN", "confidence": 0.75, "probabilities": {...}}
            actuals: Lista de resultados reales ("HOME_WIN", "DRAW", "AWAY_WIN")

        Returns:
            Reporte completo de métricas
        """
        if len(predictions) != len(actuals):
            raise ValueError("predictions y actuals deben tener la misma longitud")

        if len(predictions) == 0:
            return MetricsReport()

        report = MetricsReport()
        report.total_predictions = len(predictions)

        # Contadores para métricas
        true_positives = defaultdict(int)
        false_positives = defaultdict(int)
        false_negatives = defaultdict(int)

        # Matriz de confusión
        confusion = {
            cls: {c: 0 for c in PredictionMetrics.RESULT_CLASSES}
            for cls in PredictionMetrics.RESULT_CLASSES
        }

        # Calcular métricas base
        correct = 0

        for pred, actual in zip(predictions, actuals, strict=False):
            predicted = pred.get("predicted", pred.get("predicted_result", ""))

            if predicted == actual:
                correct += 1
                true_positives[actual] += 1
            else:
                false_positives[predicted] += 1
                false_negatives[actual] += 1

            # Actualizar matriz de confusión
            if actual in confusion and predicted in confusion[actual]:
                confusion[actual][predicted] += 1

        report.correct_predictions = correct
        report.accuracy = correct / len(predictions) if predictions else 0
        report.confusion_matrix = confusion

        # Calcular Precision, Recall, F1 por clase
        for cls in PredictionMetrics.RESULT_CLASSES:
            tp = true_positives[cls]
            fp = false_positives[cls]
            fn = false_negatives[cls]

            # Precision = TP / (TP + FP)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            report.precision_by_class[cls] = precision

            # Recall = TP / (TP + FN)
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            report.recall_by_class[cls] = recall

            # F1 = 2 * (Precision * Recall) / (Precision + Recall)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            report.f1_by_class[cls] = f1

        # Calcular calibración de confianza
        report.confidence_calibration = PredictionMetrics._calculate_calibration(
            predictions, actuals
        )

        return report

    @staticmethod
    def _calculate_calibration(predictions: list[dict], actuals: list[str]) -> dict[str, float]:
        """
        Calcular calibración de confianza
        Agrupa predicciones por nivel de confianza y calcula accuracy real
        """
        bins = {
            "0-50%": {"correct": 0, "total": 0},
            "50-70%": {"correct": 0, "total": 0},
            "70-85%": {"correct": 0, "total": 0},
            "85-100%": {"correct": 0, "total": 0},
        }

        for pred, actual in zip(predictions, actuals, strict=False):
            confidence = pred.get("confidence", 0.5)
            predicted = pred.get("predicted", pred.get("predicted_result", ""))

            # Determinar bin
            if confidence < 0.5:
                bin_key = "0-50%"
            elif confidence < 0.7:
                bin_key = "50-70%"
            elif confidence < 0.85:
                bin_key = "70-85%"
            else:
                bin_key = "85-100%"

            bins[bin_key]["total"] += 1
            if predicted == actual:
                bins[bin_key]["correct"] += 1

        return {
            k: round(v["correct"] / v["total"], 4) if v["total"] > 0 else 0 for k, v in bins.items()
        }

    @staticmethod
    def calculate_brier_score(predictions: list[dict], actuals: list[str]) -> float:
        """
        Calcular Brier Score para evaluar calidad de probabilidades

        Brier Score = (1/N) * Σ(p_i - o_i)²
        Donde p_i es la probabilidad predicha y o_i es el resultado (0 o 1)

        Menor es mejor. 0 = perfecto, 0.25 = aleatorio para 50/50
        """
        if not predictions:
            return 1.0

        brier_sum = 0.0

        for pred, actual in zip(predictions, actuals, strict=False):
            probabilities = pred.get("probabilities", {})

            for cls in PredictionMetrics.RESULT_CLASSES:
                prob = probabilities.get(cls, 1 / 3)  # Default uniforme
                outcome = 1 if cls == actual else 0
                brier_sum += (prob - outcome) ** 2

        # Normalizar por número de predicciones y clases
        return brier_sum / (len(predictions) * len(PredictionMetrics.RESULT_CLASSES))

    @staticmethod
    def calculate_roi(
        predictions: list[dict],
        actuals: list[str],
        odds: list[dict] | None = None,
        stake: float = 1.0,
    ) -> dict[str, float]:
        """
        Calcular ROI (Return on Investment) si hubiera apuestas

        Args:
            predictions: Predicciones realizadas
            actuals: Resultados reales
            odds: Cuotas de apuesta [{"home": 2.1, "draw": 3.2, "away": 3.5}, ...]
            stake: Cantidad apostada por partido

        Returns:
            ROI por tipo de apuesta y total
        """
        if not odds or len(odds) != len(predictions):
            # Usar odds promedio si no se proporcionan
            odds = [{"HOME_WIN": 2.0, "DRAW": 3.3, "AWAY_WIN": 3.5}] * len(predictions)

        total_staked = 0.0
        total_return = 0.0

        roi_by_class = {
            cls: {"staked": 0, "returned": 0} for cls in PredictionMetrics.RESULT_CLASSES
        }

        for pred, actual, match_odds in zip(predictions, actuals, odds, strict=False):
            predicted = pred.get("predicted", pred.get("predicted_result", ""))
            confidence = pred.get("confidence", 0.5)

            # Solo apostar si confianza > 60%
            if confidence < 0.6:
                continue

            bet_amount = stake
            total_staked += bet_amount
            roi_by_class[predicted]["staked"] += bet_amount

            if predicted == actual:
                # Ganó la apuesta
                odd = match_odds.get(predicted, 2.0)
                winnings = bet_amount * odd
                total_return += winnings
                roi_by_class[predicted]["returned"] += winnings

        overall_roi = (total_return - total_staked) / total_staked if total_staked > 0 else 0

        return {
            "overall_roi": round(overall_roi, 4),
            "total_staked": total_staked,
            "total_return": round(total_return, 2),
            "profit": round(total_return - total_staked, 2),
            "roi_by_class": {
                cls: round((v["returned"] - v["staked"]) / v["staked"], 4) if v["staked"] > 0 else 0
                for cls, v in roi_by_class.items()
            },
        }

    @staticmethod
    def compare_models(model_results: dict[str, tuple[list[dict], list[str]]]) -> dict[str, Any]:
        """
        Comparar múltiples modelos de predicción

        Args:
            model_results: Dict con {nombre_modelo: (predicciones, actuals)}

        Returns:
            Comparación de métricas entre modelos
        """
        comparison = {
            "models": {},
            "best_by_metric": {},
        }

        for model_name, (predictions, actuals) in model_results.items():
            report = PredictionMetrics.calculate_metrics(predictions, actuals)
            brier = PredictionMetrics.calculate_brier_score(predictions, actuals)

            comparison["models"][model_name] = {
                "accuracy": report.accuracy,
                "f1_macro": np.mean(list(report.f1_by_class.values())),
                "brier_score": brier,
                "total_predictions": report.total_predictions,
            }

        # Determinar mejor modelo por cada métrica
        if comparison["models"]:
            comparison["best_by_metric"]["accuracy"] = max(
                comparison["models"].items(), key=lambda x: x[1]["accuracy"]
            )[0]

            comparison["best_by_metric"]["f1_macro"] = max(
                comparison["models"].items(), key=lambda x: x[1]["f1_macro"]
            )[0]

            comparison["best_by_metric"]["brier_score"] = min(
                comparison["models"].items(), key=lambda x: x[1]["brier_score"]
            )[0]

        return comparison
