# Skills — TheMutation

> Catálogo de **habilidades** disponibles para los agentes definidos en `agents.md`.
> Cada skill describe qué puede hacer, cómo aplicarlo en este proyecto y qué
> herramientas / patrones usa. Los agentes deben referenciar este arquivo antes
> de ejecutar cualquier tarea.

---

## Índice

1. [code_generation](#skill-code_generation)
2. [test_writing](#skill-test_writing)
3. [refactoring](#skill-refactoring)
4. [dependency_management](#skill-dependency_management)
5. [lint_analysis](#skill-lint_analysis)
6. [test_coverage](#skill-test_coverage)
7. [static_analysis](#skill-static_analysis)
8. [ci_pipeline_review](#skill-ci_pipeline_review)
9. [system_design](#skill-system_design)
10. [api_design](#skill-api_design)
11. [scalability_review](#skill-scalability_review)
12. [adr_writing](#skill-adr_writing)
13. [technical_writing](#skill-technical_writing)
14. [openapi_documentation](#skill-openapi_documentation)
15. [changelog_management](#skill-changelog_management)
16. [secret_scanning](#skill-secret_scanning)
17. [dependency_vulnerability_analysis](#skill-dependency_vulnerability_analysis)
18. [auth_review](#skill-auth_review)
19. [rate_limit_validation](#skill-rate_limit_validation)
20. [semver_versioning](#skill-semver_versioning)
21. [docker_builds](#skill-docker_builds)
22. [ci_cd_orchestration](#skill-ci_cd_orchestration)
23. [rollback_planning](#skill-rollback_planning)

---

## Skill: `code_generation`

**Descripción:** Genera código Python idiomático alineado con las convenciones del proyecto.

**Convenciones en este proyecto:**
- Python 3.11+, type hints obligatorios en funciones públicas.
- Pydantic v1 para schemas (`app/schemas.py`).
- FastAPI para rutas (`app/main.py`); usar dependencias de inyección (`Depends`) para lógica transversal.
- `structlog` para logging, nunca `print()`.
- Archivos nuevos en `app/` deben tener `__all__` explícito si exportan símbolos públicos.

**Patrones aplicables:**
```python
# ✅ Correcto: función con type hints y manejo de excepciones tipado
def calcular_metricas(texto: str) -> dict[str, float]:
    if not texto.strip():
        raise ValueError("El texto no puede estar vacío")
    ...

# ❌ Incorrecto: sin tipos, sin validación
def calcular_metricas(texto):
    ...
```

**Archivos clave:** `app/main.py`, `app/logic.py`, `app/schemas.py`, `app/rules.py`

---

## Skill: `test_writing`

**Descripción:** Escribe tests unitarios e de integración con `pytest`.

**Estructura de tests:**
```
tests/
  test_api.py         # Tests de endpoints usando TestClient de FastAPI
  test_logic.py       # Tests unitarios de app/logic.py
  test_rate_limiter.py # Tests del rate limiter
```

**Convenciones:**
- Cada función pública en `app/` debe tener al menos un test.
- Usar `httpx.AsyncClient` o `TestClient` de FastAPI para tests de endpoints.
- Mocks con `unittest.mock` o `pytest-mock` para aislar el cliente Groq.
- Nombrar tests: `test_<función>_<escenario>` (ej: `test_humanize_con_tono_ejecutivo`).

**Ejemplo:**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_returns_ok():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_humanize_sin_api_key_usa_modo_simulado():
    payload = {"texto": "Este es un texto de IA.", "tono": "ejecutivo"}
    response = client.post("/api/v1/humanize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "humanized_text" in data
    assert data["model_metadata"]["provider"] == "simulated"
```

---

## Skill: `refactoring`

**Descripción:** Mejora la estructura del código sin cambiar su comportamiento externo.

**Reglas en este proyecto:**
- Mantener retrocompatibilidad de los contratos de API v1 (`/api/v1/`).
- Extraer lógica compleja de `main.py` hacia módulos específicos (`logic.py`, `rules.py`, etc.).
- Preferir composición sobre herencia.
- No introducir dependencias nuevas sin actualizar `requirements.txt` y notificar al `ReleaseManager`.

**Señales de refactor necesario:**
- Función > 50 líneas → extraer sub-funciones.
- Duplicación de código en más de 2 lugares → abstraer.
- `except Exception` sin re-raise o log → tipar la excepción.

---

## Skill: `dependency_management`

**Descripción:** Gestión de dependencias Python del proyecto.

**Reglas:**
- Todas las dependencias en `requirements.txt` con versión pinneada (`==`).
- Separar dependencias de desarrollo (tests, lint) en `requirements-dev.txt` si no existe aún.
- Antes de agregar una dependencia nueva: verificar licencia, popularidad y mantenimiento activo.
- Ejecutar `pip-audit` o `safety check` tras cada actualización.

**Dependencias vigentes:**
| Paquete            | Versión  | Propósito                       |
|--------------------|----------|---------------------------------|
| fastapi            | 0.95.2   | Framework web                   |
| uvicorn[standard]  | 0.22.0   | Servidor ASGI                   |
| httpx              | 0.24.0   | Cliente HTTP (llamadas a Groq)  |
| textstat           | 0.7.1    | Métricas de legibilidad         |
| python-dotenv      | 1.0.0    | Variables de entorno            |
| pydantic           | 1.10.12  | Validación de schemas           |
| pytest             | 7.4.0    | Testing                         |
| structlog          | 23.3.0   | Logging estructurado            |
| prometheus_client  | 0.16.0   | Métricas Prometheus             |
| redis              | 4.8.0    | Rate limiter distribuido        |

---

## Skill: `lint_analysis`

**Descripción:** Asegura que el código cumple con estilo y calidad mínima.

**Herramientas:**
- `ruff` (preferido sobre `flake8` + `isort` + `black` por velocidad).
- `mypy` para verificación de tipos estáticos.

**Comandos:**
```bash
# Lint y formato
ruff check app/ tests/
ruff format app/ tests/

# Type checking
mypy app/ --ignore-missing-imports
```

**Configuración recomendada (`pyproject.toml` o `ruff.toml`):**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "UP", "B"]
ignore = ["E501"]
```

---

## Skill: `test_coverage`

**Descripción:** Medir y mantener cobertura de tests.

**Herramienta:** `pytest-cov`

**Comandos:**
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

**Umbral mínimo:** 80 % de cobertura de líneas.

**Archivos excluidos de cobertura:**
- `app/logging_config.py` (configuración de infraestructura)
- `app/__init__.py`

---

## Skill: `static_analysis`

**Descripción:** Análisis estático para detectar bugs antes de ejecución.

**Herramientas:**
- `mypy` — verificación de tipos.
- `bandit` — análisis de seguridad estático en Python.
- `radon` — métricas de complejidad ciclomática.

**Comandos:**
```bash
bandit -r app/ -ll
radon cc app/ -a -nc
```

---

## Skill: `ci_pipeline_review`

**Descripción:** Revisión y mejora del pipeline de CI/CD.

**Archivo relevante:** `.github/workflows/ci.yml`

**Checks mínimos que debe tener el pipeline:**
- [ ] Trigger en `push` y `pull_request` a `main`.
- [ ] Setup de Python 3.11.
- [ ] Instalación de dependencias.
- [ ] Lint (ruff / flake8).
- [ ] Tests con cobertura.
- [ ] Build de imagen Docker (validación de Dockerfile).

---

## Skill: `system_design`

**Descripción:** Diseño de sistemas y microservicios.

**Contexto del proyecto:**
- Arquitectura actual: monolito modular dentro de `humanizer-backend/`.
- Extensión futura: separar en microservicios si el tráfico lo justifica.
- Patrón de integración con LLM: cliente HTTP con retry + fallback simulado.

**Principios:**
- 12-Factor App para configuración, logs y procesos.
- API-first: definir contratos OpenAPI antes de implementar.
- Stateless: el servicio no guarda estado entre requests (el rate limiter es infraestructura externa).

---

## Skill: `api_design`

**Descripción:** Diseño de contratos de API REST.

**Estándares en este proyecto:**
- Prefijo de versión: `/api/v1/`.
- Responses con modelos Pydantic tipados.
- Errores con `ErrorResponse` (`error`, `detail`, `request_id`).
- HTTP status codes semánticos (200, 400, 422, 500, 502).

**Convención de nuevos endpoints:**
```
POST /api/v1/<recurso>           → Crear / procesar
GET  /api/v1/<recurso>/<id>      → Obtener
GET  /api/v1/<recurso>           → Listar
POST /api/v1/admin/<acción>      → Admin (solo ENV=development)
```

---

## Skill: `scalability_review`

**Descripción:** Evalúa si el sistema puede escalar bajo carga.

**Checklist:**
- [ ] ¿El rate limiter usa Redis en producción? (ver `REDIS_URL` en `.env`)
- [ ] ¿El servidor Uvicorn corre con múltiples workers? (`--workers N`)
- [ ] ¿Las llamadas a Groq son asíncronas? (actualmente síncronas con `httpx.Client`)
- [ ] ¿Hay caché de respuestas para textos idénticos?
- [ ] ¿El Dockerfile está optimizado para producción? (multi-stage, non-root user)

**Mejoras de escalabilidad pendientes (ver BITACORA.md):**
- Migrar `httpx.Client` → `httpx.AsyncClient` para liberar el event loop.
- Añadir caché con Redis para requests idénticos (hash del texto + tono).
- Implementar Prometheus `/metrics` endpoint con latencia por tono y proveedor.

---

## Skill: `adr_writing`

**Descripción:** Documenta decisiones de arquitectura como ADRs.

**Formato (guardar en `docs/adr/NNN-titulo.md`):**
```markdown
# ADR-NNN: [Título]

## Estado
[Propuesto | Aceptado | Deprecado | Reemplazado por ADR-XXX]

## Contexto
[Por qué se tomó esta decisión]

## Decisión
[Qué se decidió hacer]

## Consecuencias
[Impacto positivo y negativo de la decisión]
```

---

## Skill: `technical_writing`

**Descripción:** Redacción de documentación técnica clara y precisa.

**Reglas:**
- Idioma: español para prosa, inglés para código y términos técnicos.
- Estructura: título → contexto → uso → ejemplos → sección de notas.
- Mantener `BITACORA.md` con entradas fechadas (`YYYY-MM-DD: acción`).
- Usar tablas para comparar opciones o listar métricas.

---

## Skill: `openapi_documentation`

**Descripción:** Documenta la API usando el esquema OpenAPI generado por FastAPI.

**Endpoints de documentación disponibles:**
- `GET /docs` — Swagger UI interactivo.
- `GET /redoc` — ReDoc.
- `GET /openapi.json` — Esquema JSON crudo.

**Para mejorar la documentación:**
- Agregar `summary`, `description` y `tags` a cada endpoint.
- Usar `response_description` en los decoradores de ruta.
- Documentar ejemplos en los schemas Pydantic con `Field(..., example=...)`.

---

## Skill: `changelog_management`

**Descripción:** Mantiene el historial de cambios en formato estándar.

**Formato:** [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)

```markdown
## [1.2.0] - 2026-02-19
### Añadido
- Endpoint `/api/v1/humanize/diff` con resaltado de cambios.

### Cambiado
- Rate limiter ahora soporta Redis en producción.

### Corregido
- Manejo de tildes en reglas locales.
```

---

## Skill: `secret_scanning`

**Descripción:** Detecta secretos exposed en código o historial.

**Herramientas:**
- `git-secrets` o `trufflehog` para historial de Git.
- `detect-secrets` como pre-commit hook.

**Patrones a buscar:**
- `GROQ_API_KEY=gsk_...`
- Cadenas de 32+ caracteres alfanuméricos hardcodeadas.
- URLs con credenciales embebidas.

**Regla:** si se detecta un secreto committed, rotar inmediatamente y usar `git filter-repo` para limpiar el historial.

---

## Skill: `dependency_vulnerability_analysis`

**Descripción:** Audita dependencias en busca de CVEs.

**Comandos:**
```bash
pip install pip-audit
pip-audit -r requirements.txt

# alternativa
pip install safety
safety check -r requirements.txt
```

**Frecuencia:** ejecutar en cada PR que modifique `requirements.txt` y semanalmente en CI.

---

## Skill: `auth_review`

**Descripción:** Revisa la implementación de autenticación y autorización.

**Estado actual:**
- No hay autenticación en el endpoint principal (`/api/v1/humanize`).
- El endpoint admin está protegido por variable de entorno (`ENV`).

**Recomendaciones pendientes:**
- Implementar API Key authentication con middleware o `Depends`.
- Proteger `/api/v1/admin/reload-rules` con un header `X-Admin-Key`.
- Considerar JWT si se añaden usuarios en el futuro.

---

## Skill: `rate_limit_validation`

**Descripción:** Valida que el rate limiter funcione correctamente.

**Configuración:**
| Variable             | Default | Descripción                    |
|----------------------|---------|--------------------------------|
| `RATE_LIMIT_REQUESTS`| 60      | Requests permitidos por ventana |
| `RATE_LIMIT_WINDOW`  | 60      | Ventana en segundos            |
| `REDIS_URL`          | None    | Si definida, usa Redis         |

**Tests de validación:**
```bash
# Verificar que el 61° request es bloqueado
for i in {1..61}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:8000/api/v1/humanize \
    -H 'Content-Type: application/json' \
    -d '{"texto":"test"}'
done
```

---

## Skill: `semver_versioning`

**Descripción:** Gestión del versionado semántico.

**Reglas:**
- `MAJOR.MINOR.PATCH` — seguir [SemVer 2.0](https://semver.org/lang/es/).
- `MAJOR`: cambios incompatibles en la API.
- `MINOR`: nuevas funcionalidades retrocompatibles.
- `PATCH`: correcciones de bugs.

**Flujo:**
1. Crear tag Git: `git tag -a v1.2.0 -m "Release v1.2.0"`
2. Push: `git push origin v1.2.0`
3. Actualizar `BITACORA.md` y `CHANGELOG.md`.

---

## Skill: `docker_builds`

**Descripción:** Construir y optimizar imágenes Docker.

**Dockerfile actual:** `humanizer-backend/Dockerfile`

**Mejoras recomendadas:**
```dockerfile
# Multi-stage build para reducir tamaño de imagen
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
# Copiar solo las dependencias instaladas
COPY --from=builder /root/.local /root/.local
COPY . .
# Usuario no-root para seguridad
RUN adduser --disabled-password --gecos "" appuser
USER appuser
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**Comandos:**
```bash
make docker-build    # construir imagen
make docker-run      # correr contenedor
docker image inspect humanizer-backend:latest  # verificar tamaño
```

---

## Skill: `ci_cd_orchestration`

**Descripción:** Orquestación del ciclo completo de CI/CD.

**Flujo recomendado:**

```
PR creado
  ↓
CI: lint + tests + coverage
  ↓ (si pasa)
CI: build Docker image
  ↓ (si pasa)
QualityGuard aprueba
  ↓
SecurityAuditor aprueba
  ↓
Merge a main
  ↓
CD: push imagen a registry
  ↓
CD: deploy a staging (smoke test)
  ↓
ReleaseManager aprueba
  ↓
CD: deploy a producción
```

---

## Skill: `rollback_planning`

**Descripción:** Planificación de rollback ante fallos en producción.

**Estrategia actual:**
1. **Imagen Docker:** mantener las últimas 3 versiones taggeadas en el registry.
2. **Rollback rápido:** `docker pull humanizer-backend:v<anterior> && docker restart <contenedor>`.
3. **Variables de entorno:** versionar `.env` en un secret manager (no en Git).
4. **Base de datos:** no aplicable actualmente (servicio stateless).

**Criterios de rollback:**
- Error rate > 5 % en los primeros 5 minutos post-deploy.
- Latencia p99 > 3 segundos.
- Healthcheck `/healthz` fallando.

---

*Última actualización: 2026-02-19 | Maintainer: TheMutation Team*
