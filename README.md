# TheMutation

Monorepo para el proyecto **TheMutation** — plataforma de transformación y humanización de texto generado por IA.

## Servicios

| Servicio            | Descripción                                      | Docs                                         |
|---------------------|--------------------------------------------------|----------------------------------------------|
| `humanizer-backend` | API FastAPI para humanizar texto (Groq LLM)     | [README](humanizer-backend/README.md)         |

## Documentación para agentes

| Archivo                                          | Propósito                                      |
|--------------------------------------------------|------------------------------------------------|
| [agents.md](agents.md)                           | Definición de agentes del monorepo             |
| [skills.md](skills.md)                           | Catálogo de habilidades para los agentes       |
| [humanizer-backend/agents.md](humanizer-backend/agents.md) | Agentes específicos del servicio  |

## Inicio rápido

```bash
cd humanizer-backend
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interfaz web: [http://localhost:8000/ui](http://localhost:8000/ui)
Docs API: [http://localhost:8000/docs](http://localhost:8000/docs)
