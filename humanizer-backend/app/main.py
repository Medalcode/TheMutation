import time
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import httpx
import structlog
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from .auth import verify_admin
from .config import ALLOWED_ORIGINS, LOG_LEVEL
from .groq_client import set_global_client
from .limiter import RateLimiter
from .logic import procesar_humanizacion
from .middleware import LoggingMiddleware, request_id_var
from .rules import recargar_reglas
from .schemas import ErrorResponse, HumanizerResponse, TextoInput
from .utils import configure_logging, generar_diff

# Logging
configure_logging(level=LOG_LEVEL)
logger = structlog.get_logger()

# Metricas Prometheus
HUMANIZE_REQUESTS = Counter(
    "humanize_requests_total",
    "Total de peticiones procesadas",
    ["tone", "status"],
)
PROVIDER_LATENCY = Histogram(
    "groq_provider_latency_seconds",
    "Latencia del proveedor LLM en segundos",
    ["provider"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización del cliente HTTP compartido para todas las solicitudes
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        set_global_client(client)
        yield
    set_global_client(None)


app = FastAPI(title="humanizer-backend", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimiter)

# Logging middleware
app.add_middleware(LoggingMiddleware)


# Manejo de errores centralizado: los endpoints solo implementan el camino feliz
# y las excepciones se traducen aquí a respuestas HTTP consistentes.
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(status_code=502, content={"error": "provider_error", "detail": {"message": str(exc)}})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    try:
        req_id = request_id_var.get() or None
    except LookupError:
        req_id = None
    logger.error("unhandled.exception", error=str(exc), request_id=req_id, exc_info=True)
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "request_id": req_id})


async def _build_humanize_response(payload: TextoInput) -> dict:
    start_time = time.time()
    tone_str = payload.tono.value if payload.tono else "neutral"
    try:
        humanized_text, metadata, metrics = await procesar_humanizacion(
            payload.texto,
            tono=tone_str,
            max_tokens=payload.max_tokens,
            temperature=payload.temperature,
            top_p=payload.top_p,
            apply_rules=bool(payload.apply_rules),
            rules_probability=float(payload.rules_probability) if payload.rules_probability is not None else 1.0,
            rules_seed=payload.rules_seed,
        )
        duration = time.time() - start_time
        PROVIDER_LATENCY.labels(provider=metadata.get("provider", "unknown")).observe(duration)
        HUMANIZE_REQUESTS.labels(tone=tone_str, status="success").inc()

        return {
            "humanized_text": humanized_text,
            "metrics": metrics,
            "model_metadata": metadata,
            "requested_tone": payload.tono or "neutral",
            "warnings": None,
        }
    except Exception:
        HUMANIZE_REQUESTS.labels(tone=tone_str, status="error").inc()
        raise


@app.post("/api/v1/humanize", response_model=HumanizerResponse, responses={400: {"model": ErrorResponse}})
async def humanize_endpoint(payload: TextoInput):
    return await _build_humanize_response(payload)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/admin/reload-rules")
async def reload_rules(admin=Depends(verify_admin)):
    recargar_reglas()
    return {"status": "ok"}


_UI_PATH = Path(__file__).resolve().parent / "static" / "ui.html"


@lru_cache(maxsize=1)
def _load_ui() -> str:
    return _UI_PATH.read_text(encoding="utf-8")


@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return HTMLResponse(content=_load_ui())


@app.post("/api/v1/humanize/diff", response_model=HumanizerResponse, responses={400: {"model": ErrorResponse}})
async def humanize_with_diff(payload: TextoInput):
    resp = await _build_humanize_response(payload)
    resp["diff"] = generar_diff(payload.texto, resp["humanized_text"])
    return resp
