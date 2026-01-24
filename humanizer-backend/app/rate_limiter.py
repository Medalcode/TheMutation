import time
import asyncio
from typing import Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW


class InMemoryRateLimiter(BaseHTTPMiddleware):
    """Simple token-bucket per IP. Not suitable for multi-process/prod.

    Use Redis or an external gateway for production.
    """

    def __init__(self, app, requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.buckets: Dict[str, Tuple[int, float]] = {}  # ip -> (tokens, last_refill)
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = None
        try:
            client_ip = request.client.host if request.client else "unknown"
        except Exception:
            client_ip = "unknown"

        now = time.time()
        async with self.lock:
            tokens, last = self.buckets.get(client_ip, (self.requests, now))
            # refill
            elapsed = now - last
            refill = int(elapsed * (self.requests / self.window))
            if refill > 0:
                tokens = min(self.requests, tokens + refill)
                last = now

            if tokens <= 0:
                # calculate retry-after roughly
                retry_after = int(self.window - (now - last)) if last else self.window
                return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded", "retry_after": retry_after})

            # consume
            tokens -= 1
            self.buckets[client_ip] = (tokens, last)

        response = await call_next(request)
        return response
