# External API module
from .api_football import APIFootballClient
from .api_selector import UnifiedAPIClient
from .football_api import FootballAPIClient
from .thesportsdb import TheSportsDBClient

__all__ = [
    "FootballAPIClient",
    "APIFootballClient",
    "TheSportsDBClient",
    "UnifiedAPIClient",
]
