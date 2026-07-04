"""Rate limiting middleware for API requests"""

from typing import Optional
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.buckets = {}
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if request is allowed for user"""
        now = datetime.utcnow()
        
        if user_id not in self.buckets:
            # Initialize bucket
            self.buckets[user_id] = {
                "tokens": self.requests_per_minute,
                "last_updated": now
            }
            return True
        
        bucket = self.buckets[user_id]
        elapsed = (now - bucket["last_updated"]).total_seconds()
        
        # Refill tokens based on elapsed time
        refill_rate = self.requests_per_minute / 60  # tokens per second
        bucket["tokens"] = min(
            self.requests_per_minute,
            bucket["tokens"] + (elapsed * refill_rate)
        )
        bucket["last_updated"] = now
        
        # Check if token available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        
        return False

def rate_limit(limiter: Optional[RateLimiter] = None, requests_per_minute: int = 60):
    """Decorator for rate limiting endpoints"""
    _limiter = limiter or RateLimiter(requests_per_minute)
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, user_id: str = None, **kwargs):
            if user_id and not _limiter.is_allowed(user_id):
                return {"error": "Rate limit exceeded", "status": 429}
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, user_id: str = None, **kwargs):
            if user_id and not _limiter.is_allowed(user_id):
                return {"error": "Rate limit exceeded", "status": 429}
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
