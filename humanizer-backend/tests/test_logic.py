import asyncio

from app.logic import calcular_metricas_texto, generar_prompt_sistema, procesar_humanizacion


def test_generar_prompt_sistema():
    p = generar_prompt_sistema("tecnico")
    assert isinstance(p, str)
    assert "Reescribe" in p or "Reescribe" in p or len(p) > 10


def test_procesar_humanizacion_simulado():
    texto = "Se implementó una optimización en el pipeline de datos."
    humanized_text, metadata, metrics = asyncio.run(procesar_humanizacion(texto, tono="tecnico"))
    assert isinstance(humanized_text, str)
    assert metadata.get("provider") in ("simulated", "groq")
    assert "SIMULATED" in humanized_text.upper() or len(humanized_text) > 0
    assert isinstance(metrics, dict)


def test_calcular_metricas_texto():
    texto = "Una oración corta. Otra oración más larga que contiene varias palabras técnicas."
    metrics = calcular_metricas_texto(texto)
    assert metrics["word_count"] > 0
    assert "flesch_reading_ease" in metrics
