"""
Logging setup.

Uses Python's built-in logging module plus RichHandler for readable
console output.
"""

import logging

from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                show_path=False,
            )
        ],
    )

    # Reduce noisy third-party HTTP logs.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module."""
    return logging.getLogger(name)