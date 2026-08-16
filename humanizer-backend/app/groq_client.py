import asyncio
import time
from typing import Any

import httpx

from .config import GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL

_shared_client: httpx.AsyncClient | None = None


def set_global_client(client: httpx.AsyncClient | None) -> None:
    global _shared_client
    _shared_client = client


def _parse_response_text(resp_json: dict[str, Any]) -> str:
    # Try common completion formats
    try:
        return resp_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        pass
    try:
        return resp_json["choices"][0]["text"]
    except (KeyError, IndexError, TypeError):
        pass
    # Fallback: stringify
    return str(resp_json)


async def call_groq_completion(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    retries: int = 3,
    timeout: int = 20,
    client: httpx.AsyncClient | None = None,
) -> tuple[str, dict[str, Any]]:
    """Llama al endpoint definido en `GROQ_API_URL` usando `GROQ_API_KEY`.

    Si no existe la clave, retorna una respuesta simulada para desarrollo local.
    Devuelve (texto, metadata).
    """
    start = time.time()
    # fallback simulado cuando no hay API key
    if not GROQ_API_KEY or not GROQ_API_URL:
        humanized = f"{user_prompt}\n\n[SIMULATED HUMANIZED - temperature={temperature} top_p={top_p}]"
        metadata = {
            "provider": "simulated",
            "duration_ms": int((time.time() - start) * 1000),
            "model": "simulated-1",
            "attempts": 1,
        }
        return humanized, metadata

    url = GROQ_API_URL.rstrip("/")
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }

    last_exc: Exception | None = None
    http_client = client or _shared_client
    should_close = False

    if http_client is None:
        http_client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
        should_close = True

    try:
        for attempt in range(1, retries + 1):
            try:
                resp = await http_client.post(url, json=payload, headers=headers)
                duration_ms = int((time.time() - start) * 1000)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except ValueError:
                        data = {"raw_text": resp.text}
                    text = _parse_response_text(data)
                    metadata = {
                        "provider": "groq",
                        "status_code": resp.status_code,
                        "duration_ms": duration_ms,
                        "model": GROQ_MODEL,
                        "attempts": attempt,
                    }
                    return text, metadata
                if 500 <= resp.status_code < 600 or resp.status_code == 429:
                    # server error o rate limit — reintentar
                    last_exc = RuntimeError(f"provider error {resp.status_code}")
                else:
                    # client error no reintentable
                    raise RuntimeError(f"provider client error {resp.status_code}: {resp.text[:200]}")
            except httpx.RequestError as exc:
                last_exc = exc

            # backoff exponencial solo si queda un intento posterior
            if attempt < retries:
                await asyncio.sleep(2 ** (attempt - 1))

        raise RuntimeError(f"Failed to call Groq after {retries} attempts: {last_exc}")
    finally:
        if should_close and http_client is not None and hasattr(http_client, "aclose"):
            await http_client.aclose()
