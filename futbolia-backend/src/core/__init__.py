# Core module - Configuration, Settings, and Utilities

from src.core.config import get_i18n_string, settings
from src.core.fuzzy_search import (
    auto_complete,
    fuzzy_search_teams,
    get_team_info,
    suggest_corrections,
)
from src.core.logger import (
    get_logger,
    log_api_call,
    log_error,
    log_info,
    log_prediction,
    log_warning,
)
from src.core.rate_limit import RateLimitMiddleware

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
