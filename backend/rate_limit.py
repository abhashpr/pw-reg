"""Simple in-memory IP-based rate limiter — no external dependencies."""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status


# Stores: {key: [timestamp, timestamp, ...]}
_buckets: dict = defaultdict(list)


def _get_ip(request: Request) -> str:
    """Get the real client IP, respecting X-Forwarded-For from nginx."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(max_calls: int, period_seconds: int):
    """
    Decorator factory for rate limiting a FastAPI route.

    Usage:
        @router.post("/endpoint")
        @rate_limit(5, 60)   # 5 calls per 60 seconds per IP
        async def handler(request: Request, ...):
    """
    def decorator(func):
        import functools

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs (FastAPI injects it by name)
            request: Request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is not None:
                ip = _get_ip(request)
                key = f"{func.__name__}:{ip}"
                now = time.time()

                # Keep only timestamps within the window
                _buckets[key] = [t for t in _buckets[key] if now - t < period_seconds]

                if len(_buckets[key]) >= max_calls:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Too many requests. Max {max_calls} per {period_seconds}s."
                    )

                _buckets[key].append(now)

            return await func(*args, **kwargs)

        return wrapper
    return decorator
