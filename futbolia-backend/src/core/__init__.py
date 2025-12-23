# Core module - Configuration, Settings, and Utilities

from src.core.config import settings, get_i18n_string
from src.core.logger import get_logger, log_info, log_warning, log_error, log_prediction, log_api_call
from src.core.rate_limit import RateLimitMiddleware
from src.core.fuzzy_search import fuzzy_search_teams, suggest_corrections, auto_complete, get_team_info

__all__ = [
    "settings",
    "get_i18n_string",
    "get_logger",
    "log_info",
    "log_warning", 
    "log_error",
    "log_prediction",
    "log_api_call",
    "RateLimitMiddleware",
    "fuzzy_search_teams",
    "suggest_corrections",
    "auto_complete",
    "get_team_info",
]
