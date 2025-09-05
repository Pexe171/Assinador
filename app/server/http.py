"""Inicialização do servidor HTTP utilizando FastAPI."""

from threading import Thread
import uvicorn
from fastapi import FastAPI

from .callbacks_govbr import router as govbr_router
from .callbacks_icpbr import router as icpbr_router
from .webhooks_wa import router as wa_router

app = FastAPI()
app.include_router(govbr_router)
app.include_router(icpbr_router)
app.include_router(wa_router)


def run_server() -> Thread:
    """Executa o servidor em uma thread separada."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    return thread
