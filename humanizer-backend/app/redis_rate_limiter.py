import os
import time
from typing import Optional

import redis.asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW


class RedisRateLimiter(BaseHTTPMiddleware):
    """Rate limiter backed by Redis using simple fixed-window counters.

    Requires `REDIS_URL` env var. Uses keys per client IP.
    """

    def __init__(self, app, redis_url: Optional[str], requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.redis_url = redis_url
        self._client: Optional[aioredis.Redis] = None

    async def _get_client(self) -> aioredis.Redis:
        if self._client is None:
            url = self.redis_url or os.getenv("REDIS_URL")
            if not url:
                raise RuntimeError("REDIS_URL is not configured for RedisRateLimiter")
            self._client = aioredis.from_url(url)
        return self._client

    async def dispatch(self, request: Request, call_next):
        client_ip = None
        try:
            client_ip = request.client.host if request.client else "unknown"
        except Exception:
            client_ip = "unknown"

        key = f"rl:{client_ip}:{int(time.time() // self.window)}"
        client = await self._get_client()
        try:
            cnt = await client.incr(key)
            if cnt == 1:
                await client.expire(key, self.window)

            if cnt > self.requests:
                ttl = await client.ttl(key)
                retry_after = ttl if ttl and ttl > 0 else self.window
                return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded", "retry_after": retry_after})
        except Exception:
            # if Redis fails, fallback to allow (fail-open) but do not block requests
            return await call_next(request)

        return await call_next(request)
