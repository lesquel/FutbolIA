"""
ETL Pipeline Module
Extract-Transform-Load para datos de fútbol
"""
from .extractor import DataExtractor
from .transformer import DataTransformer
from .loader import DataLoader
from .pipeline import ETLPipeline

__all__ = [
    "DataExtractor",
    "DataTransformer",
    "DataLoader",
    "ETLPipeline",
]
