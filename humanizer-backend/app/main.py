from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from .schemas import TextoInput, HumanizerResponse, ErrorResponse
from .logic import procesar_humanizacion
from .middleware import LoggingMiddleware
from .utils import generar_diff, configure_logging
from .limiter import RateLimiter
from .rules import recargar_reglas
from .config import ALLOWED_ORIGINS, ENV, LOG_LEVEL

# Logging
configure_logging(level=LOG_LEVEL)

app = FastAPI(title="humanizer-backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimiter)

# Logging middleware
app.add_middleware(LoggingMiddleware)


def _build_humanize_response(payload: TextoInput) -> dict:
    humanized_text, metadata, metrics = procesar_humanizacion(
        payload.texto,
        tono=payload.tono.value if payload.tono else "neutral",
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
        top_p=payload.top_p,
        apply_rules=bool(payload.apply_rules),
        rules_probability=float(payload.rules_probability) if payload.rules_probability is not None else 1.0,
        rules_seed=payload.rules_seed,
    )
    return {
        "humanized_text": humanized_text,
        "metrics": metrics,
        "model_metadata": metadata,
        "requested_tone": payload.tono or "neutral",
        "warnings": None,
    }


def _handle_humanize_errors(fn):
    try:
        return fn()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        return JSONResponse(status_code=502, content={"error": "provider_error", "detail": {"message": str(e)}})
    except Exception:
        return JSONResponse(status_code=500, content={"error": "internal_server_error"})


@app.post("/api/v1/humanize", response_model=HumanizerResponse, responses={400: {"model": ErrorResponse}})
async def humanize_endpoint(payload: TextoInput):
    return _handle_humanize_errors(lambda: _build_humanize_response(payload))


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/api/v1/admin/reload-rules")
async def reload_rules():
    if ENV != "development":
        raise HTTPException(status_code=404, detail="not_found")
    recargar_reglas()
    return {"status": "ok"}


@app.get("/ui", response_class=HTMLResponse)
async def ui():
        html = """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Humanizer UI</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 24px; }
                textarea { width: 100%; height: 200px; }
                pre { background:#f6f8fa; padding:12px; white-space:pre-wrap; }
                .col { display:flex; gap:12px; }
                .col > div { flex:1 }
            </style>
        </head>
        <body>
            <h1>Humanizer - UI</h1>
            <label for="tono">Tono:</label>
            <select id="tono">
                <option value="tecnico">Técnico</option>
                <option value="ejecutivo">Ejecutivo</option>
                <option value="academico">Académico</option>
            </select>

            <p/>
            <textarea id="inputTexto" placeholder="Pega aquí el texto generado por IA..."></textarea>
            <p/>
            <button id="procesar">Procesar</button>

            <h2>Resultado</h2>
            <div class="col">
                <div>
                    <h3>Humanizado</h3>
                    <pre id="resultado">(aún sin procesar)</pre>
                </div>
                <div>
                    <h3>Diff</h3>
                    <pre id="diff">(aún sin procesar)</pre>
                </div>
            </div>

            <script>
                document.getElementById('procesar').addEventListener('click', async () => {
                    const texto = document.getElementById('inputTexto').value;
                    const tono = document.getElementById('tono').value;
                    const res = await fetch('/api/v1/humanize/diff', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ texto: texto, tono: tono })
                    });
                    if (!res.ok) {
                        const t = await res.text();
                        alert('Error: ' + res.status + '\n' + t);
                        return;
                    }
                    const data = await res.json();
                    document.getElementById('resultado').innerText = data.humanized_text || '';
                    document.getElementById('diff').innerText = data.diff || '';
                });
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)


@app.post("/api/v1/humanize/diff", response_model=HumanizerResponse, responses={400: {"model": ErrorResponse}})
async def humanize_with_diff(payload: TextoInput):
    def _build():
        resp = _build_humanize_response(payload)
        resp["diff"] = generar_diff(payload.texto, resp["humanized_text"])
        return resp

    return _handle_humanize_errors(_build)
