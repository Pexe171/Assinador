"""Endpoints para webhooks do WhatsApp."""

import json
import hmac
import hashlib
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.config import load_settings
from app.core.db import get_session
from app.core.models import Conversation, AuditLog


router = APIRouter(prefix="/webhooks/wa")

settings = load_settings()


def _first(iterable: Iterable):
    return next(iter(iterable), None)


@router.get("/")
async def verify_whatsapp(request: Request) -> Response:
    """Valida o token de verificação do WhatsApp."""
    params = request.query_params
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge", "")
    if token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=403, detail="Token inválido")
    return Response(content=challenge)


@router.post("/")
async def receive_whatsapp(
    request: Request, session: Session = Depends(get_session)
) -> dict:
    """Recebe eventos do WhatsApp e atualiza conversas."""

    body = await request.body()

    # Validação da assinatura do webhook
    app_secret = settings.whatsapp_app_secret
    signature = request.headers.get("X-Hub-Signature-256")
    if app_secret and signature:
        expected = "sha256=" + hmac.new(
            app_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=403, detail="Assinatura inválida")

    payload = json.loads(body or b"{}").copy()

    # Registra evento de auditoria
    session.add(
        AuditLog(
            actor="wa_webhook", action="receive", payload=json.dumps(payload)
        )
    )

    allowed_statuses = {
        "novo",
        "engajado",
        "form_enviado",
        "assinado",
        "validado",
        "erro",
    }

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                wa_id = message.get("from")
                conv = _first(
                    session.query(Conversation).filter_by(wa_id=wa_id).all()
                )
                if not conv:
                    conv = Conversation(wa_id=wa_id, status="novo")
                    session.add(conv)
                    session.flush()
                conv.status = "engajado"
            for status in value.get("statuses", []):
                wa_id = status.get("recipient_id")
                new_status = status.get("status")
                session.flush()
                conv = _first(
                    session.query(Conversation).filter_by(wa_id=wa_id).all()
                )
                if not conv:
                    conv = Conversation(wa_id=wa_id, status="novo")
                    session.add(conv)
                if new_status in allowed_statuses:
                    conv.status = new_status
                else:
                    conv.status = "erro"

    session.commit()
    return {"status": "ok"}

