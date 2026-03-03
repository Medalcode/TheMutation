# Agents — TheMutation

> Este archivo define los **agentes de IA** disponibles para asistir el desarrollo y
> operación del monorepo **TheMutation**. Cada agente tiene un rol acotado y
> responsabilidades específicas, lo que garantiza separación de preocupaciones,
> trazabilidad y escalabilidad a medida que el proyecto crece.

---

## Índice

1. [Convenciones generales](#convenciones-generales)
2. [Agente: MutationDev](#agente-mutationdev)
3. [Agente: MutationOps](#agente-mutationops)

---

## Convenciones generales

| Campo         | Descripción                                                     |
|---------------|-----------------------------------------------------------------|
| `id`          | Identificador único del agente (snake_case)                    |
| `role`        | Rol principal en lenguaje natural                              |
| `scope`       | Servicios / rutas del repo donde actúa                         |
| `skills`      | Habilidades declaradas (ver `skills.md`)                       |
| `constraints` | Restricciones éticas / técnicas que **no** puede violar        |
| `escalate_to` | Agente al que debe escalar si supera su capacidad              |

Todos los agentes deben:

- Leer `skills.md` antes de ejecutar cualquier tarea.
- Registrar su actividad con `structlog` cuando interactúen con servicios en tiempo de ejecución.
- Nunca modificar directamente producción sin aprobación del `ReleaseManager`.
- Respetar las variables de entorno definidas en `.env.example` de cada servicio.

---

## Agente: MutationDev

```yaml
id: mutation_dev
role: Agente generalista de desarrollo, calidad y documentación
scope:
  - "humanizer-backend/"
  - "**/*.py"
  - "**/*.md"
  - "**/tests/**"
skills:
  - code_lifecycle(action='write|refactor|test')
  - code_audit(check='lint|coverage|static')
  - technical_governance(type='docs|changelog')
constraints:
  - No ejecutar migraciones de base de datos sin revisión humana
  - No modificar archivos de configuración de CI/CD sin aprobación de MutationOps
escalate_to: mutation_ops
```

### Responsabilidades

- Generar código Python siguiendo las convenciones del proyecto (PEP 8, type hints, docstrings).
- Mantener la calidad del código mediante linting (`ruff`) y cobertura de tests (≥ 80 %).
- Escribir y actualizar documentación técnica (`README.md`, `BITACORA.md`, `CHANGELOG.md`).
- Proponer refactors incrementales manteniendo retrocompatibilidad de la API.

---

## Agente: MutationOps

```yaml
id: mutation_ops
role: Guardián de arquitectura, seguridad y operaciones (SRE/DevOps)
scope:
  - "**"
  - ".github/workflows/"
  - "Dockerfile"
  - "Makefile"
skills:
  - system_engineering(facet='design|api|scalability')
  - security_compliance(audit='secrets|vulns|auth')
  - release_flow(stage='version|docker|deploy|rollback')
  - technical_governance(type='adr')
constraints:
  - No implementa lógica de negocio directamente exceptuando infraestructura
  - Documenta toda decisión como ADR en docs/adr/
escalate_to: null
```

### Responsabilidades

- Revisar arquitectura y diseño de sistemas (ADRs).
- Gestionar el ciclo de vida de releases y despliegues (CI/CD, Docker, SemVer).
- Auditar seguridad (secretos, vulnerabilidades de dependencias, autenticación).
- Supervisar la escalabilidad y el rendimiento del sistema.


---

*Última actualización: 2026-02-19 | Maintainer: TheMutation Team*
