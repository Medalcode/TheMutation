import pytest
from fastapi.testclient import TestClient

from app.logic import calcular_metricas_texto, generar_prompt_sistema
from app.main import app
from app.middleware import _redact_headers
from app.rules import _normalizar, _preservar_mayuscula, _reemplazar_frase, aplicar_reglas_basicas
from app.utils import generar_diff, sanitizar_texto

client = TestClient(app)


# ============================================================================
# 1. PRUEBAS DE VALIDACIÓN PYDANTIC Y ESCENARIOS NEGATIVOS (PAYLOAD)
# ============================================================================


def test_pydantic_validation_empty_texto():
    """Texto vacío (longitud 0) debe ser rechazado con 422 Unprocessable Entity."""
    response = client.post("/api/v1/humanize", json={"texto": ""})
    assert response.status_code == 422


def test_pydantic_validation_texto_excede_max_length():
    """Texto mayor a 10,000 caracteres debe ser rechazado con 422."""
    response = client.post("/api/v1/humanize", json={"texto": "a" * 10001})
    assert response.status_code == 422


def test_pydantic_validation_tono_invalido():
    """Tono no reconocido debe ser rechazado por el Enum de Pydantic."""
    response = client.post("/api/v1/humanize", json={"texto": "Texto válido", "tono": "super_informal"})
    assert response.status_code == 422


@pytest.mark.parametrize("max_tokens", [5, 5000])
def test_pydantic_validation_max_tokens_fuera_de_rango(max_tokens):
    """max_tokens fuera de [16, 4096] debe retornar 422."""
    response = client.post("/api/v1/humanize", json={"texto": "Texto válido", "max_tokens": max_tokens})
    assert response.status_code == 422


@pytest.mark.parametrize("temperature", [-0.5, 1.5])
def test_pydantic_validation_temperature_fuera_de_rango(temperature):
    """temperature fuera de [0.0, 1.0] debe retornar 422."""
    response = client.post("/api/v1/humanize", json={"texto": "Texto válido", "temperature": temperature})
    assert response.status_code == 422


@pytest.mark.parametrize("top_p", [-0.1, 1.1])
def test_pydantic_validation_top_p_fuera_de_rango(top_p):
    """top_p fuera de [0.0, 1.0] debe retornar 422."""
    response = client.post("/api/v1/humanize", json={"texto": "Texto válido", "top_p": top_p})
    assert response.status_code == 422


def test_pydantic_validation_rules_probability_invalida():
    """rules_probability fuera de [0.0, 1.0] debe retornar 422."""
    response = client.post("/api/v1/humanize", json={"texto": "Texto válido", "rules_probability": 2.5})
    assert response.status_code == 422


# ============================================================================
# 2. PRUEBAS UNITARIAS Y CASOS BORDE: UTILS
# ============================================================================


def test_sanitizar_texto_casos_borde():
    assert sanitizar_texto(None) == ""
    assert sanitizar_texto("") == ""
    assert sanitizar_texto("   \n\t  ") == ""
    assert sanitizar_texto("Hola    mundo\n\ncon   espacios") == "Hola mundo con espacios"
    assert sanitizar_texto("Cortar este texto", max_len=6) == "Cortar"


def test_sanitizar_texto_unicode_y_emojis():
    texto_complejo = "Texto con tildes (acción, función) y emojis 🚀 y símbolos €!"
    sanitizado = sanitizar_texto(texto_complejo)
    assert "acción" in sanitizado
    assert "🚀" in sanitizado


def test_generar_diff_sin_cambios():
    diff = generar_diff("Texto igual", "Texto igual")
    assert diff == ""


def test_generar_diff_con_cambios():
    diff = generar_diff("Original", "Humanizado")
    assert "-Original" in diff
    assert "+Humanizado" in diff


# ============================================================================
# 3. PRUEBAS UNITARIAS Y CASOS BORDE: RULES
# ============================================================================


def test_preservar_mayuscula():
    assert _preservar_mayuscula("hola", "usar") == "usar"
    assert _preservar_mayuscula("Hola", "usar") == "Usar"
    assert _preservar_mayuscula("", "usar") == "usar"


def test_normalizar_unicodedata():
    assert _normalizar("canción") == "cancion"
    assert _normalizar("MÜNCHEN") == "MUNCHEN"


def test_reemplazar_frase_con_mayusculas():
    original = "Por otro lado, es importante destacar este aspecto."
    resultado = _reemplazar_frase(original, "por otro lado", "por otra parte")
    assert resultado.startswith("Por otra parte")


def test_aplicar_reglas_probabilidad_cero():
    texto = "cabe mencionar que se requiere utilizar una estrategia adicional."
    resultado = aplicar_reglas_basicas(texto, probability=0.0)
    assert resultado == texto


def test_aplicar_reglas_reproducibilidad_con_seed():
    texto = "Es importante destacar que cabe mencionar la conclusion."
    res1 = aplicar_reglas_basicas(texto, probability=0.5, seed=42)
    res2 = aplicar_reglas_basicas(texto, probability=0.5, seed=42)
    assert res1 == res2


# ============================================================================
# 4. PRUEBAS UNITARIAS Y CASOS BORDE: LOGIC & PROMPTS
# ============================================================================


def test_generar_prompt_sistema_fallback():
    prompt = generar_prompt_sistema("tono_inexistente")
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_calcular_metricas_texto_casos_extremos():
    # Texto extremadamente corto o de un solo carácter
    m1 = calcular_metricas_texto("a")
    assert m1["word_count"] == 1
    assert m1["sentence_count"] == 1
    assert m1["percent_complex_words"] == 0.0

    # Texto con palabras complejas (>6 caracteres)
    m2 = calcular_metricas_texto("Democratización e infraestructura de arquitectura contemporánea")
    assert m2["percent_complex_words"] > 0.0


# ============================================================================
# 5. PRUEBAS DE SEGURIDAD EN LOGS (REDACTION)
# ============================================================================


def test_redact_headers_sensitivos():
    headers = {
        "authorization": "Bearer token_secreto",
        "X-Admin-Key": "admin_key_super_secreta",
        "cookie": "session=12345",
        "Content-Type": "application/json",
    }
    redacted = _redact_headers(headers)
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["X-Admin-Key"] == "[REDACTED]"
    assert redacted["cookie"] == "[REDACTED]"
    assert redacted["Content-Type"] == "application/json"
