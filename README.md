# TheMutation

Monorepo para el proyecto **TheMutation** — servicio principal `humanizer-backend`: API para "humanizar" texto generado por modelos de lenguaje.

Descripción corta

- Servicio: `humanizer-backend` (FastAPI)
- Objetivo: Reescribir textos generados por LLMs según distintos tonos, calcular métricas de legibilidad y aplicar reglas locales de normalización.

Estructura relevante

- `humanizer-backend/` — servicio principal
	- `app/` — código fuente (rutas, lógica, clientes, middlewares)
	- `tests/` — pruebas unitarias y de integración
	- `pyproject.toml` — configuración y dependencias modernas
	- `Dockerfile` — imagen multi-stage lista para producción

Inicio rápido (local)

```bash
cd humanizer-backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints principales

- `POST /api/v1/humanize` — humaniza texto. Payload: `TextoInput` (ver `app/schemas.py`).
- `POST /api/v1/humanize/diff` — devuelve `humanized_text` y `diff` unificado.
- `GET /healthz` — healthcheck.
- `GET /metrics` — métricas Prometheus.
- `POST /api/v1/admin/reload-rules` — recarga reglas (protegido por `ADMIN_API_KEY` o disponible en `ENV=development`).

Variables de entorno importantes

- `GROQ_API_KEY` — clave para proveedor LLM (opcional: si no está, el cliente entra en modo simulado).
- `GROQ_API_URL` — URL del proveedor LLM.
- `REDIS_URL` — URL para rate limiting en Redis (opcional).
- `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW` — configuración del rate limiter.
- `REQUEST_SIZE_LIMIT` — límite máximo de tamaño de body en bytes.
- `ADMIN_API_KEY` — clave para proteger endpoints admin.
- `LOG_LEVEL`, `ALLOWED_ORIGINS`, `ENV` — configuración general.

Desarrollo y pruebas

- Ejecutar tests:

```bash
cd humanizer-backend
./venv/bin/python -m pytest tests
```

- Tests incluidos cubren lógica principal, endpoints básicos, rate limiter y comportamiento ante fallos del proveedor/Redis.

Docker

- Build:

```bash
cd humanizer-backend
docker build -t humanizer-backend .
```

- La imagen usa multi-stage build y corre como usuario no-root; expone `/healthz` y agrega `HEALTHCHECK`.

CI/CD

- Se añadió `.github/workflows/ci.yml` que ejecuta tests y `pip-audit` en pushes y PRs hacia `main`.

Seguridad y observabilidad

- Logging estructurado con `structlog` y trazabilidad via `x-request-id`.
- Métricas expuestas en `/metrics` (Prometheus).
- Rate limiter con backend Redis opcional y degradado seguro a token-bucket local.

Notas operativas y recomendaciones

- Añadir `ADMIN_API_KEY` en el entorno de producción y asegurar `REDIS_URL` con ACLs.
- Asegurar que `pyproject.toml` se mantiene actualizado y ejecutar linters (`ruff`, `mypy`) en CI.

Contacto

Para cambios o dudas, revisar `INSIGHTS.txt` y abrir PR en este repositorio.

