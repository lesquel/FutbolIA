"""
ETL Pipeline Module
Extract-Transform-Load para datos de fútbol
"""

from .extractor import DataExtractor
from .loader import DataLoader
from .pipeline import ETLPipeline
from .transformer import DataTransformer

__all__ = [
    "DataExtractor",
    "DataTransformer",
    "DataLoader",
    "ETLPipeline",
]
