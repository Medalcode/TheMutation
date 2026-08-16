import contextvars
import json
import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .utils import configure_logging, generate_request_id

configure_logging()

logger = structlog.get_logger()

# contextvar para request_id
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

# Headers sensibles que nunca deben aparecer en logs
_REDACT_KEYS = {"authorization", "cookie", "set-cookie", "x-api-key", "x-admin-key", "proxy-authorization"}


def _redact_headers(headers: dict) -> dict:
    return {k: ("[REDACTED]" if k.lower() in _REDACT_KEYS else v) for k, v in headers.items()}


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("x-request-id") or generate_request_id()
        request_id_var.set(req_id)
        start = time.time()

        # La validación de tamaño (413) es responsabilidad exclusiva de RateLimiter.
        # Aquí solo se extrae el tono para logging, y únicamente cuando el body es
        # conocido y pequeño, para no leer en memoria requests grandes.
        tone = None
        try:
            content_length = request.headers.get("content-length", "")
            if content_length.isdigit() and int(content_length) < 2000:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        body_json = json.loads(body_bytes.decode("utf-8"))
                        tone = body_json.get("tono") or body_json.get("tone")
                    except (ValueError, UnicodeDecodeError):
                        tone = None
        except Exception:
            tone = None

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = int((time.time() - start) * 1000)
            logger.error(
                "request.error",
                method=request.method,
                path=request.url.path,
                request_id=req_id,
                duration_ms=duration_ms,
                error=str(exc),
            )
            raise

        duration_ms = int((time.time() - start) * 1000)

        client_ip = None
        try:
            client_ip = request.client.host if request.client else None
        except Exception:
            client_ip = None

        # limited query params
        query = dict(request.query_params)

        headers = _redact_headers(dict(request.headers))

        log_data = {
            "request_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": client_ip,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "query": query,
            "tone": tone,
            "headers": headers,
        }

        logger.info("request.completed", **log_data)
        response.headers["x-request-id"] = req_id
        return response
