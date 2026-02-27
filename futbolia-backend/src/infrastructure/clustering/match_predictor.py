"""
Match Prediction ML Module
Modelos de Machine Learning para predicción de resultados de partidos
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from src.core.logger import get_logger

logger = get_logger(__name__)


# Intentar importar sklearn, usar fallback si no está disponible
try:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, confusion_matrix
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("⚠️ sklearn no disponible. Usando predicciones heurísticas.")


class MatchResult(Enum):
    """Posibles resultados de un partido"""

    HOME_WIN = "HOME_WIN"
    DRAW = "DRAW"
    AWAY_WIN = "AWAY_WIN"


@dataclass
class PredictionOutput:
    """Resultado de una predicción"""

    predicted_result: MatchResult
    probabilities: dict[str, float]
    confidence: float
    features_used: list[str]
    model_name: str

    def to_dict(self) -> dict:
        return {
            "predicted_result": self.predicted_result.value,
            "probabilities": self.probabilities,
            "confidence": round(self.confidence * 100, 1),
            "features_used": self.features_used,
            "model_name": self.model_name,
        }


class MatchPredictor:
    """
    Predictor de resultados de partidos usando ML

    Modelos disponibles:
    - Random Forest (default): Robusto, buen balance
    - Gradient Boosting: Mayor precisión, más lento
    - Logistic Regression: Rápido, interpretable
    - Heurístico: Basado en reglas (fallback sin sklearn)

    Features utilizadas:
    - Posición en tabla
    - Puntos por partido
    - Diferencia de goles
    - Forma reciente
    - Ventaja de local
    """

    FEATURE_NAMES = [
        "home_position",
        "home_points",
        "home_ppg",
        "home_goal_diff",
        "home_win_rate",
        "home_form_rating",
        "away_position",
        "away_points",
        "away_ppg",
        "away_goal_diff",
        "away_win_rate",
        "away_form_rating",
        "position_diff",
        "points_diff",
        "home_advantage",
    ]

    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.label_encoder = LabelEncoder() if SKLEARN_AVAILABLE else None
        self.is_trained = False

        if SKLEARN_AVAILABLE:
            self._initialize_model(model_type)

    def _initialize_model(self, model_type: str):
        """Inicializar modelo de ML"""
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        elif model_type == "logistic_regression":
            self.model = LogisticRegression(
                max_iter=1000, random_state=42, multi_class="multinomial"
            )
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def prepare_training_data(
        self, matches: list[dict], standings: list[dict]
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Preparar datos de entrenamiento desde partidos históricos

        Args:
            matches: Lista de partidos con resultados
            standings: Datos de tabla para extraer features

        Returns:
            Tuple con X (features) e y (labels)
        """
        x_features = []
        y = []

        # Crear diccionario de equipos para búsqueda rápida
        team_stats = {}
        for entry in standings:
            team_name = entry.get("team", {}).get("name", "").lower()
            if team_name:
                team_stats[team_name] = entry

        for match in matches:
            # Solo usar partidos terminados
            if match.get("status") != "FINISHED":
                continue

            home_team = match.get("homeTeam", {}).get("name", "").lower()
            away_team = match.get("awayTeam", {}).get("name", "").lower()

            if home_team not in team_stats or away_team not in team_stats:
                continue

            # Extraer features
            features = self._extract_features(team_stats[home_team], team_stats[away_team])

            if features is None:
                continue

            # Extraer label (resultado)
            score = match.get("score", {})
            home_goals = score.get("home", 0)
            away_goals = score.get("away", 0)

            if home_goals > away_goals:
                result = MatchResult.HOME_WIN.value
            elif away_goals > home_goals:
                result = MatchResult.AWAY_WIN.value
            else:
                result = MatchResult.DRAW.value

            x_features.append(features)
            y.append(result)

        return np.array(x_features), np.array(y)

    def _extract_features(
        self,
        home_stats: dict,
        away_stats: dict,
        home_form: dict | None = None,
        away_form: dict | None = None,
    ) -> list[float] | None:
        """Extraer vector de features para un partido"""
        try:
            home_played = max(home_stats.get("playedGames", 1), 1)
            away_played = max(away_stats.get("playedGames", 1), 1)

            features = [
                # Home features
                home_stats.get("position", 10),
                home_stats.get("points", 0),
                home_stats.get("points", 0) / home_played,  # PPG
                home_stats.get("goalDifference", 0),
                home_stats.get("won", 0) / home_played,  # Win rate
                home_form.get("form_rating", 50) if home_form else 50,
                # Away features
                away_stats.get("position", 10),
                away_stats.get("points", 0),
                away_stats.get("points", 0) / away_played,  # PPG
                away_stats.get("goalDifference", 0),
                away_stats.get("won", 0) / away_played,  # Win rate
                away_form.get("form_rating", 50) if away_form else 50,
                # Comparative features
                home_stats.get("position", 10) - away_stats.get("position", 10),
                home_stats.get("points", 0) - away_stats.get("points", 0),
                # Home advantage (always 1 for home team)
                1.0,
            ]

            return features

        except Exception as e:
            logger.error(f"Error extrayendo features: {e}")
            return None

    def train(
        self, matches: list[dict], standings: list[dict], test_size: float = 0.2
    ) -> dict[str, Any]:
        """
        Entrenar modelo con datos históricos

        Args:
            matches: Partidos históricos con resultados
            standings: Tabla de posiciones para features
            test_size: Proporción de datos para test

        Returns:
            Métricas de entrenamiento
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "sklearn no disponible", "model": "heuristic"}

        # Preparar datos
        x_features, y = self.prepare_training_data(matches, standings)

        if len(x_features) < 10:
            return {"error": "Datos insuficientes para entrenar", "samples": len(x_features)}

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)

        # Split datos
        x_train, x_test, y_train, y_test = train_test_split(
            x_features, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )

        # Normalizar features
        x_train_scaled = self.scaler.fit_transform(x_train)
        x_test_scaled = self.scaler.transform(x_test)

        # Entrenar modelo
        self.model.fit(x_train_scaled, y_train)
        self.is_trained = True

        # Evaluar
        y_pred = self.model.predict(x_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)

        # Cross-validation
        cv_scores = cross_val_score(self.model, x_train_scaled, y_train, cv=5)

        # Matriz de confusión
        cm = confusion_matrix(y_test, y_pred)

        return {
            "model_type": self.model_type,
            "samples_total": len(x_features),
            "samples_train": len(x_train),
            "samples_test": len(x_test),
            "accuracy": round(float(accuracy), 4),
            "cv_mean": round(float(cv_scores.mean()), 4),
            "cv_std": round(float(cv_scores.std()), 4),
            "confusion_matrix": cm.tolist(),
            "classes": self.label_encoder.classes_.tolist(),
            "feature_importance": self._get_feature_importance(),
        }

    def _get_feature_importance(self) -> dict[str, float] | None:
        """Obtener importancia de features (solo para tree-based models)"""
        if not hasattr(self.model, "feature_importances_"):
            return None

        importance = self.model.feature_importances_
        return {
            name: round(float(imp), 4)
            for name, imp in zip(self.FEATURE_NAMES, importance, strict=False)
        }

    def predict(
        self,
        home_stats: dict,
        away_stats: dict,
        home_form: dict | None = None,
        away_form: dict | None = None,
    ) -> PredictionOutput:
        """
        Predecir resultado de un partido

        Args:
            home_stats: Estadísticas del equipo local
            away_stats: Estadísticas del equipo visitante
            home_form: Forma reciente del local
            away_form: Forma reciente del visitante

        Returns:
            Predicción con probabilidades
        """
        features = self._extract_features(home_stats, away_stats, home_form, away_form)

        if features is None:
            # Fallback a predicción heurística
            return self._heuristic_prediction(home_stats, away_stats)

        if not SKLEARN_AVAILABLE or not self.is_trained:
            return self._heuristic_prediction(home_stats, away_stats)

        # Normalizar features
        features_scaled = self.scaler.transform([features])

        # Predecir
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]

        # Decodificar label
        result_str = self.label_encoder.inverse_transform([prediction])[0]
        result = MatchResult(result_str)

        # Crear diccionario de probabilidades
        prob_dict = {
            label: round(float(prob), 4)
            for label, prob in zip(self.label_encoder.classes_, probabilities, strict=False)
        }

        confidence = max(probabilities)

        return PredictionOutput(
            predicted_result=result,
            probabilities=prob_dict,
            confidence=confidence,
            features_used=self.FEATURE_NAMES,
            model_name=self.model_type,
        )

    def _heuristic_prediction(self, home_stats: dict, away_stats: dict) -> PredictionOutput:
        """
        Predicción basada en heurísticas cuando ML no está disponible

        Reglas:
        1. Diferencia de posición > 5: favorito gana
        2. Diferencia de puntos significativa: favorito gana
        3. Ventaja de local: +10% para local
        4. Casos cercanos: mayor probabilidad de empate
        """
        home_pos = home_stats.get("position", 10)
        away_pos = away_stats.get("position", 10)
        home_pts = home_stats.get("points", 0)
        away_pts = away_stats.get("points", 0)

        pos_diff = away_pos - home_pos  # Positivo = local mejor
        pts_diff = home_pts - away_pts

        # Base probabilities
        p_home = 0.4  # Ventaja de local base
        p_draw = 0.25
        p_away = 0.35

        # Ajustar por posición
        if pos_diff > 8:
            p_home += 0.25
            p_away -= 0.15
        elif pos_diff > 4:
            p_home += 0.15
            p_away -= 0.10
        elif pos_diff < -8:
            p_away += 0.20
            p_home -= 0.15
        elif pos_diff < -4:
            p_away += 0.10
            p_home -= 0.05

        # Ajustar por puntos
        if pts_diff > 15:
            p_home += 0.10
        elif pts_diff < -15:
            p_away += 0.10

        # Normalizar probabilidades
        total = p_home + p_draw + p_away
        p_home /= total
        p_draw /= total
        p_away /= total

        # Determinar resultado
        if p_home > p_away and p_home > p_draw:
            result = MatchResult.HOME_WIN
            confidence = p_home
        elif p_away > p_home and p_away > p_draw:
            result = MatchResult.AWAY_WIN
            confidence = p_away
        else:
            result = MatchResult.DRAW
            confidence = p_draw

        return PredictionOutput(
            predicted_result=result,
            probabilities={
                "HOME_WIN": round(p_home, 4),
                "DRAW": round(p_draw, 4),
                "AWAY_WIN": round(p_away, 4),
            },
            confidence=confidence,
            features_used=["position", "points"],
            model_name="heuristic",
        )

    def batch_predict(self, matches: list[dict], standings: list[dict]) -> list[dict]:
        """
        Predecir múltiples partidos

        Args:
            matches: Lista de partidos a predecir
            standings: Tabla de posiciones

        Returns:
            Lista de predicciones
        """
        # Crear diccionario de equipos
        team_stats = {}
        for entry in standings:
            team_name = entry.get("team", {}).get("name", "").lower()
            if team_name:
                team_stats[team_name] = entry

        results = []

        for match in matches:
            home_team = match.get("homeTeam", {}).get("name", "").lower()
            away_team = match.get("awayTeam", {}).get("name", "").lower()

            if home_team not in team_stats or away_team not in team_stats:
                results.append(
                    {
                        "match": match,
                        "prediction": None,
                        "error": "Equipo no encontrado en standings",
                    }
                )
                continue

            prediction = self.predict(team_stats[home_team], team_stats[away_team])

            results.append(
                {
                    "match": {
                        "home": match.get("homeTeam", {}).get("name"),
                        "away": match.get("awayTeam", {}).get("name"),
                        "date": match.get("date"),
                    },
                    "prediction": prediction.to_dict(),
                }
            )

        return results
