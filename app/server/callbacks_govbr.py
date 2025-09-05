"""Callback de OAuth2 para GOV.BR."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/callbacks/govbr")


@router.get("/")
async def govbr_callback(code: str, state: str) -> dict:
    """Recebe o código de autorização e estado."""
    # Aqui trocaria o código por token e dispararia fluxo.
    return {"code": code, "state": state}
