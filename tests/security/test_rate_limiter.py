"""
Rate Limiter Unit Tests
"""
from app.security.rate_limiter import InMemoryRateLimiter


def test_rate_limiter_allows_under_quota():
    limiter = InMemoryRateLimiter(requests_per_minute=10)
    for _ in range(10):
        assert limiter.is_allowed("test_client_1") is True


def test_rate_limiter_blocks_over_quota():
    limiter = InMemoryRateLimiter(requests_per_minute=5)
    for _ in range(5):
        assert limiter.is_allowed("test_client_2") is True
    # 6th request must be rejected
    assert limiter.is_allowed("test_client_2") is False
