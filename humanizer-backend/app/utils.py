import re
import uuid
from typing import Tuple
import difflib


def generate_request_id() -> str:
    return str(uuid.uuid4())


def sanitizar_texto(texto: str, max_len: int = 10000) -> str:
    if texto is None:
        return ""
    # Normalizar espacios
    s = re.sub(r"\s+", " ", texto).strip()
    if len(s) > max_len:
        s = s[:max_len]
    return s


def generar_diff(original: str, humanized: str) -> str:
    """Genera un unified diff entre original y humanized."""
    orig_lines = original.splitlines(keepends=False)
    hum_lines = humanized.splitlines(keepends=False)
    diff = difflib.unified_diff(orig_lines, hum_lines, fromfile='original', tofile='humanized', lineterm='')
    return '\n'.join(list(diff))
