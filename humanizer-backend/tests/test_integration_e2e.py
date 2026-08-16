import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ============================================================================
# 1. INTEGRACIÓN DE ENDPOINTS PRINCIPALES CON TODOS LOS TONOS Y PARÁMETROS
# ============================================================================


@pytest.mark.parametrize("tono", ["academico", "ejecutivo", "tecnico", "neutral"])
def test_e2e_humanize_todos_los_tonos(tono):
    payload = {
        "texto": "Se realizó la optimización del pipeline de datos con latencia reducida.",
        "tono": tono,
        "max_tokens": 128,
        "temperature": 0.3,
        "top_p": 0.85,
        "apply_rules": True,
        "rules_probability": 0.9,
        "rules_seed": 123,
    }
    response = client.post("/api/v1/humanize", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "humanized_text" in data
    assert len(data["humanized_text"]) > 0
    assert data["requested_tone"] == tono
    assert "metrics" in data
    assert data["metrics"]["word_count"] > 0
    assert "model_metadata" in data


def test_e2e_humanize_diff_endpoint():
    payload = {
        "texto": "Por otro lado, es importante destacar los avances técnicos.",
        "tono": "tecnico",
        "apply_rules": True,
    }
    response = client.post("/api/v1/humanize/diff", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "diff" in data
    assert isinstance(data["diff"], str)


# ============================================================================
# 2. AUTENTICACIÓN EN RUTAS DE ADMINISTRACIÓN (/api/v1/admin/reload-rules)
# ============================================================================


def test_admin_reload_rules_con_x_admin_key(monkeypatch):
    monkeypatch.setattr("app.auth.ADMIN_API_KEY", "secreto-admin-test")
    headers = {"x-admin-key": "secreto-admin-test"}
    response = client.post("/api/v1/admin/reload-rules", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_admin_reload_rules_con_bearer_token(monkeypatch):
    monkeypatch.setattr("app.auth.ADMIN_API_KEY", "secreto-admin-test")
    headers = {"authorization": "Bearer secreto-admin-test"}
    response = client.post("/api/v1/admin/reload-rules", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_admin_reload_rules_clave_incorrecta(monkeypatch):
    monkeypatch.setattr("app.auth.ADMIN_API_KEY", "secreto-admin-test")
    headers = {"x-admin-key": "clave-erronea"}
    response = client.post("/api/v1/admin/reload-rules", headers=headers)
    assert response.status_code == 401


def test_admin_reload_rules_produccion_sin_clave_configurada(monkeypatch):
    monkeypatch.setattr("app.auth.ADMIN_API_KEY", None)
    monkeypatch.setattr("app.auth.ENV", "production")
    response = client.post("/api/v1/admin/reload-rules")
    assert response.status_code == 404


# ============================================================================
# 3. MANEJADORES CENTRALIZADOS DE EXCEPCIONES EN FASTAPI
# ============================================================================


def test_exception_handler_value_error(monkeypatch):
    async def mock_procesar(*args, **kwargs):
        raise ValueError("Error de validación simulado")

    monkeypatch.setattr("app.main.procesar_humanizacion", mock_procesar)
    response = client.post("/api/v1/humanize", json={"texto": "Texto de prueba"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Error de validación simulado"


def test_exception_handler_runtime_error(monkeypatch):
    async def mock_procesar(*args, **kwargs):
        raise RuntimeError("Fallo en el proveedor LLM")

    monkeypatch.setattr("app.main.procesar_humanizacion", mock_procesar)
    response = client.post("/api/v1/humanize", json={"texto": "Texto de prueba"})
    assert response.status_code == 502
    assert response.json()["error"] == "provider_error"
    assert "Fallo en el proveedor LLM" in response.json()["detail"]["message"]


def test_exception_handler_unhandled_exception(monkeypatch):
    async def mock_procesar(*args, **kwargs):
        raise ZeroDivisionError("Error inesperado en runtime")

    monkeypatch.setattr("app.main.procesar_humanizacion", mock_procesar)
    local_client = TestClient(app, raise_server_exceptions=False)
    response = local_client.post("/api/v1/humanize", json={"texto": "Texto de prueba"})
    assert response.status_code == 500
    assert response.json()["error"] == "internal_server_error"
