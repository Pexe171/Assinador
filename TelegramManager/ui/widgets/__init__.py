"""Widgets reutilizáveis da interface."""

from .accounts_manager import AccountsManagerWidget
from .automation import GroupAutomationWidget
from .dashboard import DashboardWidget
from .group_manager import GroupManagerWidget
from .log_console import LogConsoleWidget
from .reports import ReportsWidget
from .session_form import SessionFormWidget
from .settings import SettingsWidget
from .user_bank import UserBankWidget

__all__ = [
    "AccountsManagerWidget",
    "DashboardWidget",
    "GroupAutomationWidget",
    "GroupManagerWidget",
    "LogConsoleWidget",
    "ReportsWidget",
    "SessionFormWidget",
    "SettingsWidget",
    "UserBankWidget",
]
