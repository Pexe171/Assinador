"""Gerenciamento do túnel seguro (Cloudflared ou ngrok)."""

from subprocess import Popen, PIPE
from typing import Optional
import time

import requests


def start_tunnel(port: int) -> Popen:
    """Inicia o túnel e retorna o processo."""
    proc = Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=PIPE,
        stderr=PIPE,
    )
    # Aguarda alguns instantes para que o serviço local exponha a URL.
    time.sleep(2)
    return proc


def get_public_url() -> Optional[str]:
    """Obtém a URL pública do túnel, se disponível."""
    try:
        resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        data = resp.json()
        return data["tunnels"][0]["public_url"]
    except Exception:
        return None


def stop_tunnel(proc: Optional[Popen]) -> None:
    """Encerra o túnel se o processo estiver ativo."""
    if proc and proc.poll() is None:
        proc.terminate()
