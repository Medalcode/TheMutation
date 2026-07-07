from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.limiter import RateLimiter


def test_rate_limiter_blocking():
    app = FastAPI()

    # mount limiter with low quota for test
    app.add_middleware(RateLimiter, requests=2, window=60)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    client = TestClient(app)

    r1 = client.get("/ping")
    assert r1.status_code == 200
    r2 = client.get("/ping")
    assert r2.status_code == 200
    r3 = client.get("/ping")
    assert r3.status_code == 429
