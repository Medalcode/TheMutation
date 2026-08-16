from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_smoke_healthz():
    """Smoke test: Verificar que el endpoint de healthcheck responde HTTP 200."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_smoke_metrics():
    """Smoke test: Verificar que el endpoint de Prometheus responde contenido valido."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "process_cpu_seconds_total" in response.text or "python_info" in response.text or len(response.text) > 0


def test_smoke_ui():
    """Smoke test: Verificar que el endpoint /ui responde HTML."""
    response = client.get("/ui")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "<!DOCTYPE html>" in response.text or "<html>" in response.text or "<head>" in response.text


def test_smoke_humanize_minimal():
    """Smoke test: Verificar ejecución mínima del endpoint /api/v1/humanize."""
    payload = {"texto": "Este es un texto corto de prueba para el smoke test."}
    response = client.post("/api/v1/humanize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "humanized_text" in data
    assert "metrics" in data
    assert "model_metadata" in data
    assert data["requested_tone"] == "neutral"
