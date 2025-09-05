"""Integração com a API de Assinatura Eletrônica GOV.BR."""

from typing import Optional
import requests

from app.core.config import load_settings

settings = load_settings()


def get_authorization_url(state: str) -> str:
    """Monta a URL de autorização OAuth2."""
    return (
        "https://sso.acesso.gov.br/authorize?response_type=code"
        f"&client_id={settings.govbr_client_id}&redirect_uri={settings.govbr_redirect_uri}"
        f"&scope=assinatura&state={state}"
    )


def exchange_code_for_token(code: str) -> Optional[str]:
    """Troca o código de autorização por um token de acesso."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.govbr_redirect_uri,
        "client_id": settings.govbr_client_id,
        "client_secret": settings.govbr_client_secret,
    }
    response = requests.post("https://sso.acesso.gov.br/token", data=data, timeout=30)
    if response.ok:
        return response.json().get("access_token")
    return None
