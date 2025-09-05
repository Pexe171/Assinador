"""Integração com serviços de assinatura qualificada (ICP-Brasil)."""

from pathlib import Path
from typing import Optional

import requests

from app.core.config import load_settings

settings = load_settings()


def sign_document(document_path: str) -> Optional[bytes]:
    """Assina o documento informado e retorna o conteúdo P7S.

    A implementação realiza uma chamada ao serviço IntegraICP enviando o
    arquivo PDF. O endpoint utilizado é um exemplo e pode variar conforme o
    provedor contratado.
    """
    url = "https://api.integraicp.org.br/sign"
    headers = {"Authorization": f"Bearer {settings.integraicp_token}"}
    with Path(document_path).open("rb") as document:
        files = {"file": (Path(document_path).name, document, "application/pdf")}
        try:
            response = requests.post(url, headers=headers, files=files, timeout=30)
            if response.ok:
                return response.content
        except requests.RequestException:
            pass
    return None
