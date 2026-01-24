import logging
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


configure_logging()
