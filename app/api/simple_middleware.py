# app/api/simple_middleware.py
import time
from typing import Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def refill(self):
        now = time.time()
        added = (now - self.last_refill) * self.refill_rate
        if added > 0:
            self.tokens = min(self.capacity, self.tokens + added)
            self.last_refill = now

    def consume(self) -> bool:
        self.refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple token bucket rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 10, target_paths: list = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        self.target_paths = target_paths or []
        self.buckets: Dict[str, TokenBucket] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        client_ip = request.headers.get("x-forwarded-for")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        return client_ip
    
    def _should_rate_limit(self, path: str) -> bool:
        """Check if the path should be rate limited."""
        if not self.target_paths:
            return True 
        
        return any(target in path for target in self.target_paths)
    
    def _get_or_create_bucket(self, client_id: str) -> TokenBucket:
        """Get or create token bucket for client."""
        if client_id not in self.buckets:
            self.buckets[client_id] = TokenBucket(
                capacity=self.requests_per_minute,
                refill_rate=self.refill_rate
            )
        return self.buckets[client_id]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request and apply rate limiting."""
        if not self._should_rate_limit(request.url.path):
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        
        bucket = self._get_or_create_bucket(client_id)
        
        if not bucket.consume():
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Too many requests. Please try again later.",
                    "data": None,
                    "rate_limit": {
                        "requests_per_minute": self.requests_per_minute,
                        "available_tokens": int(bucket.tokens)
                    }
                }
            )
        
        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))
        
        return response