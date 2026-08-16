import asyncio
import time

import redis.asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, REDIS_URL, REQUEST_SIZE_LIMIT

# Techo de memoria del fallback local: entradas por IP purgadas al superarlo
_LOCAL_BUCKETS_MAX = 10_000

# Script Lua para incremento y expiración atómica en Redis
_LUA_RATE_LIMIT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


def _get_client_ip(request: Request) -> str:
    """Extrae la IP real del cliente considerando proxies de confianza (X-Forwarded-For)."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.redis_url = REDIS_URL
        self._redis: aioredis.Redis | None = None
        self._local_buckets: dict[str, tuple[int, float]] = {}
        self._lock = asyncio.Lock()
        self._redis_lock = asyncio.Lock()

    async def _get_redis(self) -> aioredis.Redis:
        # Doble inicialización posible bajo concurrencia sin el lock dedicado
        async with self._redis_lock:
            if self._redis is None:
                self._redis = aioredis.from_url(self.redis_url)
        return self._redis

    def _prune_local_buckets(self, now: float) -> None:
        """Evita crecimiento ilimitado del dict por IP (memory leak)."""
        if len(self._local_buckets) <= _LOCAL_BUCKETS_MAX:
            return
        cutoff = now - 2 * self.window
        stale = [ip for ip, (_, last) in self._local_buckets.items() if last < cutoff]
        for ip in stale:
            del self._local_buckets[ip]
        if len(self._local_buckets) > _LOCAL_BUCKETS_MAX:
            # Caso patológico: demasiadas IPs activas a la vez; descartar las más antiguas
            ordered = sorted(self._local_buckets.items(), key=lambda kv: kv[1][1])
            for ip, _ in ordered[: len(self._local_buckets) - _LOCAL_BUCKETS_MAX]:
                del self._local_buckets[ip]

    async def dispatch(self, request: Request, call_next):
        client_ip = _get_client_ip(request)

        # Enforce request size limit (use Content-Length when provided)
        try:
            cl = request.headers.get("content-length")
            if cl is not None:
                try:
                    if int(cl) > REQUEST_SIZE_LIMIT:
                        return JSONResponse(status_code=413, content={"error": "request_too_large"})
                except ValueError:
                    pass
        except Exception:
            pass

        use_local = False
        # Try Redis strategy; if Redis fails, degrade to local token-bucket (fail-closed)
        if self.redis_url:
            try:
                client = await self._get_redis()
                key = f"rl:{client_ip}:{int(time.time() // self.window)}"
                cnt = await client.eval(_LUA_RATE_LIMIT, 1, key, self.window)
                if cnt > self.requests:
                    ttl = await client.ttl(key)
                    retry_after = ttl if ttl and ttl > 0 else self.window
                    content = {"error": "rate_limit_exceeded", "retry_after": retry_after}
                    return JSONResponse(status_code=429, content=content)
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
                    content = {"error": "rate_limit_exceeded", "retry_after": retry_after}
                    return JSONResponse(status_code=429, content=content)
                tokens -= 1.0
                self._local_buckets[client_ip] = (tokens, last)
                self._prune_local_buckets(now)

        return await call_next(request)
