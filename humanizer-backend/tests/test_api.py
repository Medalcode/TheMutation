from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_humanize_minimal():
    payload = {"texto": "Este es un texto de prueba generado por IA.", "tono": "ejecutivo"}
    r = client.post("/api/v1/humanize", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "humanized_text" in data
    assert "metrics" in data
    # metadata should include provider
    assert "model_metadata" in data
    assert data["model_metadata"].get("provider") in ("simulated", "groq")


def test_humanize_with_diff():
    payload = {"texto": "Primera oración. Segunda oración.", "tono": "tecnico"}
    r = client.post("/api/v1/humanize/diff", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "diff" in data
    assert isinstance(data["diff"], str)
