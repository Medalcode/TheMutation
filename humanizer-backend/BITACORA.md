# Bitácora del proyecto humanizer-backend

Fecha: 24 de enero de 2026

## Tareas realizadas

- 2026-01-24: Crear la estructura inicial del proyecto (`app/`, `tests/`, `requirements.txt`).
- 2026-01-24: Añadir `.env.example` y `README.md` base.
- 2026-01-24: Implementar esquemas Pydantic en `app/schemas.py` (`TextoInput`, `Metrics`, `HumanizerResponse`, `ErrorResponse`).
- 2026-01-24: Añadir `app/prompts.py` con `PROMPTS_POR_TONO` y `CONFIG_TONOS`.
- 2026-01-24: Implementar `app/logic.py` (generación de prompt, limpieza, llamada al proveedor simulada y cálculo de métricas con `textstat`).
- 2026-01-24: Crear `app/groq_client.py` con fallback simulado y versión HTTP (retries, timeouts, parsing).
- 2026-01-24: Añadir utilidades en `app/utils.py` (sanitización, generación de request_id, diff con `difflib`).
- 2026-01-24: Implementar `LoggingMiddleware` en `app/middleware.py` y configurar `structlog` en `app/logging_config.py`.
- 2026-01-24: Implementar `InMemoryRateLimiter` en `app/rate_limiter.py`.
- 2026-01-24: Añadir `RedisRateLimiter` en `app/redis_rate_limiter.py` (opcional, usa `REDIS_URL`).
- 2026-01-24: Añadir endpoints en `app/main.py` (`/api/v1/humanize`, `/api/v1/humanize/diff`, `/healthz`) y una UI simple en `/ui`.
- 2026-01-24: Añadir tests básicos en `tests/` (tests para endpoints, lógica y rate limiter).
- 2026-01-24: Añadir `Makefile`, script `scripts/run_tests.sh`, `Dockerfile` y `.gitignore`.
- 2026-01-24: Añadir workflow CI GitHub Actions en `.github/workflows/ci.yml` para ejecutar tests y lint.

## Tareas pendientes / Recomendadas

- Integrar el SDK oficial de Groq (o el cliente HTTP definitivo) y validar contratos de respuesta.
- Validación y manejo avanzado de errores del proveedor (mapear códigos y reintentos según respuesta).
- Añadir redacción automática y encriptación para logs sensibles si se manejan PII.
- Reemplazar `InMemoryRateLimiter` por una solución distribuida en producción (activar `RedisRateLimiter` con `REDIS_URL`).
- Añadir métricas de perplejidad y determinismo (perplejidad/token entropy) si el proveedor lo permite.
- Mejorar el UI: resaltado de diff, descarga de resultados, y pruebas E2E para interfaz.
- Harden: límites de tamaño de petición a nivel de servidor (Nginx/gateway), autenticación (API keys) y pruebas de carga.
- Documentación: ejemplos de prompts, análisis comparativo de métricas antes/después y notebook de demostración.

## Notas adicionales

- El backend tiene un modo simulado cuando no hay `GROQ_API_KEY` y `GROQ_API_URL` configurados, útil para desarrollo.
- Revisa `README.md` para instrucciones de ejecución y variables de entorno.
