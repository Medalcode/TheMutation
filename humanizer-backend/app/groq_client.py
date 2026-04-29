import asyncio
import time
from typing import Any

import httpx

from .config import GROQ_API_KEY, GROQ_API_URL


def _parse_response_text(resp_json: dict[str, Any]) -> str:
    # Try common completion formats
    try:
        return resp_json["choices"][0]["message"]["content"]
    except Exception:
        pass
    try:
        return resp_json["choices"][0]["text"]
    except Exception:
        pass
    # Fallback: stringify
    return str(resp_json)


async def call_groq_completion(system_prompt: str, user_prompt: str, max_tokens: int = 512, temperature: float = 0.7, top_p: float = 0.9, retries: int = 3, timeout: int = 20) -> tuple[str, dict[str, Any]]:
    """
    Llama al endpoint definido en `GROQ_API_URL` usando `GROQ_API_KEY`.
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
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }

    attempt = 0
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
                resp = await client.post(url, json=payload, headers=headers)
            duration_ms = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = {"raw_text": resp.text}
                text = _parse_response_text(data)
                metadata = {
                    "provider": "groq",
                    "status_code": resp.status_code,
                    "duration_ms": duration_ms,
                    "attempts": attempt,
                }
                return text, metadata
            elif 500 <= resp.status_code < 600:
                # server error - retry
                last_exc = RuntimeError(f"provider error {resp.status_code}")
            else:
                # client error or other - do not retry
                duration_ms = int((time.time() - start) * 1000)
                try:
                    data = resp.json()
                except Exception:
                    data = {"raw_text": resp.text}
                text = _parse_response_text(data)
                metadata = {
                    "provider": "groq",
                    "status_code": resp.status_code,
                    "duration_ms": duration_ms,
                    "attempts": attempt,
                }
                # return what provider returned even if non-200
                return text, metadata
        except httpx.RequestError as exc:
            last_exc = exc

        # async backoff
        backoff = 1 * (2 ** (attempt - 1))
        await asyncio.sleep(backoff)

    # if we exit loop, raise last exception
    raise RuntimeError(f"Failed to call Groq after {retries} attempts: {last_exc}")

