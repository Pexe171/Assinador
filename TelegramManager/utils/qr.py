"""Utilitários para leitura de QR Codes."""

from __future__ import annotations

from pathlib import Path

import cv2


def decode_qr_image(image_path: str | Path) -> str:
    """Lê um QR Code de uma imagem retornando o conteúdo textual."""

    caminho = Path(image_path)
    if not caminho.exists():
        raise ValueError("Arquivo de imagem não encontrado.")

    imagem = cv2.imread(str(caminho))
    if imagem is None:
        raise ValueError("Não foi possível carregar a imagem informada.")

    detector = cv2.QRCodeDetector()
    dados, pontos, _ = detector.detectAndDecode(imagem)
    if not dados or pontos is None:
        raise ValueError("Nenhum QR Code foi detectado na imagem selecionada.")

    return dados.strip()
