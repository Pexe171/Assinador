"""Envio de link e tutorial para o cliente."""

from app.services import whatsapp
from app.ui.tray import TrayIcon


def send_form_link(phone: str, url: str) -> None:
    """Envia o link do formulário para o cliente."""
    whatsapp.send_message(phone, f"Acesse o formulário em: {url}")


def send_form_pdf(phone: str, file_path: str, caption: str = "") -> None:
    """Envia um formulário em PDF para o cliente via WhatsApp."""
    media_id = whatsapp.upload_media(file_path)
    if media_id:
        whatsapp.send_document(phone, media_id, caption)
        destinatario = caption or phone
        TrayIcon.notify_global(f"PDF enviado para {destinatario}")
