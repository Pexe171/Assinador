"""Sistema de automação central da aplicação."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Callable, Dict, List

from TelegramManager.utils.async_worker import BackgroundWorker


@dataclass
class AutomationTask:
    """Representa uma tarefa de automação de grupos agendada."""

    identificador: str
    titulo: str
    grupo: str
    agendamento: datetime
    delay_min: int
    delay_max: int
    status: str = "Agendado"
    progresso: int = 0
    logs: List[str] = field(default_factory=list)


class AutomationEngine:
    """Orquestra tarefas de automação utilizando *workers* em segundo plano."""

    def __init__(self) -> None:
        self._worker = BackgroundWorker("automation-engine")
        self._tasks: Dict[str, AutomationTask] = {}
        self._lock = Lock()
        self._cache_ordenado: List[AutomationTask] = []
        self._cache_sujo = True

    def agendar(self, tarefa: AutomationTask) -> AutomationTask:
        """Registra uma nova tarefa no motor de automação."""

        with self._lock:
            self._tasks[tarefa.identificador] = tarefa
            self._cache_sujo = True
        tarefa.logs.append("Registrada no motor de automação.")
        return tarefa

    def listar(self) -> List[AutomationTask]:
        """Retorna as tarefas ordenadas pela data de execução."""

        with self._lock:
            if self._cache_sujo:
                self._cache_ordenado = sorted(
                    self._tasks.values(), key=lambda item: item.agendamento
                )
                self._cache_sujo = False
            tarefas = list(self._cache_ordenado)
        return tarefas

    def atualizar_status(
        self,
        identificador: str,
        *,
        status: str | None = None,
        progresso: int | None = None,
        mensagem: str | None = None,
    ) -> None:
        """Atualiza metadados de uma tarefa de forma segura."""

        with self._lock:
            tarefa = self._tasks.get(identificador)
        if not tarefa:
            return
        if status is not None and status != tarefa.status:
            tarefa.status = status
            self._cache_sujo = True
        if progresso is not None:
            tarefa.progresso = progresso
        if mensagem:
            tarefa.logs.append(mensagem)

    def executar_em_background(self, identificador: str, acao: Callable[[], None]) -> None:
        """Executa uma ação em *background* e atualiza o status automaticamente."""

        def _job() -> None:
            self.atualizar_status(
                identificador,
                status="Em andamento",
                mensagem="Execução iniciada pelo motor de automação.",
            )
            try:
                acao()
            except Exception as exc:  # pragma: no cover - tratamento defensivo
                self.atualizar_status(
                    identificador,
                    status="Falhou",
                    mensagem=f"Erro durante a automação: {exc}",
                )
            else:
                # Simula conclusão imediata quando não há lógica real.
                self.atualizar_status(
                    identificador,
                    status="Concluído",
                    progresso=100,
                    mensagem="Automação concluída com sucesso.",
                )
            finally:
                time.sleep(0.05)

        self._worker.submit(_job)

    def remover(self, identificador: str) -> None:
        """Remove uma tarefa agendada."""

        with self._lock:
            removida = self._tasks.pop(identificador, None)
            if removida is not None:
                self._cache_sujo = True

    def shutdown(self) -> None:
        """Encerra o *worker* interno com segurança."""

        self._worker.stop()

    def __del__(self) -> None:  # pragma: no cover - garantia em GC
        try:
            self.shutdown()
        except Exception:
            pass
