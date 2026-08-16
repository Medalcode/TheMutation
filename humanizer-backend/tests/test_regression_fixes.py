import asyncio

import pytest

from app import groq_client, limiter
from app.logic import generar_prompt_sistema, procesar_humanizacion
from app.middleware import _redact_headers
from app.prompts import PROMPTS_POR_TONO


def test_redact_headers_hides_admin_key():
    headers = {
        "x-admin-key": "secreto-admin",
        "authorization": "Bearer token",
        "content-type": "application/json",
    }
    redacted = _redact_headers(headers)
    assert redacted["x-admin-key"] == "[REDACTED]"
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["content-type"] == "application/json"


def test_system_prompt_no_contiene_placeholder():
    for tono in PROMPTS_POR_TONO:
        prompt = generar_prompt_sistema(tono)
        assert "{texto}" not in prompt


def test_user_prompt_es_el_texto():
    texto = "Texto de entrada."
    humanized, metadata, _ = asyncio.run(procesar_humanizacion(texto))
    assert metadata["provider"] in ("simulated", "groq")
    if metadata["provider"] == "simulated":
        # el modo simulado devuelve user_prompt como cuerpo: debe ser el texto,
        # no la plantilla del system prompt
        assert humanized.startswith(texto)


def test_call_groq_completion_raises_on_4xx(monkeypatch):
    monkeypatch.setattr(groq_client, "GROQ_API_KEY", "key")
    monkeypatch.setattr(groq_client, "GROQ_API_URL", "http://example.com")

    class FakeResp:
        status_code = 401
        text = '{"error": "invalid key"}'

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return FakeResp()

    monkeypatch.setattr(groq_client.httpx, "AsyncClient", FakeAsyncClient)

    with pytest.raises(RuntimeError, match="client error"):
        asyncio.run(groq_client.call_groq_completion(system_prompt="s", user_prompt="u", retries=1))


def test_local_buckets_pruning_evita_crecimiento_ilimitado():
    rl = limiter.RateLimiter(app=None, requests=10, window=60)
    now = 1000.0
    for i in range(11_000):
        rl._local_buckets[f"10.0.{i // 256}.{i % 256}"] = (5.0, now)
    assert len(rl._local_buckets) == 11_000

    rl._prune_local_buckets(now)
    assert len(rl._local_buckets) <= limiter._LOCAL_BUCKETS_MAX
