# humanizer-backend

Microservicio FastAPI para "humanizar" textos generados por IA. Recibe texto, aplica un prompt según tono (académico/ejecutivo/técnico), puede aplicar reglas locales sin IA, mide legibilidad con `textstat` y devuelve el texto transformado junto a métricas.

Ver `.env.example` para variables de entorno.

Comandos útiles:

```bash
# crear entorno e instalar dependencias
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"

# ejecutar en desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ejecutar tests
pytest -q

# alternativas via Makefile
make install
make run
make test
```

Ejemplo `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/humanize \
	-H 'Content-Type: application/json' \
	-d '{"texto":"Este es un texto de prueba generado por IA.", "tono":"ejecutivo", "apply_rules": true, "rules_probability": 0.7, "rules_seed": 42}'
```

Notas:
- Copia `.env.example` a `.env` y configura `GROQ_API_KEY` y `GROQ_API_URL` si usarás el proveedor.
- Si no hay `GROQ_API_KEY` configurada, el backend responde con un modo simulado útil para desarrollo.

Reglas locales (sin IA)

- Las reglas viven en `app/data/` (`reemplazos_frases.txt`, `reemplazos_palabras.txt`) con formato `original|reemplazo`.
- El motor de reglas es sensible a mayúsculas iniciales y hace matching sin tildes (ej: `ademas` encuentra `además`).
- Puedes controlar su uso por request con:
  - `apply_rules` (bool, default `true`)
  - `rules_probability` (float 0.0-1.0, default `1.0`)
  - `rules_seed` (int, opcional, para resultados reproducibles)

Recarga de reglas (solo desarrollo)

- Endpoint: `POST /api/v1/admin/reload-rules`
- Solo disponible cuando `ENV=development` (default).

Rate limiting

- El servicio usa un componente `RateLimiter` híbrido (`app/limiter.py`).
- Por defecto usa **In-memory** (Tokens-bucket) para desarrollo local.
- Si defines `REDIS_URL` en tu `.env`, escala automáticamente a **Redis** para producción.
- Configurable vía `RATE_LIMIT_REQUESTS` y `RATE_LIMIT_WINDOW`.

Interfaz web

- Hay una interfaz simple disponible en `/ui` cuando ejecutas el servidor. Usa el formulario para pegar el texto IA, seleccionar el tono y obtener el texto humanizado y el diff.

Bitácora

- Consulta la bitácora del desarrollo en [BITACORA.md](./BITACORA.md) para ver tareas realizadas y pendientes.
