"""Integração com a Cloud API do WhatsApp."""

import requests

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
