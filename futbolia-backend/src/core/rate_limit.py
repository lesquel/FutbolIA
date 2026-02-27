"""
FutbolIA - Rate Limiting Middleware
Protects API endpoints from abuse
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from src.core.logger import log_warning


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm

    Features:
    - Per-IP rate limiting
    - Per-user rate limiting (if authenticated)
    - Different limits for different endpoints
    """

    def __init__(self, app, default_limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds

        # Storage: {identifier: [(timestamp, count), ...]}
        self.requests: dict[str, list] = defaultdict(list)

        # Endpoint-specific limits (requests per minute)
        self.endpoint_limits = {
            "/api/v1/predictions/predict": 50,  # AI predictions are expensive
            "/api/v1/teams/generate-players": 50,  # AI generation
            "/api/v1/auth/register": 20,  # Prevent spam registrations
            "/api/v1/auth/login": 30,  # Prevent brute force
        }

        # Whitelist (no rate limiting)
        self.whitelist = {
            "/health",
            "/docs",
            "/openapi.json",
            "/",
        }

    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for the request (IP or user_id)"""
        # Try to get user from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    def _get_limit(self, path: str) -> int:
        """Get rate limit for a specific endpoint"""
        # Check exact match first
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]

        # Check prefix match
        for endpoint, limit in self.endpoint_limits.items():
            if path.startswith(endpoint.rstrip("/")):
                return limit

        return self.default_limit

    def _clean_old_requests(self, identifier: str, now: float) -> None:
        """Remove requests outside the current window"""
        cutoff = now - self.window_seconds
        self.requests[identifier] = [ts for ts in self.requests[identifier] if ts > cutoff]

    def _is_rate_limited(self, identifier: str, limit: int) -> tuple[bool, int, int]:
        """
        Check if identifier is rate limited
        Returns: (is_limited, current_count, reset_time)
        """
        now = time.time()
        self._clean_old_requests(identifier, now)

        current_count = len(self.requests[identifier])
        reset_time = (
            int(self.window_seconds - (now - self.requests[identifier][0]))
            if self.requests[identifier]
            else self.window_seconds
        )

        if current_count >= limit:
            return True, current_count, reset_time

        # Record this request
        self.requests[identifier].append(now)
        return False, current_count + 1, reset_time

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting"""
        path = request.url.path

        # Skip whitelist
        if path in self.whitelist:
            return await call_next(request)

        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        identifier = self._get_identifier(request)
        limit = self._get_limit(path)

        is_limited, count, reset_time = self._is_rate_limited(identifier, limit)

        if is_limited:
            log_warning(
                "Rate limit exceeded", identifier=identifier, path=path, limit=limit, count=count
            )
            # Return JSON response directly instead of raising HTTPException
            # This ensures proper 429 status code instead of 500
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit}/min. Try again in {reset_time}s",
                    "retry_after": reset_time,
                },
                headers={
                    "Retry-After": str(reset_time),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                },
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - count)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response


class RateLimiter:
    """
    Decorator-based rate limiter for specific functions

    Usage:
        @RateLimiter(limit=5, window=60)
        async def my_expensive_function():
            ...
    """

    _instances: dict[str, "RateLimiter"] = {}

    def __init__(self, limit: int = 10, window: int = 60):
        self.limit = limit
        self.window = window
        self.requests: dict[str, list] = defaultdict(list)

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Use function name as key
            key = f"{func.__module__}.{func.__name__}"

            now = time.time()
            cutoff = now - self.window

            # Clean old requests
            self.requests[key] = [ts for ts in self.requests[key] if ts > cutoff]

            if len(self.requests[key]) >= self.limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Function rate limit exceeded. Max {self.limit} calls per {self.window}s",
                )

            self.requests[key].append(now)
            return await func(*args, **kwargs)

        return wrapper
