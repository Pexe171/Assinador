"""Executores em *thread* para tarefas de longa duração."""

from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Task:
    func: Callable[[], None]


class BackgroundWorker:
    """Fila de tarefas simples com processamento em *thread* dedicada."""

    def __init__(self, nome: str) -> None:
        self._nome = nome
        self._fila: "queue.Queue[Task]" = queue.Queue()
        self._thread = threading.Thread(target=self._loop, name=nome, daemon=True)
        self._ativo = True
        self._thread.start()

    def submit(self, func: Callable[[], None]) -> None:
        self._fila.put(Task(func=func))

    def _loop(self) -> None:
        logger.info("Worker %s iniciado", self._nome)
        while self._ativo:
            try:
                tarefa = self._fila.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                tarefa.func()
            except Exception as exc:  # pragma: no cover - logging defensivo
                logger.exception("Erro ao executar tarefa no worker %s", self._nome)
            finally:
                self._fila.task_done()

    def stop(self) -> None:
        self._ativo = False
        self._thread.join(timeout=1)
        logger.info("Worker %s finalizado", self._nome)
