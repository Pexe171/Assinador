"""Envio de link e tutorial para o cliente."""

from app.services import whatsapp


def send_form_link(phone: str, url: str) -> None:
    """Envia o link do formulário para o cliente."""
    whatsapp.send_message(phone, f"Acesse o formulário em: {url}")
