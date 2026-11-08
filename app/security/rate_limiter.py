"""
High-Performance In-Memory Sliding Window Rate Limiter & Login Brute-Force Throttler
"""
import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status
from app.config import get_settings

settings = get_settings()


class InMemoryRateLimiter:
    """
    Sliding-window counter for rate limiting per client identifier.
    """

    def __init__(self, requests_per_minute: int = 120):
        self.rate_limit = requests_per_minute
        self.window_seconds = 60
        self.client_records: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds

        # Prune old timestamps
        timestamps = [t for t in self.client_records[client_id] if t > cutoff]
        self.client_records[client_id] = timestamps

        if len(timestamps) >= self.rate_limit:
            return False

        self.client_records[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        valid = [t for t in self.client_records[client_id] if t > cutoff]
        return max(0, self.rate_limit - len(valid))


class LoginThrottler:
    """
    Guards authentication endpoints against credential stuffing and brute-force attacks.
    Locks identifier after max_attempts failures within lockout_window seconds.
    """

    def __init__(self, max_attempts: int = 5, lockout_seconds: int = 900):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self.failed_attempts: Dict[str, List[float]] = defaultdict(list)
        self.locked_until: Dict[str, float] = {}

    def is_locked(self, identifier: str) -> Tuple[bool, int]:
        now = time.time()
        if identifier in self.locked_until:
            remaining = int(self.locked_until[identifier] - now)
            if remaining > 0:
                return True, remaining
            else:
                del self.locked_until[identifier]
                self.failed_attempts[identifier] = []
        return False, 0

    def record_failure(self, identifier: str) -> Tuple[bool, int]:
        now = time.time()
        cutoff = now - self.lockout_seconds
        attempts = [t for t in self.failed_attempts[identifier] if t > cutoff]
        attempts.append(now)
        self.failed_attempts[identifier] = attempts

        if len(attempts) >= self.max_attempts:
            self.locked_until[identifier] = now + self.lockout_seconds
            return True, self.lockout_seconds
        return False, 0

    def record_success(self, identifier: str):
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        if identifier in self.locked_until:
            del self.locked_until[identifier]


rate_limiter = InMemoryRateLimiter(settings.RATE_LIMIT_PER_MINUTE)
login_throttler = LoginThrottler(max_attempts=5, lockout_seconds=900)


async def check_rate_limit(request: Request):
    """FastAPI dependency to enforce rate limits per IP or API Key."""
    api_key = request.headers.get("X-API-Key")
    client_ip = request.client.host if request.client else "unknown"
    identifier = f"key:{api_key}" if api_key else f"ip:{client_ip}"

    if not rate_limiter.is_allowed(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 120 requests per minute allowed.",
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(rate_limiter.rate_limit),
                "X-RateLimit-Remaining": "0"
            }
        )
