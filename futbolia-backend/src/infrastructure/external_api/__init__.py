# External API module
from .football_api import FootballAPIClient
from .api_football import APIFootballClient
from .thesportsdb import TheSportsDBClient
from .api_selector import UnifiedAPIClient

__all__ = [
    "FootballAPIClient",
    "APIFootballClient",
    "TheSportsDBClient",
    "UnifiedAPIClient",
]
