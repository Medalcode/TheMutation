# TheMutation

Monorepo para el proyecto **TheMutation** — servicio principal `humanizer-backend`: API para "humanizar" texto generado por modelos de lenguaje.

## Stack

- **FastAPI** (Python 3.11+) — async REST API
- **Groq API** — proveedor LLM principal (con modo simulado sin API key)
- **structlog** — logging estructurado con trazabilidad via `x-request-id`
- **Prometheus** — métricas expuestas en `/metrics`
- **Redis** — rate limiting opcional con degradado seguro a token-bucket local
- **Pydantic v2** — validación de schemas
- **textstat** — métricas de legibilidad (Flesch, Flesch-Kincaid)

## Inicio rápido

```bash
cd humanizer-backend
cp .env.example .env   # configurar GROQ_API_KEY (opcional)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| POST | `/api/v1/humanize` | Humaniza texto (ver `app/schemas.py`) |
| POST | `/api/v1/humanize/diff` | Humaniza + devuelve diff unificado |
| GET | `/healthz` | Healthcheck |
| GET | `/metrics` | Métricas Prometheus |
| POST | `/api/v1/admin/reload-rules` | Recarga reglas (protegido) |

## Variables de entorno

Ver `.env.example` para todas las variables disponibles.

## Tests

```bash
cd humanizer-backend
pytest tests -v
```

## Knowledge Graph

`graphify-out/` contiene 66 nodos y 65 aristas del AST del proyecto, permitiendo a agentes AI comprender la arquitectura sin escanear archivos.

## Skills

- **tdd** (skills.sh) — patrones de testing para mantener y expandir la cobertura

## Docker

```bash
cd humanizer-backend
docker build -t humanizer-backend .
```

## CI/CD

`.github/workflows/ci.yml` ejecuta tests + ruff en pushes a `main`.

## Contacto

Para cambios o dudas, revisar `INSIGHTS.txt` y abrir PR.

