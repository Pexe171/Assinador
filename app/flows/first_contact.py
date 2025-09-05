"""Fluxo de envio do primeiro contato via WhatsApp."""

from app.services import whatsapp


def send_initial_template(phone: str) -> None:
    """Envia a mensagem de primeiro contato."""
    whatsapp.send_message(phone, "Olá! Aqui é o serviço de assinaturas.")
