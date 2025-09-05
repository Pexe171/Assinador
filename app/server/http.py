"""Inicialização do servidor HTTP utilizando FastAPI."""

from threading import Thread
import uvicorn
from fastapi import FastAPI

app = FastAPI()


def run_server() -> Thread:
    """Executa o servidor em uma thread separada."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    return thread
