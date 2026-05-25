import logging
import sys
from datetime import datetime, timezone


def setup_logger():
    """Настройка логгера для всего приложения"""
    logger = logging.getLogger("dwelve")
    logger.setLevel(logging.INFO)

    # Формат логов
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()


def log_auth_event(event: str, email: str, ip: str = "unknown", success: bool = True):
    """Логирование событий авторизации"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"AUTH | {event} | {status} | email={email} | ip={ip}")


def log_security_event(event: str, detail: str, ip: str = "unknown"):
    """Логирование подозрительных событий"""
    logger.warning(f"SECURITY | {event} | {detail} | ip={ip}")
