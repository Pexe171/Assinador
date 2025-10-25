# Caminho: TelegramManager/ui/widgets/accounts_manager.py
"""Widget para gestão visual de contas Telegram com estilo moderno."""

from __future__ import annotations

from datetime import datetime
import logging # Adicionado para logging
from dataclasses import dataclass, field
from typing import Callable, Dict

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap # QColor adicionado
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame, # Adicionado QFrame
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy, # Adicionado QSizePolicy
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.container import Container
from TelegramManager.core.session_manager import SessionInfo
from TelegramManager.notifications.dispatcher import NotificationDispatcher
from TelegramManager.ui.widgets.session_form import SessionFormWidget

logger = logging.getLogger(__name__)


@dataclass
class AccountData:
    """Mantém as preferências e histórico de cada conta."""

    info: SessionInfo
    notificacoes: bool = True
    logs: list[str] = field(default_factory=list)


class AccountsManagerWidget(QWidget):
    """Apresenta a lista de contas com opções de organização e detalhes."""

    # Sinal emitido quando contas são adicionadas ou modificadas
    account_changed = pyqtSignal()

    def __init__(
        self,
        container: Container,
        notifications: NotificationDispatcher,
    ) -> None:
        super().__init__()
        self._container = container
        self._notifications = notifications
        self._contas: Dict[str, AccountData] = {}

        self._montar_layout()
        self._aplicar_estilos() # Centraliza estilos
        self._carregar_sessoes()

    def _montar_layout(self) -> None:
        """Monta a estrutura principal com painel esquerdo e direito (splitter)."""
        layout = QHBoxLayout(self)
        # Margens maiores para dar respiro
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25) # Espaço entre painel esquerdo e splitter

        # --- Painel Esquerdo (Título, Descrição, Formulário) ---
        painel_esquerdo = QWidget()
        layout_esquerdo = QVBoxLayout(painel_esquerdo)
        layout_esquerdo.setContentsMargins(0, 0, 0, 0) # Remove margens internas
        layout_esquerdo.setSpacing(20) # Espaço entre título, descrição e form

        titulo = QLabel("Gerenciar Contas Telegram")
        titulo.setObjectName("viewTitle") # ID para estilo
        layout_esquerdo.addWidget(titulo)

        descricao = QLabel(
            "Adicione novas contas do Telegram usando o formulário abaixo. "
            "Selecione uma conta na lista à direita para ver detalhes e logs."
        )
        descricao.setObjectName("viewDescription") # ID para estilo
        descricao.setWordWrap(True)
        layout_esquerdo.addWidget(descricao)

        # Formulário dentro de um QFrame estilizado
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout_wrapper = QVBoxLayout(form_frame) # Layout para o frame
        form_layout_wrapper.setContentsMargins(20, 20, 20, 20) # Padding interno

        self._form = SessionFormWidget(
            container=self._container,
            on_create=self._registrar_sessao,
        )
        form_layout_wrapper.addWidget(self._form)
        layout_esquerdo.addWidget(form_frame)

        layout_esquerdo.addStretch() # Empurra o formulário para cima
        layout.addWidget(painel_esquerdo, stretch=1) # Painel esquerdo ocupa 1/3

        # --- Painel Direito (Splitter com Lista e Detalhes) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("accountSplitter")

        # Lista de Contas (dentro de um QFrame)
        lista_frame = QFrame()
        lista_frame.setObjectName("listFrame")
        layout_lista = QVBoxLayout(lista_frame)
        layout_lista.setContentsMargins(0,0,0,0) # Sem margem interna no frame da lista
        titulo_lista = QLabel("Contas Conectadas")
        titulo_lista.setObjectName("listTitle")
        layout_lista.addWidget(titulo_lista)

        self._lista = QListWidget()
        self._lista.setObjectName("accountList") # ID para estilo
        self._lista.setAlternatingRowColors(False) # Desativa zebrado padrão, faremos no CSS
        self._lista.setDragEnabled(True)
        self._lista.setAcceptDrops(True)
        self._lista.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._lista.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._lista.itemSelectionChanged.connect(self._atualizar_detalhes)
        layout_lista.addWidget(self._lista)
        splitter.addWidget(lista_frame)

        # Painel de Detalhes (dentro de um QFrame)
        detalhes_frame = QFrame()
        detalhes_frame.setObjectName("detailsFrame")
        layout_detalhes_wrapper = QVBoxLayout(detalhes_frame) # Layout para o frame
        layout_detalhes_wrapper.setContentsMargins(20, 20, 20, 20) # Padding interno
        self._painel_detalhes = self._criar_painel_detalhes() # Cria o conteúdo interno
        layout_detalhes_wrapper.addWidget(self._painel_detalhes)
        splitter.addWidget(detalhes_frame)

        # Configura tamanhos iniciais do splitter
        splitter.setSizes([250, 500]) # Lista menor, Detalhes maior
        splitter.setStretchFactor(1, 2) # Detalhes cresce mais

        layout.addWidget(splitter, stretch=2) # Splitter ocupa 2/3

    def _aplicar_estilos(self) -> None:
        """Aplica a folha de estilos (Stylesheet) para a aparência."""
        self.setStyleSheet("""
            AccountsManagerWidget {
                background-color: transparent;
            }
            QWidget {
                color: #e2e8f0;
            }

            /* Títulos e Descrições Gerais da View */
            QLabel#viewTitle {
                font-size: 24px;
                font-weight: 600;
                color: #f8fafc;
                padding-bottom: 5px;
            }
            QLabel#viewDescription {
                font-size: 14px;
                color: #94a3b8;
                padding-bottom: 10px;
            }

            /* Frame do Formulário */
            QFrame#formFrame {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 14px;
            }

            /* Estilos dentro do SessionFormWidget */
            SessionFormWidget QLineEdit {
                padding: 10px 14px;
                border: 1px solid #1e293b;
                border-radius: 8px;
                font-size: 14px;
                background-color: #0b1220;
                color: #f1f5f9;
                selection-background-color: #38bdf8;
                selection-color: #0f172a;
            }
            SessionFormWidget QLineEdit:focus {
                border: 1px solid #38bdf8;
            }
            SessionFormWidget QPushButton {
                padding: 12px 16px;
                background-color: #f8fafc;
                color: #0f172a;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                margin-top: 12px;
            }
            SessionFormWidget QPushButton:hover {
                background-color: #e2e8f0;
            }
            SessionFormWidget QLabel#qrHelperLabel {
                margin-top: 16px;
                font-size: 12px;
                color: #94a3b8;
            }

            /* Frame da Lista */
            QFrame#listFrame {
                 background-color: #111827;
                 border: 1px solid #1f2937;
                 border-radius: 14px;
                 padding: 18px;
            }
             QLabel#listTitle {
                font-size: 16px;
                font-weight: 600;
                color: #f1f5f9;
                padding-bottom: 12px;
                margin-left: 6px;
             }

            /* Lista de Contas */
            QListWidget#accountList {
                border: none;
                outline: 0px;
                background-color: transparent;
            }
            QListWidget#accountList::item {
                padding: 12px 16px;
                border-radius: 10px;
                margin: 4px 0px;
                background-color: #111827;
                color: #cbd5f5;
            }
             QListWidget#accountList::item:hover {
                background-color: #1e293b;
                color: #f8fafc;
            }
            QListWidget#accountList::item:selected {
                background-color: #38bdf8;
                color: #0f172a;
                font-weight: 600;
                border-left: 3px solid #f8fafc;
                padding-left: 13px;
            }
            QListWidget#accountList::item:focus {
                outline: none;
                border: none;
            }


            /* Frame de Detalhes */
            QFrame#detailsFrame {
                 background-color: #111827;
                 border: 1px solid #1f2937;
                 border-radius: 14px;
            }

            /* Conteúdo do Painel de Detalhes */
            #detailsPanel QLabel#detailTitle {
                font-size: 20px;
                font-weight: 600;
                color: #f8fafc;
                padding-bottom: 15px;
            }
            #detailsPanel QGroupBox {
                border: 1px solid #1e293b;
                border-radius: 10px;
                margin-top: 18px;
                padding: 18px;
                background-color: #0f172a;
            }
            #detailsPanel QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px 6px 6px;
                color: #94a3b8;
                font-weight: 500;
            }
            #detailsPanel QFormLayout QLabel {
                color: #94a3b8;
                padding-top: 3px;
            }
             #detailsPanel QFormLayout QLabel#detailValueLabel {
                font-weight: 600;
                color: #f8fafc;
            }
            #detailsPanel QPushButton {
                padding: 10px 14px;
                background-color: #f8fafc;
                color: #0f172a;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
             #detailsPanel QPushButton:hover {
                 background-color: #e2e8f0;
             }
             #detailsPanel QPlainTextEdit {
                 background-color: #0b1220;
                 color: #e2e8f0;
                 font-family: "Consolas", "Courier New", monospace;
                 font-size: 13px;
                 border: 1px solid #1e293b;
                 border-radius: 10px;
                 padding: 12px;
             }
        """)

    def _criar_painel_detalhes(self) -> QWidget:
        """Cria o conteúdo do painel direito (detalhes da conta selecionada)."""
        painel = QWidget()
        painel.setObjectName("detailsPanel") # ID para estilo
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(0,0,0,0) # Sem margens internas no widget base
        painel_layout.setSpacing(15)

        self._titulo_detalhe = QLabel("Selecione uma conta")
        self._titulo_detalhe.setObjectName("detailTitle")
        painel_layout.addWidget(self._titulo_detalhe)

        # Grupo de Informações Básicas
        grupo_info = QGroupBox("Informações")
        form_info = QFormLayout(grupo_info)
        form_info.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_info.setHorizontalSpacing(15) # Espaço entre label e valor

        self._label_telefone = QLabel("-")
        self._label_telefone.setObjectName("detailValueLabel")
        form_info.addRow("Telefone:", self._label_telefone)

        self._label_status = QLabel("-")
        self._label_status.setObjectName("detailValueLabel")
        form_info.addRow("Status:", self._label_status)

        self._botao_teste = QPushButton("Testar Conexão")
        self._botao_teste.setToolTip("Verifica se a sessão está ativa (simulado)")
        self._botao_teste.clicked.connect(self._testar_conexao)
        self._botao_teste.setEnabled(False)
        form_info.addRow("Rede:", self._botao_teste)
        painel_layout.addWidget(grupo_info)

        # Grupo de Logs
        grupo_logs = QGroupBox("Logs da Sessão")
        logs_layout = QVBoxLayout(grupo_logs)
        logs_layout.setContentsMargins(5, 5, 5, 5) # Margens internas menores
        self._logs = QPlainTextEdit()
        self._logs.setReadOnly(True)
        logs_layout.addWidget(self._logs)
        painel_layout.addWidget(grupo_logs, stretch=1) # Logs ocupam espaço restante

        return painel

    def _carregar_sessoes(self) -> None:
        """Carrega sessões do backend e popula a lista."""
        logger.debug("Carregando sessões para a lista...")
        self._lista.clear() # Limpa a lista antes de recarregar
        self._contas.clear() # Limpa o dicionário de dados
        try:
            self._container.session_manager.load_persisted_sessions()
            sessoes = self._container.session_manager.sessions
            for info in sessoes.values():
                # Passa notificar=False para evitar múltiplas notificações na carga inicial
                self._registrar_sessao(info, notificar=False)
            logger.info("%d sessões carregadas na interface.", len(sessoes))
            # Seleciona o primeiro item se houver algum
            if self._lista.count() > 0:
                self._lista.setCurrentRow(0)
            else:
                self._atualizar_detalhes() # Limpa painel de detalhes se não houver contas
        except Exception as e:
            logger.exception("Erro ao carregar sessões na interface")
            self._notifications.notify("Erro", f"Não foi possível carregar as contas: {e}")

    def _gerar_avatar_placeholder(self, status: str) -> QPixmap:
        """Gera um QPixmap simples indicando o status."""
        size = 48
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent) # Fundo transparente

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define cor baseada no status
        if status.lower() == "online":
            color = QColor("#4ade80") # Verde
            border_color = QColor("#22c55e")
        elif status.lower() == "conectando":
            color = QColor("#facc15") # Amarelo
            border_color = QColor("#eab308")
        else: # Offline ou erro
            color = QColor("#cbd5e0") # Cinza
            border_color = QColor("#94a3b8")

        # Desenha círculo com borda
        pen = painter.pen()
        pen.setWidth(2)
        pen.setColor(border_color)
        painter.setPen(pen)
        painter.setBrush(color)
        # Ajusta retângulo para caber a borda
        rect = pixmap.rect().adjusted(1, 1, -1, -1)
        painter.drawEllipse(rect)

        painter.end()
        return pixmap

    def _registrar_sessao(self, session: SessionInfo, notificar: bool = True) -> None:
        """Adiciona ou atualiza um item na lista de contas."""
        try:
            phone = session.phone
            display_name = session.display_name
            status = session.status

            # Gera um avatar placeholder baseado no status
            avatar_pixmap = self._gerar_avatar_placeholder(status)
            avatar_icon = QIcon(avatar_pixmap)

            existente = self._buscar_item(phone)
            if existente is None:
                logger.debug("Adicionando nova conta à lista: %s", phone)
                # Formata texto com nome maior e telefone menor
                item_text = f"{display_name}\n<span style='color: #718096; font-size: 11px;'>{phone}</span>"
                item = QListWidgetItem(avatar_icon, "") # Texto será HTML
                # Define texto como RichText para formatar
                label_item = QLabel(item_text)
                label_item.setTextFormat(Qt.TextFormat.RichText)
                label_item.setStyleSheet("background-color: transparent;") # Evita fundo branco no label
                self._lista.addItem(item)
                self._lista.setItemWidget(item, label_item) # Usa QLabel para renderizar HTML

                item.setData(Qt.ItemDataRole.UserRole, phone)
                item.setSizeHint(QSize(200, 60)) # Ajusta altura do item

                dados = AccountData(info=session)
                dados.logs.append(f"[{datetime.now():%H:%M:%S}] Conta conectada.")
                self._contas[phone] = dados
                if notificar:
                    self._notifications.notify(
                        titulo="Conta Adicionada",
                        mensagem=f"A conta {display_name} foi registrada.",
                    )
            else:
                logger.debug("Atualizando conta existente na lista: %s", phone)
                existente.setIcon(avatar_icon) # Atualiza ícone/status
                # Atualiza texto no QLabel associado
                label_widget = self._lista.itemWidget(existente)
                if isinstance(label_widget, QLabel):
                    label_widget.setText(f"{display_name}\n<span style='color: #718096; font-size: 11px;'>{phone}</span>")

                # Atualiza dados internos
                dados = self._contas[phone]
                dados.info = session # Atualiza SessionInfo
                dados.logs.append(f"[{datetime.now():%H:%M:%S}] Status atualizado: {status}")

            # Se esta for a conta atualmente selecionada, atualiza os detalhes
            if self._lista.currentItem() == existente or (existente is None and self._lista.count() == 1):
                 self._atualizar_detalhes()

            self.account_changed.emit() # Notifica que a lista mudou

        except Exception as e:
            logger.exception("Erro ao registrar/atualizar sessão na UI: %s", session.phone)
            self._notifications.notify("Erro Interface", f"Falha ao exibir conta {session.phone}: {e}")

    def _obter_conta_selecionada(self) -> AccountData | None:
        """Retorna os dados da conta atualmente selecionada na lista."""
        item = self._lista.currentItem()
        if not item:
            return None
        phone = item.data(Qt.ItemDataRole.UserRole)
        return self._contas.get(phone)

    def _buscar_item(self, phone: str) -> QListWidgetItem | None:
        """Encontra um item na lista pelo número de telefone."""
        for indice in range(self._lista.count()):
            item = self._lista.item(indice)
            if item.data(Qt.ItemDataRole.UserRole) == phone:
                return item
        return None

    def _atualizar_detalhes(self) -> None:
        """Atualiza o painel de detalhes com base na conta selecionada."""
        conta = self._obter_conta_selecionada()
        logger.debug("Atualizando painel de detalhes para: %s", conta.info.phone if conta else "Nenhum")

        if not conta:
            self._titulo_detalhe.setText("Selecione uma conta na lista")
            self._label_telefone.setText("-")
            self._label_status.setText("-")
            self._logs.clear()
            self._botao_teste.setEnabled(False)
            return

        self._titulo_detalhe.setText(conta.info.display_name)
        self._label_telefone.setText(conta.info.phone)
        self._label_status.setText(conta.info.status.capitalize()) # Capitaliza status
        # Estiliza o status
        if conta.info.status.lower() == "online":
             self._label_status.setStyleSheet("color: #22c55e; font-weight: 500;") # Verde
        elif conta.info.status.lower() == "conectando":
             self._label_status.setStyleSheet("color: #eab308; font-weight: 500;") # Amarelo
        else:
            self._label_status.setStyleSheet("color: #718096; font-weight: normal;") # Cinza

        # Exibe logs mais recentes primeiro
        self._logs.setPlainText("\n".join(reversed(conta.logs)))
        self._botao_teste.setEnabled(True)

    def _testar_conexao(self) -> None:
        """Simula um teste de conexão e adiciona ao log."""
        conta = self._obter_conta_selecionada()
        if not conta:
            return
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg_ok = f"[{timestamp}] Teste de conexão: OK (Simulado)"
        log_msg_fail = f"[{timestamp}] Teste de conexão: Falhou (Simulado)"

        # Simula sucesso ou falha
        sucesso = True # Pode adicionar lógica aleatória: import random; sucesso = random.choice([True, False])
        if sucesso:
            conta.logs.append(log_msg_ok)
            # Atualiza status na UI e backend (simulação)
            conta.info.status = "online"
            self._container.session_manager.update_status(conta.info.phone, "online")
            self._registrar_toast(f"Conexão com {conta.info.display_name} OK.")
        else:
             conta.logs.append(log_msg_fail)
             conta.info.status = "offline"
             self._container.session_manager.update_status(conta.info.phone, "offline")
             self._registrar_toast(f"Falha na conexão com {conta.info.display_name}.")

        # Atualiza a lista (para refletir status no ícone) e os detalhes
        item = self._buscar_item(conta.info.phone)
        if item:
             # Atualiza ícone e texto (pode ser otimizado)
             self._registrar_sessao(conta.info, notificar=False) # Re-registra para atualizar tudo

        self._atualizar_detalhes() # Garante que logs e status no painel estão atualizados

    def _registrar_toast(self, mensagem: str) -> None:
        """Envia uma notificação."""
        self._notifications.notify(titulo="Status da Conta", mensagem=mensagem)

