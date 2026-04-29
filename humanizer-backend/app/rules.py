import random
import re
import unicodedata
from pathlib import Path

_REEMPLAZOS_FRASES = [
    ("por otro lado", "por otra parte"),
    ("en conclusion", "en resumen"),
    ("es importante destacar", "vale la pena mencionar"),
    ("cabe mencionar", "vale mencionar"),
]

_REEMPLAZOS_PALABRAS = [
    ("ademas", "tambien"),
    ("utilizar", "usar"),
    ("adicional", "extra"),
    ("significativo", "importante"),
    ("muy", "bastante"),
]

_DATA_DIR = Path(__file__).resolve().parent / "data"
_FRASES_FILE = _DATA_DIR / "reemplazos_frases.txt"
_PALABRAS_FILE = _DATA_DIR / "reemplazos_palabras.txt"


def _preservar_mayuscula(original: str, reemplazo: str) -> str:
    if original and original[0].isupper():
        return reemplazo[0].upper() + reemplazo[1:]
    return reemplazo


def _normalizar(texto: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", texto) if not unicodedata.combining(ch)
    )


def _normalizar_con_mapa(texto: str) -> tuple[str, list[int]]:
    normalizado = []
    mapa: list[int] = []
    for idx, ch in enumerate(texto):
        for dch in unicodedata.normalize("NFD", ch):
            if unicodedata.combining(dch):
                continue
            normalizado.append(dch)
            mapa.append(idx)
    return "".join(normalizado), mapa


def _reemplazar_frase(texto: str, frase: str, reemplazo: str) -> str:
    if not texto or not frase:
        return texto

    texto_norm, mapa = _normalizar_con_mapa(texto)
    frase_norm = _normalizar(frase)
    if not frase_norm:
        return texto

    patron = re.compile(rf"(?i)\b{re.escape(frase_norm)}\b")
    coincidencias = list(patron.finditer(texto_norm))
    if not coincidencias:
        return texto

    resultado = texto
    for match in reversed(coincidencias):
        inicio_orig = mapa[match.start()]
        fin_orig = mapa[match.end() - 1] + 1
        original = resultado[inicio_orig:fin_orig]
        reemplazo_final = _preservar_mayuscula(original, reemplazo)
        resultado = resultado[:inicio_orig] + reemplazo_final + resultado[fin_orig:]
    return resultado


def _cargar_reemplazos(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    pares: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        linea = raw.strip()
        if not linea or linea.startswith("#"):
            continue
        if "|" not in linea:
            continue
        original, reemplazo = (p.strip() for p in linea.split("|", 1))
        if original and reemplazo:
            pares.append((original, reemplazo))
    return pares


_FRASES_CACHE = _cargar_reemplazos(_FRASES_FILE) or _REEMPLAZOS_FRASES
_PALABRAS_CACHE = _cargar_reemplazos(_PALABRAS_FILE) or _REEMPLAZOS_PALABRAS


def recargar_reglas() -> None:
    global _FRASES_CACHE, _PALABRAS_CACHE
    _FRASES_CACHE = _cargar_reemplazos(_FRASES_FILE) or _REEMPLAZOS_FRASES
    _PALABRAS_CACHE = _cargar_reemplazos(_PALABRAS_FILE) or _REEMPLAZOS_PALABRAS


def aplicar_reglas_basicas(texto: str, probability: float = 1.0, seed: int | None = None) -> str:
    if not texto:
        return texto
    if probability <= 0.0:
        return texto

    rng = random.Random(seed) if seed is not None else random
    frases = _FRASES_CACHE
    palabras = _PALABRAS_CACHE

    resultado = texto
    for frase, reemplazo in frases:
        if rng.random() <= probability:
            resultado = _reemplazar_frase(resultado, frase, reemplazo)

    for palabra, reemplazo in palabras:
        if rng.random() <= probability:
            resultado = _reemplazar_frase(resultado, palabra, reemplazo)

    return resultado
