"""Testes para o webhook do WhatsApp."""

import os
import json
import hmac
import hashlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Garante que o pacote `app` esteja no caminho
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Configura variáveis antes de importar a aplicação
os.environ["WA_VERIFY_TOKEN"] = "secreto"
os.environ["WA_APP_SECRET"] = "appsecret"

from app.server.http import app  # noqa: E402
from app.core.models import Base, Conversation, AuditLog  # noqa: E402
from app.core.db import engine, SessionLocal  # noqa: E402


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_verify_token() -> None:
    client = TestClient(app)
    resp = client.get(
        "/webhooks/wa",
        params={"hub.verify_token": "secreto", "hub.challenge": "42"},
    )
    assert resp.status_code == 200
    assert resp.text == "42"


def test_receive_message_and_status() -> None:
    client = TestClient(app)

    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [{"from": "123"}],
                            "statuses": [
                                {"recipient_id": "123", "status": "form_enviado"}
                            ],
                        }
                    }
                ]
            }
        ]
    }

    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(
        b"appsecret", body, hashlib.sha256
    ).hexdigest()

    resp = client.post(
        "/webhooks/wa", data=body, headers={"X-Hub-Signature-256": signature}
    )
    assert resp.status_code == 200

    session = SessionLocal()
    conv = session.query(Conversation).filter_by(wa_id="123").first()
    assert conv is not None and conv.status == "form_enviado"
    log = session.query(AuditLog).first()
    assert log is not None and log.actor == "wa_webhook"
    session.close()

