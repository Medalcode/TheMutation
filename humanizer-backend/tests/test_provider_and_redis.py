import asyncio
import types

import pytest

from app import groq_client, limiter, config


class DummyResp:
    def __init__(self, status_code=500, text="error"):
        self.status_code = status_code
        self.text = text

    def json(self):
        raise ValueError("no json")


def test_call_groq_completion_raises_on_5xx(monkeypatch):
    # Force module to behave as if API key present
    monkeypatch.setattr(groq_client, "GROQ_API_KEY", "key")
    monkeypatch.setattr(groq_client, "GROQ_API_URL", "http://example.com")

    # Mock AsyncClient.post to return 500
    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return DummyResp(status_code=500, text="server error")

    # Replace AsyncClient context manager
    monkeypatch.setattr(groq_client.httpx, "AsyncClient", FakeAsyncClient)

    # Call with retries=1 to avoid long backoff in tests
    with pytest.raises(RuntimeError):
        asyncio.run(groq_client.call_groq_completion(system_prompt="s", user_prompt="u", retries=1))


def test_rate_limiter_degrades_to_local(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()

    # force RateLimiter to raise when getting redis
    async def bad_get_redis(self):
        raise RuntimeError("redis down")

    monkeypatch.setattr(limiter.RateLimiter, "_get_redis", bad_get_redis)

    app.add_middleware(limiter.RateLimiter, requests=1, window=60)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    client = TestClient(app)
    r1 = client.get("/ping")
    assert r1.status_code == 200
    r2 = client.get("/ping")
    assert r2.status_code == 429


def test_request_too_large(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app

    # Make the REQUEST_SIZE_LIMIT small for test (patch limiter module import)
    monkeypatch.setattr(limiter, "REQUEST_SIZE_LIMIT", 10)

    client = TestClient(app)
    payload = {"texto": "a" * 50}
    r = client.post("/api/v1/humanize", json=payload)
    assert r.status_code == 413
