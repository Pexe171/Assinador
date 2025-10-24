"""Camada de regras de negócio do TelegramManager."""

from .automation import AutomationEngine, AutomationTask
from .container import Container
from .database import Database
from .session_manager import SessionManager
from .telegram_client import TelegramClientPool

__all__ = [
    "AutomationEngine",
    "AutomationTask",
    "Container",
    "Database",
    "SessionManager",
    "TelegramClientPool",
]
