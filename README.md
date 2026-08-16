# 🧬 TheMutation — `humanizer-backend` (v0.2.0)

[![CI](https://github.com/Jonatthan/TheMutation/actions/workflows/ci.yml/badge.svg)](https://github.com/Jonatthan/TheMutation/actions/workflows/ci.yml)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-green)
![Tests Status](https://img.shields.io/badge/tests-54%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

Monorepo para **TheMutation** — servicio principal `humanizer-backend`: API asíncrona de alto rendimiento construida con FastAPI para "humanizar" y reescribir textos generados por modelos de lenguaje (LLM), aplicando reglas de normalización, métricas de legibilidad y transformaciones estilísticas.

---

## 🛠️ Tech Stack & Arquitectura

- **Framework**: FastAPI (Python 3.11+) — Async ASGI API
- **Proveedor LLM**: Groq API (`llama-3.1-70b-versatile`) con fallback a modo simulado automático.
- **Orquestación & Rate Limiting**: Redis 7 (con script Lua atómico `INCR` + `EXPIRE` y token-bucket local de degradación segura).
- **Resiliencia & Concurrencia**: `httpx.AsyncClient` reutilizable vía `lifespan` manager, `asyncio.to_thread` para trabajo CPU-bound y soporte de cabecera `X-Forwarded-For`.
- **Seguridad**: Autenticación en tiempo constante (`secrets.compare_digest`), mitigación de Timing Attacks y sanitización de cabeceras sensibles en logs.
- **Métricas & Logging**: `structlog` (JSON estandarizado con `x-request-id`) y Prometheus (`HUMANIZE_REQUESTS`, `PROVIDER_LATENCY`).
- **Pruebas Automatizadas**: 54 pruebas unitarias, de integración, E2E, smoke y rendimiento con `pytest` (**100% de pasaje**).

---

## 🚀 Inicio Rápido

### Opción 1: Con Docker Compose (Recomendado)

Inicia el backend FastAPI junto a una instancia de Redis 7 con un solo comando:

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8000`.

---

### Opción 2: Desarrollo Local

```bash
cd humanizer-backend
cp .env.example .env   # Configurar variables de entorno si se requiere
python -m venv .venv
source .venv/bin/activate  # En Windows: .\.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 Endpoints de la API

| Método | Path | Descripción | Autenticación |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/humanize` | Humaniza el texto según el tono solicitado | Pública |
| `POST` | `/api/v1/humanize/diff` | Humaniza el texto y retorna el unified diff | Pública |
| `GET` | `/healthz` | Healthcheck de disponibilidad del servicio | Pública |
| `GET` | `/metrics` | Métricas de Prometheus (`HUMANIZE_REQUESTS`, `PROVIDER_LATENCY`) | Pública |
| `GET` | `/ui` | Interfaz interactiva de prueba embebida | Pública |
| `POST` | `/api/v1/admin/reload-rules` | Recarga reglas dinámicamente desde disco | `x-admin-key` / `Bearer` |

---

## 🧪 Ejecución de Pruebas & Calidad de Código

```bash
cd humanizer-backend

# Ejecutar suite completa de 54 pruebas
pytest -v

# Linter y verificación de formato con Ruff
ruff check .
ruff format --check .
```

---

## ⚙️ Variables de Entorno

Ver `.env.example` para la lista completa. Principales variables:

```ini
GROQ_API_KEY=tu_api_key_opcional
GROQ_MODEL=llama-3.1-70b-versatile
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
ADMIN_API_KEY=tu_clave_secreta_admin
ENV=development
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.
