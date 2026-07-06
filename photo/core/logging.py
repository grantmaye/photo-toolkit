from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(run_dir: Path) -> logging.Logger:
    logger = logging.getLogger("photo")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(run_dir / "photo.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
