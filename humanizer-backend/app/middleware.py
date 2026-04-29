import contextvars
import json
import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .config import REQUEST_SIZE_LIMIT
from .logging_config import configure_logging
from .utils import generate_request_id

configure_logging()

logger = structlog.get_logger()

# contextvar para request_id
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


def _redact_headers(headers: dict, redact_keys=None):
    if redact_keys is None:
        redact_keys = {"authorization", "cookie", "set-cookie", "x-api-key"}
    out = {}
    for k, v in headers.items():
        if k.lower() in redact_keys:
            out[k] = "[REDACTED]"
        else:
            out[k] = v
    return out


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("x-request-id") or generate_request_id()
        request_id_var.set(req_id)
        start = time.time()

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > REQUEST_SIZE_LIMIT:
             return JSONResponse(status_code=413, content={"error": "request_too_large"})

        # extract small body safely (only if small)
        tone = None
        try:
            # Note: request.body() consumes the stream, BaseHTTPMiddleware handles this by re-creating it
            # if we don't handle it carefully. However, for simplicity in fixing the test:
            body_bytes = await request.body()
            body_len = len(body_bytes or b"")
            if body_len > REQUEST_SIZE_LIMIT:
                 return JSONResponse(status_code=413, content={"error": "request_too_large"})

            if body_len and body_len < 2000:
                try:
                    body_json = json.loads(body_bytes.decode("utf-8"))
                    tone = body_json.get("tono") or body_json.get("tone")
                except Exception:
                    tone = None
        except Exception:
            body_len = 0

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = int((time.time() - start) * 1000)
            logger.error("request.error", method=request.method, path=request.url.path, request_id=req_id, duration_ms=duration_ms, error=str(exc))
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
        }

        logger.info("request.completed", **log_data)
        response.headers["x-request-id"] = req_id
        return response
