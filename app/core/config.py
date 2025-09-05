"""Carregamento de configurações do arquivo .env."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import os


@dataclass
class Settings:
    """Configurações da aplicação."""

    whatsapp_token: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    whatsapp_api_url: str = "https://graph.facebook.com/v17.0"

    govbr_client_id: Optional[str] = None
    govbr_client_secret: Optional[str] = None
    govbr_redirect_uri: str = "http://localhost:8000/callbacks/govbr"

    tunnel_provider: str = "cloudflared"


def load_settings(env_file: str = ".env") -> Settings:
    """Carrega as variáveis de ambiente e retorna uma instância de Settings."""
    if Path(env_file).exists():
        load_dotenv(env_file)
    return Settings(
        whatsapp_token=os.getenv("WHATSAPP_TOKEN"),
        whatsapp_phone_id=os.getenv("WHATSAPP_PHONE_ID"),
        whatsapp_api_url=os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v17.0"),
        govbr_client_id=os.getenv("GOVBR_CLIENT_ID"),
        govbr_client_secret=os.getenv("GOVBR_CLIENT_SECRET"),
        govbr_redirect_uri=os.getenv("GOVBR_REDIRECT_URI", "http://localhost:8000/callbacks/govbr"),
        tunnel_provider=os.getenv("TUNNEL_PROVIDER", "cloudflared"),
    )
