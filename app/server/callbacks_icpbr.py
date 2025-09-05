"""Callback para resultados de assinatura ICP-Brasil."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/callbacks/icpbr")


@router.post("/")
async def icpbr_callback(request: Request) -> dict:
    """Recebe notificações do serviço de assinatura."""
    payload = await request.json()
    return {"status": "ok", "payload": payload}
