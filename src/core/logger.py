"""Logging configuration with structlog — colored dev output, JSON in production."""

import logging

import structlog


def _get_env() -> str:
    """Get environment name, with fallback for test/import scenarios."""
    try:
        from config import settings

        return settings.get("ENV_FOR_DYNACONF", "DEVELOPMENT").lower()
    except Exception:
        return "development"


def _configure_structlog() -> structlog.stdlib.ProcessorFormatter:
    """Configure structlog and return a formatter for stdlib logging."""
    env = _get_env()
    pre_chain = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
    ]

    if env in ("development", "homologation"):
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.RichTracebackFormatter(
                show_locals=False,
                max_frames=10,
            ),
        )
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )

    if env in ("development", "homologation"):
        processors_list = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ]
    else:
        processors_list = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.format_exc_info,
            renderer,
        ]

    return structlog.stdlib.ProcessorFormatter(
        processors=processors_list,
        foreign_pre_chain=pre_chain,
    )


def configure_logging() -> None:
    """Set up root logger with structlog formatter."""
    env = _get_env()
    formatter = _configure_structlog()

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if env == "development" else logging.INFO)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG if env == "development" else logging.INFO)

    root.handlers = [console]

    # Silence noisy third-party loggers
    for name in ("httpcore", "httpx", "urllib3", "asyncio", "flet_runtime"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a stdlib logger for the given module name."""
    return logging.getLogger(name)
