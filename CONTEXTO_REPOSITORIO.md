# Contexto Técnico del Repositorio — TheMutation

Este documento ofrece un resumen técnico exhaustivo del repositorio TheMutation, diseñado para proporcionar a otra IA o a un nuevo desarrollador un contexto completo y accionable del proyecto.

**Propósito General**

TheMutation contiene un servicio llamado `humanizer-backend`: una API construida con FastAPI que recibe texto generado por modelos de lenguaje y lo "humaniza" (reescribe) según un tono solicitado (académico, ejecutivo, técnico, neutral). El objetivo principal es mejorar la legibilidad, adecuación y estilo del texto producido por LLMs, calcular métricas de legibilidad y aplicar reglas locales de normalización/edición.

**Stack Tecnológico**

- Lenguaje: Python 3.x (sintaxis moderna usada: anotaciones de tipos, union `|` en algunas funciones).
- Framework web: FastAPI (v0.95.2 en `humanizer-backend/requirements.txt`).
- Servidor ASGI: Uvicorn (uvicorn[standard]==0.22.0).
- Clientes HTTP: httpx==0.24.0.
- Validación/Modelos: pydantic==1.10.12.
- Gestión de entorno: python-dotenv==1.0.0.
- Métricas de legibilidad: textstat==0.7.1.
- Cache / Rate limiter optional: redis (redis==4.8.0) y `redis.asyncio` usado en `limiter.py`.
- Observabilidad/logs: structlog==23.3.0 y `prometheus_client==0.16.0` (presente en requirements).
- Tests: pytest==7.4.0 (tests unitarios incluidos).

**Estructura del Proyecto (simplificada)**

- `agents.md`, `skills.md`, documentación general del monorepo.
- `humanizer-backend/`
  - `BITACORA.md` — bitácora de cambios.
  - `Dockerfile`, `Makefile` — recursos de despliegue y construcción.
  - `requirements.txt` — dependencias del servicio.
  - `app/` — código de la aplicación:
    - `main.py` — definición de la app FastAPI y rutas públicas.
    - `config.py` — carga de variables de entorno y constantes de configuración.
    - `schemas.py` — modelos Pydantic para entrada y salida (request/response).
    - `logic.py` — lógica principal: preparación de prompts, llamadas al proveedor y cálculo de métricas.
    - `groq_client.py` — cliente HTTP para el proveedor LLM (GROQ), con modo "simulado" si faltan credenciales.
    - `prompts.py` — plantillas de prompts y configuración por tono.
    - `rules.py` — reglas locales de reemplazo/normalización y carga desde `data/`.
    - `utils.py` — utilidades (sanitización, diff, logging helper).
    - `middleware.py` — middleware de logging y contexto de request_id.
    - `limiter.py` — middleware de rate limiting con backend Redis opcional o estrategia local.
    - `data/` — archivos `reemplazos_frases.txt`, `reemplazos_palabras.txt` con pares de reemplazo.
  - `tests/` — pruebas unitarias para API, lógica y rate limiter.

**Arquitectura y Flujo de Datos**

1. Solicitud entrante HTTP POST a `/api/v1/humanize` o `/api/v1/humanize/diff` (definidas en `main.py`).
2. Middlewares ejecutan: límite de tasa (`limiter.py`), logging (request_id y metadatos) (`middleware.py`).
3. Validación de payload por Pydantic (`schemas.py`).
4. `main.py` delega a `logic.procesar_humanizacion`:
   - sanitiza el texto (`utils.sanitizar_texto`), arma prompts según `prompts.CONFIG_TONOS` y plantilla en `prompts.PROMPTS_POR_TONO`.
   - invoca `groq_client.call_groq_completion` para obtener una respuesta del LLM (o modo simulado si no hay `GROQ_API_KEY`).
   - aplica reglas locales con `rules.aplicar_reglas_basicas` si `apply_rules` es True.
   - calcula métricas de legibilidad con funciones en `logic.calcular_metricas_texto` (usa `textstat`).
5. Respuesta (`HumanizerResponse`) es construida y retornada; la ruta `/api/v1/humanize/diff` añade además un diff unificado (`utils.generar_diff`).

Comunicación externa:
- Llamadas salientes HTTP al proveedor GROQ (URL y API key desde `GROQ_API_URL` y `GROQ_API_KEY`).
- Redis (opcional) para contador de rate limiting (`REDIS_URL`).

**Puntos de Entrada (Entry Points)**

- `humanizer-backend/app/main.py`: instancia la app FastAPI `app` y define rutas principales:
  - `POST /api/v1/humanize` — endpoint principal.
  - `POST /api/v1/humanize/diff` — devuelve texto humanizado y `diff`.
  - `GET /healthz` — healthcheck.
  - `GET /ui` — UI simple embebida para pruebas manuales.

- Cliente local de desarrollo: comando sugerido en `README.md` — `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

**Modelos de Datos / Entidades**

- `TextoInput` (request):
  - `texto`: str (1..10000)
  - `tono`: opcional enum (`academico|ejecutivo|tecnico|neutral`)
  - `max_tokens`: optional int
  - `temperature`: optional float
  - `top_p`: optional float
  - `apply_rules`: optional bool (default True)
  - `rules_probability`: optional float (0..1)
  - `rules_seed`: optional int
  - `metadata`: optional dict

- `Metrics` (subobj respuesta): campos numéricos calculados por `logic.calcular_metricas_texto`:
  - `flesch_reading_ease`, `flesch_kincaid_grade`, `sentence_count`, `word_count`, `avg_words_per_sentence`, `percent_complex_words`.

- `HumanizerResponse` (response):
  - `humanized_text`: str
  - `metrics`: `Metrics`
  - `model_metadata`: opcional dict con metadatos del proveedor (duración, provider, status_code, etc.)
  - `requested_tone`: ToneEnum
  - `warnings`: opcional lista
  - `diff`: opcional str

**Variables de Entorno Necesarias**

Lista de claves consultadas en `app/config.py` (no incluir valores):
- `GROQ_API_KEY`
- `GROQ_API_URL`
- `LOG_LEVEL`
- `ALLOWED_ORIGINS` (separadas por `;`)
- `ENV` (ej. `development`, `production`)
- `REQUEST_SIZE_LIMIT`
- `REDIS_URL`
- `RATE_LIMIT_REQUESTS`
- `RATE_LIMIT_WINDOW`

Adicionales implícitos / recomendados por despliegue / Dockerfile:
- variables para configuración de contenedor o puertos (revisar `Dockerfile` para detalles de runtime si se requiere).

**Consideraciones de Diseño y Operación**

- Fallback a modo simulado en `groq_client` permite desarrollo sin credenciales.
- Rate limiter soporta backend Redis (resiliente) y una estrategia local en memoria (fail-open si Redis falla).
- Logging estructurado con `structlog`; middleware añade `x-request-id` para trazabilidad.
- Tests básicos presentes en `humanizer-backend/tests/` para API, lógica y rate-limiter.

**Siguientes pasos recomendados**

- Añadir un `README.md` más detallado en `humanizer-backend/` con ejemplos de variables de entorno (`.env.example`).
- Documentar contrato del proveedor GROQ y formatos posibles de respuesta en `groq_client.py`.
- Integrar CI que ejecute `pytest` y verifique formato/linting (`ruff` no incluido pero recomendado).

---

Archivo generado automáticamente a partir de la inspección del código fuente. Para más detalles, revisar los módulos señalados en `humanizer-backend/app/`.
