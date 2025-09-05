"""Integração com a Cloud API do WhatsApp."""

import requests
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import qrcode

from app.core.config import load_settings

settings = load_settings()


def send_message(phone: str, message: str) -> requests.Response:
    """Envia uma mensagem de texto para o número informado."""
    url = f"{settings.whatsapp_api_url}/{settings.whatsapp_phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"preview_url": False, "body": message},
    }
    return requests.post(url, headers=headers, json=payload, timeout=30)


def upload_media(file_path: str) -> Optional[str]:
    """Realiza o upload de um arquivo e retorna o ID da mídia."""
    url = f"{settings.whatsapp_api_url}/{settings.whatsapp_phone_id}/media"
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
    with Path(file_path).open("rb") as file_handle:
        files = {
            "file": file_handle,
            "messaging_product": (None, "whatsapp"),
        }
        response = requests.post(url, headers=headers, files=files, timeout=30)
    if response.ok:
        return response.json().get("id")
    return None


def send_document(phone: str, media_id: str, caption: str = "") -> requests.Response:
    """Envia um documento previamente enviado para o WhatsApp."""
    url = f"{settings.whatsapp_api_url}/{settings.whatsapp_phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "document",
        "document": {"id": media_id, "caption": caption},
    }
    return requests.post(url, headers=headers, json=payload, timeout=30)


def send_form(phone: str, file_path: str, caption: str = "") -> Optional[requests.Response]:
    """Envia um formulário em PDF ao cliente.

    Autor: Pexe (Instagram: David.devloli)
    """
    if not (settings.whatsapp_token and settings.whatsapp_phone_id):
        return None
    media_id = upload_media(file_path)
    if not media_id:
        return None
    return send_document(phone, media_id, caption)


def generate_qr_code(phone: str, message: str = "") -> Path:
    """Gera um QR Code para iniciar conversa no WhatsApp Web.

    Autor: Pexe (Instagram: David.devloli)
    """
    link = f"https://wa.me/{phone}"
    if message:
        link += f"?text={quote(message)}"
    img = qrcode.make(link)
    output = Path(f"wa_{phone}.png")
    img.save(output)
    return output
