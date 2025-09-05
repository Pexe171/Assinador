"""Validação de assinaturas digitais."""

import requests

from app.core.config import load_settings

settings = load_settings()


def validate_signature(p7s: bytes) -> bool:
    """Valida o arquivo de assinatura e retorna ``True`` se for válida.

    Dependendo do ambiente configurado em ``VALIDATOR_ENV`` a função utiliza o
    serviço oficial do ITI (produção) ou o verificador de conformidade da UFSC
    (homologação).
    """
    if settings.validator_env.lower() == "homologacao":
        url = "https://verificador.labsec.ufsc.br/report"
    else:
        url = "https://validar.iti.gov.br/api/validate"
    files = {"file": ("assinatura.p7s", p7s, "application/pkcs7-signature")}
    try:
        response = requests.post(url, files=files, timeout=30)
        if not response.ok:
            return False
        data = response.json()
        if settings.validator_env.lower() == "homologacao":
            return data.get("status") == "success"
        return data.get("valid", False)
    except requests.RequestException:
        return False
