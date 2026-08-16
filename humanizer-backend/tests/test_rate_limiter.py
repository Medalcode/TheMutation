from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import limiter
from app.limiter import RateLimiter
from app.main import app as main_app


def test_rate_limiter_local_blocking():
    """Verifica que el RateLimiter bloquee con 429 al superar el límite de peticiones."""
    app = FastAPI()
    app.add_middleware(RateLimiter, requests=2, window=60)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/ping").status_code == 200
    assert client.get("/ping").status_code == 200
    # Tercera petición excede cuota = 2
    r3 = client.get("/ping")
    assert r3.status_code == 429
    assert r3.json()["error"] == "rate_limit_exceeded"
    assert "retry_after" in r3.json()


def test_rate_limiter_degrades_to_local_on_redis_failure(monkeypatch):
    """Verifica la degradación suave a buckets locales cuando Redis falla."""
    app = FastAPI()

    async def bad_get_redis(self):
        raise RuntimeError("Conexión Redis fallida")

    monkeypatch.setattr(RateLimiter, "_get_redis", bad_get_redis)
    app.add_middleware(RateLimiter, requests=1, window=60)

    @app.get("/test-redis-fail")
    async def ping():
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/test-redis-fail").status_code == 200
    assert client.get("/test-redis-fail").status_code == 429


def test_request_too_large_413(monkeypatch):
    """Verifica que peticiones que superan REQUEST_SIZE_LIMIT reciban HTTP 413 Payload Too Large."""
    monkeypatch.setattr(limiter, "REQUEST_SIZE_LIMIT", 20)

    client = TestClient(main_app)
    payload = {"texto": "a" * 100}
    response = client.post("/api/v1/humanize", json=payload)
    assert response.status_code == 413
    assert response.json() == {"error": "request_too_large"}
