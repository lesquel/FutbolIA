"""
Dataset Management Module
Provides local data storage for fast access without API rate limits
"""
from .data_downloader import DataDownloader
from .dataset_manager import DatasetManager
from .league_registry import LeagueRegistry, GLOBAL_LEAGUES

__all__ = [
    "DataDownloader",
    "DatasetManager", 
    "LeagueRegistry",
    "GLOBAL_LEAGUES",
]
