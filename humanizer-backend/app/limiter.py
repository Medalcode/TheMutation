import os
import time
import asyncio
from typing import Dict, Tuple, Optional

import redis.asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, REDIS_URL, REQUEST_SIZE_LIMIT


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
        # Enforce request size limit (use Content-Length when provided)
        try:
            cl = request.headers.get("content-length")
            if cl is not None:
                try:
                    if int(cl) > REQUEST_SIZE_LIMIT:
                        return JSONResponse(status_code=413, content={"error": "request_too_large"})
                except Exception:
                    pass
        except Exception:
            pass

        use_local = False
        # Try Redis strategy; if Redis fails, degrade to local token-bucket (fail-closed)
        if self.redis_url:
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
                # Redis failed — degrade to local enforcement (do not open)
                use_local = True
        else:
            use_local = True

        if use_local:
            now = time.time()
            async with self._lock:
                tokens, last = self._local_buckets.get(client_ip, (float(self.requests), now))
                elapsed = now - last
                # refill in float tokens per elapsed seconds
                refill = elapsed * (self.requests / float(self.window))
                if refill > 0:
                    tokens = min(float(self.requests), tokens + refill)
                    last = now
                if tokens < 1.0:
                    # calculate retry_after in seconds (approx)
                    retry_after = int(max(1, (1.0 - tokens) * (self.window / float(self.requests))))
                    return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded", "retry_after": retry_after})
                tokens -= 1.0
                self._local_buckets[client_ip] = (tokens, last)

        return await call_next(request)
