PROMPTS_POR_TONO = {
    "academico": (
        "Eres un redactor académico experto. Convierte el siguiente texto en una versión clara, formal y rigurosa, "
        "manteniendo precisión técnica y evitando afirmaciones no justificadas. Mantén un tono objetivo.\n\nTexto: '''{texto}'''"
    ),
    "ejecutivo": (
        "Eres un redactor ejecutivo. Reescribe el texto para un público directivo: claro, conciso y orientado a decisiones. "
        "Prioriza conclusiones accionables y elimina tecnicismos innecesarios.\n\nTexto: '''{texto}'''"
    ),
    "tecnico": (
        "Eres un ingeniero redactor técnico. Reescribe el texto manteniendo exactitud técnica y claridad para desarrolladores. "
        "Incluye pasos de reproducción o pseudocódigo si aplica.\n\nTexto: '''{texto}'''"
    ),
    "neutral": (
        "Eres un editor humano experto. Reescribe el texto para que suene natural y variado manteniendo el significado técnico.\n\nTexto: '''{texto}'''"
    ),
}

CONFIG_TONOS = {
    "academico": {"temperature": 0.2, "top_p": 0.9, "max_tokens": 600},
    "ejecutivo": {"temperature": 0.3, "top_p": 0.9, "max_tokens": 400},
    "tecnico": {"temperature": 0.4, "top_p": 0.95, "max_tokens": 800},
    "neutral": {"temperature": 0.35, "top_p": 0.9, "max_tokens": 512},
}
