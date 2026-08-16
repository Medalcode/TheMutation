# 📝 Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.2.0] - 2026-08-15

### 🛡️ Seguridad
- Reemplazo de comparaciones directas de clave de administración con `secrets.compare_digest` para erradicar vulnerabilidades a ataques de tiempo (Timing Attacks) en `app/auth.py`.
- Normalización de comprobación de cabecera `Authorization: Bearer` sensible a mayúsculas/minúsculas.

### ⚡ Rendimiento
- Precompilación de expresiones regulares `re.Pattern` en la carga de reglas (`app/rules.py`).
- Delegación de procesamiento pesados CPU-bound a hilos secundarios con `asyncio.to_thread` en `app/logic.py`.
- Reutilización de un único cliente HTTP `httpx.AsyncClient` mediante `lifespan` context manager en FastAPI (`app/main.py` & `app/groq_client.py`).

### 🐛 Correcciones de Errores & Resiliencia
- Extracción de IP real del cliente usando cabecera `X-Forwarded-For` para soporte detrás de proxies inversos y Load Balancers en `app/limiter.py`.
- Ejecución atómica de comandos `INCR` + `EXPIRE` en Redis Rate Limiter utilizando un script Lua (`eval`).
- Reintentos automáticos con backoff exponencial para estados HTTP 429 (Rate Limit del proveedor) en `app/groq_client.py`.

### 🧪 QA & Estrategia de Pruebas
- Creación de una suite piramidal de 54 pruebas unitarias, de integración, E2E, smoke tests y performance con `pytest` (**100% de pasaje**).
- Consolidación y eliminación de archivos de prueba redundantes.

### 🐳 DevOps & Observabilidad
- Creación del archivo `docker-compose.yml` para la orquestación local del backend y Redis.
- Configuración de `.dockerignore` para optimizar el contexto de construcción de contenedores.
- Instrumentación de métricas Prometheus personalizadas (`HUMANIZE_REQUESTS`, `PROVIDER_LATENCY`).
- Actualización de workflow CI/CD en `.github/workflows/ci.yml`.
