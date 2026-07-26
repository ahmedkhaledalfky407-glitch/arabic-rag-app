from __future__ import annotations

import logging

from config import LOG_DIR


def setup_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("arabic_rag")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handlers = [
        ("app.log", logging.INFO),
        ("errors.log", logging.ERROR),
        ("questions.log", logging.INFO),
        ("answers.log", logging.INFO),
        ("processing.log", logging.INFO),
    ]

    for filename, level in handlers:
        handler = logging.FileHandler(LOG_DIR / filename, encoding="utf-8")
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()
