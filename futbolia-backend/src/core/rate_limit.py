"""
FutbolIA - Rate Limiting Middleware
Protects API endpoints from abuse

Supports both in-memory (for single instance) and Redis (for distributed systems)
"""
import time
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.config import settings
from src.core.logger import log_warning


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm with optional Redis support
    
    Features:
    - Per-IP rate limiting
    - Per-user rate limiting (if authenticated)
    - Different limits for different endpoints
    - Redis support for distributed deployments
    - Efficient in-memory fallback using deque
    """
    
    def __init__(self, app, default_limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        
        # Storage: {identifier: deque(timestamps)} - more efficient than list
        self.requests: Dict[str, deque] = defaultdict(deque)
        
        # Endpoint-specific limits (requests per minute)
        self.endpoint_limits = {
            "/api/v1/predictions/predict": 10,  # AI predictions are expensive
            "/api/v1/teams/generate-players": 5,  # AI generation
            "/api/v1/auth/register": 5,  # Prevent spam registrations
            "/api/v1/auth/login": 10,  # Prevent brute force
        }
        
        # Whitelist (no rate limiting)
        self.whitelist = {
            "/health",
            "/docs",
            "/openapi.json",
            "/",
        }
        
        # Try to initialize Redis if configured
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis client if configured"""
        try:
            if settings.REDIS_URL:
                import redis.asyncio as redis
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                print("✅ Redis rate limiter initialized")
        except Exception as e:
            print(f"⚠️ Redis not available, using in-memory rate limiting: {e}")
            self.redis_client = None
    
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
    
    def _clean_old_requests_local(self, identifier: str, now: float) -> None:
        """Remove requests outside the current window (in-memory)"""
        cutoff = now - self.window_seconds
        while self.requests[identifier] and self.requests[identifier][0] <= cutoff:
            self.requests[identifier].popleft()
    
    def _is_rate_limited_local(self, identifier: str, limit: int) -> Tuple[bool, int, int]:
        """
        Check if identifier is rate limited (in-memory)
        Returns: (is_limited, current_count, reset_time)
        """
        now = time.time()
        self._clean_old_requests_local(identifier, now)
        
        current_count = len(self.requests[identifier])
        reset_time = int(self.window_seconds - (now - self.requests[identifier][0])) if self.requests[identifier] else self.window_seconds
        
        if current_count >= limit:
            return True, current_count, reset_time
        
        # Record this request
        self.requests[identifier].append(now)
        return False, current_count + 1, reset_time
    
    async def _is_rate_limited_redis(self, identifier: str, limit: int) -> Tuple[bool, int, int]:
        """
        Check if identifier is rate limited (Redis)
        Returns: (is_limited, current_count, reset_time)
        """
        try:
            key = f"rate_limit:{identifier}"
            now = int(time.time())
            window_start = now - self.window_seconds
            
            # Use Redis sorted set for efficient sliding window
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = await self.redis_client.zcard(key)
            
            if current_count >= limit:
                # Get reset time from oldest request
                oldest = await self.redis_client.zrange(key, 0, 0, withscores=True)
                reset_time = int(oldest[0][1]) + self.window_seconds - now if oldest else self.window_seconds
                return True, current_count, max(1, reset_time)
            
            # Add current request
            await self.redis_client.zadd(key, {str(now): now})
            await self.redis_client.expire(key, self.window_seconds + 60)
            
            return False, current_count + 1, self.window_seconds
        except Exception as e:
            print(f"⚠️ Redis error, falling back to in-memory: {e}")
            # Fallback to in-memory
            return self._is_rate_limited_local(identifier, limit)
    
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
        
        # Use Redis if available, otherwise fall back to in-memory
        if self.redis_client:
            is_limited, count, reset_time = await self._is_rate_limited_redis(identifier, limit)
        else:
            is_limited, count, reset_time = self._is_rate_limited_local(identifier, limit)
        
        if is_limited:
            log_warning(
                "Rate limit exceeded",
                identifier=identifier,
                path=path,
                limit=limit,
                count=count
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit}/min. Try again in {reset_time}s",
                    "retry_after": reset_time
                },
                headers={"Retry-After": str(reset_time)}
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
    
    _instances: Dict[str, "RateLimiter"] = {}
    
    def __init__(self, limit: int = 10, window: int = 60):
        self.limit = limit
        self.window = window
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Use function name as key
            key = f"{func.__module__}.{func.__name__}"
            
            now = time.time()
            cutoff = now - self.window
            
            # Clean old requests using deque
            while self.requests[key] and self.requests[key][0] <= cutoff:
                self.requests[key].popleft()
            
            if len(self.requests[key]) >= self.limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Function rate limit exceeded. Max {self.limit} calls per {self.window}s"
                )
            
            self.requests[key].append(now)
            return await func(*args, **kwargs)
        
        return wrapper
