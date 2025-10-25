"""Diálogo modal para autenticação de contas via QR Code."""

from __future__ import annotations

from threading import Event

import qrcode
from PyQt6.QtCore import QObject, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.authentication import (
    AuthenticationCancelledError,
    AuthenticationError,
    AuthenticationService,
)
from TelegramManager.core.container import Container
from TelegramManager.core.session_manager import SessionInfo


class _QrLoginWorker(QObject):
    """Executa o fluxo de autenticação em *thread* dedicada."""

    qr_code_generated = pyqtSignal(str)
    state_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    completed = pyqtSignal(object)

    def __init__(self, service: AuthenticationService, cancel_event: Event) -> None:
        super().__init__()
        self._service = service
        self._cancel_event = cancel_event

    @pyqtSlot()
    def run(self) -> None:
        try:
            session = self._service.authenticate_with_qr(
                self.qr_code_generated.emit,
                on_state=self.state_changed.emit,
                cancel_event=self._cancel_event,
            )
            if not self._cancel_event.is_set():
                self.completed.emit(session)
        except AuthenticationCancelledError:
            # Cancelamento silencioso
            pass
        except AuthenticationError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:  # pragma: no cover - última linha de defesa
            self.error_occurred.emit(str(exc))


class QrLoginDialog(QDialog):
    """Janela modal que apresenta o QR Code e estados da autenticação."""

    login_completed = pyqtSignal(object)

    def __init__(self, *, container: Container, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Autenticar conta com QR Code")
        self.setModal(True)
        self.resize(420, 520)

        self._service = container.authentication_service
        self._cancel_event = Event()
        self._thread: QThread | None = QThread(self)
        self._worker = _QrLoginWorker(self._service, self._cancel_event)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)

        self._worker.qr_code_generated.connect(self._atualizar_qr)
        self._worker.state_changed.connect(self._atualizar_status)
        self._worker.error_occurred.connect(self._tratar_erro)
        self._worker.completed.connect(self._finalizar_com_sucesso)
        self._worker.error_occurred.connect(self._encerrar_thread)
        self._worker.completed.connect(self._encerrar_thread)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)

        self._montar_interface()
        self._thread.start()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titulo = QLabel("Escaneie o QR Code abaixo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(titulo)

        descricao = QLabel(
            "Abra o Telegram no celular, acesse Configurações > Dispositivos > "
            "Conectar Dispositivo e escaneie o QR Code."
        )
        descricao.setWordWrap(True)
        descricao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        descricao.setStyleSheet("color: #94a3b8;")
        layout.addWidget(descricao)

        self._qr_label = QLabel()
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setStyleSheet(
            "background-color: #0f172a; border-radius: 12px; padding: 16px;"
        )
        layout.addWidget(self._qr_label, stretch=1)

        self._status_label = QLabel("Preparando ambiente...")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("color: #38bdf8; font-weight: 500;")
        layout.addWidget(self._status_label)

        botoes = QHBoxLayout()
        botoes.addStretch()
        self._botao_cancelar = QPushButton("Cancelar")
        self._botao_cancelar.clicked.connect(self.reject)
        botoes.addWidget(self._botao_cancelar)
        layout.addLayout(botoes)

    def _encerrar_thread(self) -> None:
        if self._thread is None:
            return

        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)

    def _on_thread_finished(self) -> None:
        self._thread = None

    def reject(self) -> None:  # type: ignore[override]
        self._cancel_event.set()
        super().reject()
        self._encerrar_thread()

    def accept(self) -> None:  # type: ignore[override]
        super().accept()
        self._encerrar_thread()

    @pyqtSlot(str)
    def _atualizar_qr(self, url: str) -> None:
        imagem = self._gerar_qr(url)
        if imagem is not None:
            self._qr_label.setPixmap(imagem)

    @pyqtSlot(str)
    def _atualizar_status(self, mensagem: str) -> None:
        self._status_label.setText(mensagem)

    @pyqtSlot(object)
    def _finalizar_com_sucesso(self, session: SessionInfo) -> None:
        self.login_completed.emit(session)
        self._status_label.setText("Conta autenticada com sucesso!")
        self._botao_cancelar.setText("Fechar")
        self._botao_cancelar.setEnabled(True)
        QTimer.singleShot(600, self.accept)

    @pyqtSlot(str)
    def _tratar_erro(self, mensagem: str) -> None:
        self._status_label.setText("Não foi possível autenticar.")
        QMessageBox.warning(self, "Autenticação", mensagem)
        self._botao_cancelar.setText("Fechar")
        self._botao_cancelar.setEnabled(True)

    def _gerar_qr(self, url: str) -> QPixmap | None:
        try:
            qr = qrcode.QRCode(version=None, box_size=8, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            imagem = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            dados = imagem.tobytes("raw", "RGB")
            qimage = QImage(dados, imagem.width, imagem.height, QImage.Format.Format_RGB888)
            return QPixmap.fromImage(qimage).scaled(
                280,
                280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        except Exception:
            return None
