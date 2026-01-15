# Infrastructure module - Technical implementations
"""
FutbolIA Infrastructure Layer

Módulos disponibles:
- datasets: Sistema de datos locales y descarga batch
- etl: Pipeline de Extracción, Transformación y Carga
- clustering: Algoritmos de minería de datos (K-Means, DBSCAN, ML)
- metrics: Sistema de evaluación de predicciones
- external_api: Conectores a APIs externas
- db: Conexiones a bases de datos
- chromadb: Vector store para RAG
- llm: Integraciones con modelos de lenguaje
"""

from .datasets import LeagueRegistry, DataDownloader, DatasetManager
from .etl import DataExtractor, DataTransformer, DataLoader, ETLPipeline
from .clustering import TeamClustering, AdvancedClustering, MatchPredictor
from .metrics import PredictionMetrics, ModelEvaluator, MetricsTracker

__all__ = [
    # Datasets
    "LeagueRegistry",
    "DataDownloader", 
    "DatasetManager",
    # ETL
    "DataExtractor",
    "DataTransformer",
    "DataLoader",
    "ETLPipeline",
    # Clustering & ML
    "TeamClustering",
    "AdvancedClustering",
    "MatchPredictor",
    # Metrics
    "PredictionMetrics",
    "ModelEvaluator",
    "MetricsTracker",
]
