import difflib
import logging
import re
import uuid

import structlog
from structlog.stdlib import LoggerFactory


def configure_logging(level: str = "INFO"):
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    processors = [
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    logging.basicConfig(level=level)
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


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
