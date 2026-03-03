# Skills — TheMutation

> Catálogo de **habilidades** disponibles para los agentes definidos en `agents.md`.
> Cada skill describe qué puede hacer, cómo aplicarlo en este proyecto y qué
> herramientas / patrones usa. Los agentes deben referenciar este arquivo antes
> de ejecutar cualquier tarea.

---

## Índice

1. [code_lifecycle](#super-skill-code_lifecycle)
2. [code_audit](#super-skill-code_audit)
3. [system_engineering](#super-skill-system_engineering)
4. [technical_governance](#super-skill-technical_governance)
5. [security_compliance](#super-skill-security_compliance)
6. [release_flow](#super-skill-release_flow)

---

## Super-Skill: `code_lifecycle`
**Parámetros:** `action` ('write', 'refactor', 'test')
- **write**: Genera código Python 3.11+ con type hints y Pydantic v1.
- **refactor**: Optimiza lógica (>50 líneas) y extrae sub-funciones en `app/logic.py`.
- **test**: Implementa tests en `pytest` siguiendo el patrón `test_<fn>_<escenario>`.

## Super-Skill: `code_audit`
**Parámetros:** `check` ('lint', 'coverage', 'static')
- **lint**: Ejecuta `ruff check` y `ruff format`.
- **coverage**: Mantiene umbral ≥ 80% con `pytest-cov`.
- **static**: Análisis con `mypy` (tipos) y `radon` (complejidad ≤ 10).

## Super-Skill: `system_engineering`
**Parámetros:** `facet` ('design', 'api', 'scalability')
- **design**: Sigue 12-Factor App y arquitectura modular.
- **api**: Define contratos OpenAPI en `/api/v1/` usando Pydantic.
- **scalability**: Evalúa async (`httpx.AsyncClient`) y uso de Redis para rate limiting.

## Super-Skill: `technical_governance`
**Parámetros:** `type` ('docs', 'adr', 'changelog')
- **docs**: Mantenimiento de `README.md` y `BITACORA.md`.
- **adr**: Documenta decisiones en `docs/adr/` (formato NNN-titulo.md).
- **changelog**: Gestión de tags y `CHANGELOG.md` (Keep a Changelog).

## Super-Skill: `security_compliance`
**Parámetros:** `audit` ('secrets', 'vulns', 'auth')
- **secrets**: Escaneo de variables de entorno y hardcoded keys.
- **vulns**: Ejecuta `pip-audit -r requirements.txt`.
- **auth**: Verifica protección de endpoints admin y headers de API Key.

## Super-Skill: `release_flow`
**Parámetros:** `stage` ('version', 'docker', 'deploy', 'rollback')
- **version**: Incremento SemVer (Major.Minor.Patch).
- **docker**: Build multi-stage (Dockerfile) optimizado para prod.
- **deploy/rollback**: Orquestación en GitHub Actions y plan de retorno rápido.

---

*Última actualización: 2026-03-03 | Maintainer: MutationOps*
