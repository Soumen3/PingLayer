"""
Rate Limiter Module

Simple in-memory rate limiting for API endpoints.

Design Decisions:
- In-memory storage (Redis-based in production)
- Per-user rate limiting
- Configurable limits per endpoint
- Sliding window algorithm

Production Consideration:
- This uses in-memory dict (not suitable for multi-process)
- In production, use Redis with redis-py or slowapi
- For Phase 1, this is sufficient for demo purposes
"""

import time
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import HTTPException, status
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.
    
    Tracks requests per user/IP and enforces limits.
    
    Attributes:
        requests: Dict mapping (identifier, endpoint) -> list of timestamps
    """
    
    def __init__(self):
        # Storage: {(identifier, endpoint): [timestamp1, timestamp2, ...]}
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)
    
    def _clean_old_requests(self, identifier: str, endpoint: str, window_seconds: int):
        """
        Remove timestamps older than the window.
        
        Args:
            identifier: User ID or IP address
            endpoint: API endpoint path
            window_seconds: Time window in seconds
        """
        key = (identifier, endpoint)
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Keep only recent requests
        self.requests[key] = [
            ts for ts in self.requests[key]
            if ts > cutoff_time
        ]
    
    def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        max_requests: int = None,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: User ID or IP address
            endpoint: API endpoint path
            max_requests: Maximum requests allowed (default from config)
            window_seconds: Time window in seconds (default 60)
        
        Returns:
            True if within limit, False if exceeded
        """
        if max_requests is None:
            max_requests = settings.rate_limit_per_minute
        
        # Clean old requests
        self._clean_old_requests(identifier, endpoint, window_seconds)
        
        # Check current count
        key = (identifier, endpoint)
        current_count = len(self.requests[key])
        
        if current_count >= max_requests:
            logger.warning(
                f"Rate limit exceeded for {identifier} on {endpoint}: "
                f"{current_count}/{max_requests} requests in {window_seconds}s"
            )
            return False
        
        # Record this request
        self.requests[key].append(time.time())
        return True
    
    def get_remaining(
        self,
        identifier: str,
        endpoint: str,
        max_requests: int = None,
        window_seconds: int = 60
    ) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            identifier: User ID or IP address
            endpoint: API endpoint path
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Number of remaining requests
        """
        if max_requests is None:
            max_requests = settings.rate_limit_per_minute
        
        self._clean_old_requests(identifier, endpoint, window_seconds)
        key = (identifier, endpoint)
        current_count = len(self.requests[key])
        return max(0, max_requests - current_count)
    
    def reset(self, identifier: str = None, endpoint: str = None):
        """
        Reset rate limit counters.
        
        Args:
            identifier: Optional specific identifier to reset
            endpoint: Optional specific endpoint to reset
        
        If both are None, resets all counters.
        """
        if identifier is None and endpoint is None:
            self.requests.clear()
        elif identifier and endpoint:
            key = (identifier, endpoint)
            if key in self.requests:
                del self.requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(
    identifier: str,
    endpoint: str,
    max_requests: int = None,
    window_seconds: int = 60
):
    """
    Dependency function to check rate limit.
    
    Raises HTTPException if limit exceeded.
    
    Args:
        identifier: User ID or IP address
        endpoint: API endpoint path
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Raises:
        HTTPException 429: Too Many Requests
    
    Usage:
        @router.get("/api/data")
        def get_data(current_user: CurrentUser = Depends(get_current_user)):
            check_rate_limit(str(current_user.user_id), "/api/data")
            return {"data": "..."}
    """
    if not rate_limiter.check_rate_limit(identifier, endpoint, max_requests, window_seconds):
        remaining = rate_limiter.get_remaining(identifier, endpoint, max_requests, window_seconds)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again later.",
            headers={
                "X-RateLimit-Limit": str(max_requests or settings.rate_limit_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + window_seconds))
            }
        )


# Decorator for rate limiting (alternative approach)
def rate_limit(max_requests: int = None, window_seconds: int = 60):
    """
    Decorator for rate limiting endpoints.
    
    Note: This is a simplified version. In production, use a proper
    rate limiting library like slowapi.
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Usage:
        @router.get("/api/data")
        @rate_limit(max_requests=10, window_seconds=60)
        def get_data():
            return {"data": "..."}
    """
    def decorator(func):
        # This is a placeholder - proper implementation would use functools.wraps
        # and integrate with FastAPI's dependency system
        return func
    return decorator


if __name__ == "__main__":
    # Test rate limiter
    print("=== Testing Rate Limiter ===")
    
    limiter = RateLimiter()
    
    # Simulate 5 requests (limit is 3)
    for i in range(5):
        allowed = limiter.check_rate_limit("user_123", "/api/test", max_requests=3)
        remaining = limiter.get_remaining("user_123", "/api/test", max_requests=3)
        print(f"Request {i+1}: Allowed={allowed}, Remaining={remaining}")
    
    # Reset and try again
    limiter.reset("user_123", "/api/test")
    print("\nAfter reset:")
    allowed = limiter.check_rate_limit("user_123", "/api/test", max_requests=3)
    remaining = limiter.get_remaining("user_123", "/api/test", max_requests=3)
    print(f"Allowed={allowed}, Remaining={remaining}")
