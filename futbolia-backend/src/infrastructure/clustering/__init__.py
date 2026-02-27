"""
Clustering Infrastructure
Módulo completo para análisis de clustering y predicción de equipos

Incluye:
- TeamClustering: Clustering jerárquico original
- AdvancedClustering: K-Means, DBSCAN, análisis de silueta
- MatchPredictor: Predicción de resultados con ML
"""

from .advanced_clustering import AdvancedClustering, ClusteringResult
from .match_predictor import MatchPredictor, MatchResult, PredictionOutput
from .team_clustering import TeamClustering

__all__ = [
    "TeamClustering",
    "AdvancedClustering",
    "ClusteringResult",
    "MatchPredictor",
    "MatchResult",
    "PredictionOutput",
]
