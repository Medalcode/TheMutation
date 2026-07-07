from typing import Any

import textstat

from .groq_client import call_groq_completion
from .prompts import CONFIG_TONOS, PROMPTS_POR_TONO
from .rules import aplicar_reglas_basicas
from .utils import sanitizar_texto


def generar_prompt_sistema(tono: str) -> str:
    plantilla = PROMPTS_POR_TONO.get(tono, PROMPTS_POR_TONO["neutral"])
    return plantilla


def calcular_metricas_texto(texto: str) -> dict[str, Any]:
    # textstat puede lanzar errores si el texto es extremadamente corto; manejar eso
    try:
        flesch = textstat.flesch_reading_ease(texto)
        fk = textstat.flesch_kincaid_grade(texto)
    except Exception:
        flesch = 0.0
        fk = 0.0

    import re
    sentences = max(1, len([s for s in re.split(r'[.!?]+', texto) if s.strip() != '']))
    words = max(0, len(texto.split()))
    avg = float(words) / sentences if sentences else float(words)
    # simplistic complex words percent: words longer than 6 chars
    complex_words = len([w for w in texto.split() if len(w) > 6])
    pct_complex = (complex_words / words * 100.0) if words else 0.0

    return {
        "flesch_reading_ease": float(flesch),
        "flesch_kincaid_grade": float(fk),
        "sentence_count": sentences,
        "word_count": words,
        "avg_words_per_sentence": avg,
        "percent_complex_words": pct_complex,
    }


async def procesar_humanizacion(texto: str, tono: str = "neutral", max_tokens: int | None = None, temperature: float | None = None, top_p: float | None = None, apply_rules: bool = True, rules_probability: float = 1.0, rules_seed: int | None = None) -> tuple[str, dict[str, Any], dict[str, Any]]:
    texto_limpio = sanitizar_texto(texto)

    config = CONFIG_TONOS.get(tono, CONFIG_TONOS["neutral"]) if isinstance(tono, str) else CONFIG_TONOS["neutral"]
    max_toks = max_tokens or config.get("max_tokens")
    temp = temperature if temperature is not None else config.get("temperature")
    tp = top_p if top_p is not None else config.get("top_p")

    system_prompt = generar_prompt_sistema(tono)
    user_prompt = system_prompt.replace("{texto}", texto_limpio)

    # Call provider (simulated if no API key)
    humanized_text, metadata = await call_groq_completion(system_prompt=system_prompt, user_prompt=user_prompt, max_tokens=max_toks, temperature=temp, top_p=tp)

    if apply_rules:
        humanized_text = aplicar_reglas_basicas(humanized_text, probability=rules_probability, seed=rules_seed)
    metrics = calcular_metricas_texto(humanized_text)

    return humanized_text, metadata, metrics
