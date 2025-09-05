"""Integração com a API de Assinatura Eletrônica GOV.BR."""

from pathlib import Path
from typing import Optional
import base64
import hashlib

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


def sign_hash(access_token: str, digest: bytes) -> Optional[bytes]:
    """Assina um hash SHA-256 e retorna o conteúdo P7S."""
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "hash": base64.b64encode(digest).decode(),
        "algoritmo": "SHA256",
    }
    try:
        response = requests.post(
            "https://assinatura.api.gov.br/sign-hash",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if response.ok:
            return base64.b64decode(response.json().get("p7s", ""))
    except requests.RequestException:
        pass
    return None


def sign_document(access_token: str, document_path: str) -> Optional[bytes]:
    """Calcula o hash do arquivo e solicita a assinatura ao serviço GOV.BR."""
    data = Path(document_path).read_bytes()
    digest = hashlib.sha256(data).digest()
    return sign_hash(access_token, digest)
