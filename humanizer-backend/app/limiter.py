import os
import time
import asyncio
from typing import Dict, Tuple, Optional

import redis.asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, REDIS_URL


class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.redis_url = REDIS_URL
        self._redis: Optional[aioredis.Redis] = None
        self._local_buckets: Dict[str, Tuple[int, float]] = {}
        self._lock = asyncio.Lock()

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url)
        return self._redis

    async def dispatch(self, request: Request, call_next):
        client_ip = "unknown"
        try:
            if request.client:
                client_ip = request.client.host
        except Exception:
            pass

        if self.redis_url:
            # Redis Strategy
            try:
                client = await self._get_redis()
                key = f"rl:{client_ip}:{int(time.time() // self.window)}"
                cnt = await client.incr(key)
                if cnt == 1:
                    await client.expire(key, self.window)
                if cnt > self.requests:
                    ttl = await client.ttl(key)
                    retry_after = ttl if ttl and ttl > 0 else self.window
                    return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded", "retry_after": retry_after})
            except Exception:
                # Fail open if Redis is down
                return await call_next(request)
        else:
            # Local Strategy
            now = time.time()
            async with self._lock:
                tokens, last = self._local_buckets.get(client_ip, (self.requests, now))
                elapsed = now - last
                refill = int(elapsed * (self.requests / self.window))
                if refill > 0:
                    tokens = min(self.requests, tokens + refill)
                    last = now
                if tokens <= 0:
                    retry_after = int(self.window - (now - last)) if last else self.window
                    return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded", "retry_after": retry_after})
                tokens -= 1
                self._local_buckets[client_ip] = (tokens, last)

        return await call_next(request)
