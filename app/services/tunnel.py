"""Gerenciamento do túnel seguro (Cloudflared ou ngrok)."""

from subprocess import Popen
from typing import Optional


def start_tunnel(port: int) -> Popen:
    """Inicia o túnel e retorna o processo."""
    # Implementação simplificada; em produção escolheria provider.
    return Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{port}"])


def stop_tunnel(proc: Optional[Popen]) -> None:
    """Encerra o túnel se o processo estiver ativo."""
    if proc and proc.poll() is None:
        proc.terminate()
