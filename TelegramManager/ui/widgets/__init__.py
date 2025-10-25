# Caminho: TelegramManager/ui/widgets/__init__.py
"""Widgets reutilizáveis da interface."""

from .accounts_manager import AccountsManagerWidget
from .addition_manager import AdditionManagerWidget  # Novo
from .automation import GroupAutomationWidget
from .dashboard import DashboardWidget
from .group_manager import GroupManagerWidget
from .log_console import LogConsoleWidget
from .session_form import SessionFormWidget
from .settings import SettingsWidget
from .user_bank import UserBankWidget

__all__ = [
    "AccountsManagerWidget",
    "AdditionManagerWidget",  # Novo
    "DashboardWidget",
    "GroupAutomationWidget",
    "GroupManagerWidget",
    "LogConsoleWidget",
    "SessionFormWidget",
    "SettingsWidget",
    "UserBankWidget",
]

