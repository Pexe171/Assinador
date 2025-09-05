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
    whatsapp_verify_token: Optional[str] = None
    whatsapp_api_url: str = "https://graph.facebook.com/v17.0"
    whatsapp_app_secret: Optional[str] = None

    govbr_auth_url: str = "https://cas.staging.iti.br/oauth2.0"
    govbr_client_id: Optional[str] = None
    govbr_client_secret: Optional[str] = None
    govbr_redirect_rel: str = "/callbacks/govbr"
    govbr_sign_url: str = (
        "https://assinatura-api.staging.iti.br/externo/v2/assinarPKCS7"
    )

    ufsc_verifier_url: str = "https://pbad.labsec.ufsc.br/verifier-dev/report"

    tunnel_provider: str = "cloudflare"
    ngrok_authtoken: Optional[str] = None
    integraicp_token: Optional[str] = None
    validator_env: str = "producao"


def load_settings(env_file: str = ".env") -> Settings:
    """Carrega as variáveis de ambiente e retorna uma instância de Settings."""
    if Path(env_file).exists():
        load_dotenv(env_file)
    return Settings(
        whatsapp_token=
            os.getenv("WA_ACCESS_TOKEN") or os.getenv("WHATSAPP_TOKEN"),
        whatsapp_phone_id=
            os.getenv("WA_PHONE_NUMBER_ID") or os.getenv("WHATSAPP_PHONE_ID"),
        whatsapp_verify_token=os.getenv("WA_VERIFY_TOKEN"),
        whatsapp_api_url=
            os.getenv("WA_API_URL")
            or os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v17.0"),
        whatsapp_app_secret=
            os.getenv("WA_APP_SECRET") or os.getenv("WHATSAPP_APP_SECRET"),
        govbr_auth_url=os.getenv(
            "GOVBR_AUTH_URL", "https://cas.staging.iti.br/oauth2.0"
        ),
        govbr_client_id=os.getenv("GOVBR_CLIENT_ID"),
        govbr_client_secret=os.getenv("GOVBR_CLIENT_SECRET"),
        govbr_redirect_rel=os.getenv("GOVBR_REDIRECT_REL", "/callbacks/govbr"),
        govbr_sign_url=os.getenv(
            "GOVBR_SIGN_URL",
            "https://assinatura-api.staging.iti.br/externo/v2/assinarPKCS7",
        ),
        ufsc_verifier_url=os.getenv(
            "UFSC_VERIFIER_URL", "https://pbad.labsec.ufsc.br/verifier-dev/report"
        ),
        tunnel_provider=os.getenv("USE_TUNNEL", os.getenv("TUNNEL_PROVIDER", "cloudflare")),
        ngrok_authtoken=os.getenv("NGROK_AUTHTOKEN"),
        integraicp_token=os.getenv("INTEGRAICP_TOKEN"),
        validator_env=os.getenv("VALIDATOR_ENV", "producao"),
    )
