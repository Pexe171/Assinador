"""Valida a assinatura e notifica o cliente."""

from app.services import validator, whatsapp
from app.ui.tray import TrayIcon


def validate_and_notify(phone: str, p7s: bytes) -> None:
    """Valida o arquivo assinado e avisa o cliente."""
    if validator.validate_signature(p7s):
        whatsapp.send_message(phone, "Assinatura validada com sucesso!")
        TrayIcon.notify_global(
            f"Assinatura de {phone} validada com sucesso!"
        )
    else:
        whatsapp.send_message(phone, "Falha na validação da assinatura.")
