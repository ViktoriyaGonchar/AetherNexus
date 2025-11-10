"""
Настройка логирования
"""
import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Настройка системы логирования"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Базовый уровень логирования
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Настройка root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                settings.LOGS_DIR / "aethernexus.log",
                encoding="utf-8"
            )
        ]
    )
    
    # Настройка уровней для внешних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

