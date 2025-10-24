# Caminho: TelegramManager/core/automation.py
"""Sistema de automação central da aplicação."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Callable, Dict, List

from TelegramManager.utils.async_worker import BackgroundWorker


class TaskStatus(str, Enum):
    """Define os estados possíveis de uma tarefa."""

    SCHEDULED = "Agendado"
    RUNNING = "Em andamento"
    COMPLETED = "Concluído"
    FAILED = "Falhou"
    PAUSED = "Pausado"


@dataclass
class AutomationTask:
    """Representa uma tarefa de automação de grupos agendada."""

    identificador: str
    titulo: str
    grupo: str
    agendamento: datetime
    delay_min: int
    delay_max: int
    status: TaskStatus = TaskStatus.SCHEDULED
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
        status: TaskStatus | None = None,
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
            tarefa.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {mensagem}")

    def executar_em_background(self, identificador: str, acao: Callable[[], None]) -> None:
        """Executa uma ação em *background* e atualiza o status automaticamente."""

        def _job() -> None:
            # Em um cenário real de automação, esta função (executar_em_background)
            # não deveria controlar o status. O chamador (ex: AdditionManager)
            # é quem deve atualizar o status via 'atualizar_status' ou
            # manipulando seu próprio monitor.
            #
            # No entanto, para tarefas simples do 'AutomationWidget', mantemos este
            # wrapper básico.
            #
            # A lógica do 'AdditionManager' é mais complexa e usa este worker
            # apenas para obter o thread, mas controla o estado externamente.
            if "addition-job-" not in identificador:
                self.atualizar_status(
                    identificador,
                    status=TaskStatus.RUNNING,
                    mensagem="Execução iniciada pelo motor de automação.",
                )
            try:
                acao()
            except Exception as exc:  # pragma: no cover - tratamento defensivo
                if "addition-job-" not in identificador:
                    self.atualizar_status(
                        identificador,
                        status=TaskStatus.FAILED,
                        mensagem=f"Erro durante a automação: {exc}",
                    )
            else:
                if "addition-job-" not in identificador:
                    # Simula conclusão imediata quando não há lógica real.
                    self.atualizar_status(
                        identificador,
                        status=TaskStatus.COMPLETED,
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

