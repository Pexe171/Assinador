"""Endpoints para webhooks do WhatsApp."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/webhooks/wa")


@router.post("/")
async def receive_whatsapp(request: Request) -> dict:
    """Recebe eventos do WhatsApp."""
    payload = await request.json()
    # Processamento simplificado
    return {"status": "ok", "payload": payload}
