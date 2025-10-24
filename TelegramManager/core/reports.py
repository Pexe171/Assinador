"""Serviços de relatórios e indicadores da aplicação."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean
from typing import Dict, Iterable, List, Tuple

from TelegramManager.core.automation import AutomationEngine, AutomationTask
from TelegramManager.core.extraction import ExtractionService


@dataclass(frozen=True)
class AutomationSummary:
    """Consolida estatísticas básicas do módulo de automação."""

    total: int
    agendadas: int
    em_andamento: int
    concluidas: int
    falhas: int
    progresso_medio: float
    proxima_execucao: datetime | None


@dataclass(frozen=True)
class DailyAutomationActivity:
    """Representa a quantidade de execuções concluídas por dia."""

    dia: datetime
    concluidas: int


class ReportService:
    """Gera relatórios básicos combinando dados de automação e extrações."""

    def __init__(
        self,
        *,
        automation_engine: AutomationEngine,
        extraction_service: ExtractionService,
    ) -> None:
        self._automation_engine = automation_engine
        self._extraction_service = extraction_service

    def gerar_resumo_automacao(self) -> AutomationSummary:
        """Calcula indicadores principais das tarefas de automação."""

        tarefas = self._automation_engine.listar()
        total = len(tarefas)
        agendadas = sum(1 for tarefa in tarefas if tarefa.status == "Agendado")
        em_andamento = sum(1 for tarefa in tarefas if tarefa.status == "Em andamento")
        concluidas = sum(1 for tarefa in tarefas if tarefa.status == "Concluído")
        falhas = sum(1 for tarefa in tarefas if tarefa.status == "Falhou")
        progresso_medio = (
            round(mean(tarefa.progresso for tarefa in tarefas), 2) if tarefas else 0.0
        )
        proxima_execucao = self._proxima_execucao(tarefas)

        return AutomationSummary(
            total=total,
            agendadas=agendadas,
            em_andamento=em_andamento,
            concluidas=concluidas,
            falhas=falhas,
            progresso_medio=progresso_medio,
            proxima_execucao=proxima_execucao,
        )

    def gerar_atividade_diaria(self) -> List[DailyAutomationActivity]:
        """Agrupa tarefas concluídas por data para alimentar gráficos simples."""

        tarefas = self._automation_engine.listar()
        contagem: Dict[str, Tuple[datetime, int]] = {}
        for tarefa in tarefas:
            if tarefa.status != "Concluído":
                continue
            chave = tarefa.agendamento.strftime("%Y-%m-%d")
            agregado = contagem.get(chave)
            if not agregado:
                contagem[chave] = (tarefa.agendamento, 1)
            else:
                contagem[chave] = (agregado[0], agregado[1] + 1)

        atividades = [
            DailyAutomationActivity(dia=valor[0], concluidas=valor[1])
            for valor in contagem.values()
        ]
        atividades.sort(key=lambda item: item.dia)
        return atividades

    def gerar_overview_extracao(self) -> Dict[str, int]:
        """Retorna métricas básicas sobre extrações já executadas."""

        overview = self._extraction_service.overview()
        return {
            "usuarios": overview.total_users,
            "grupos": overview.total_groups,
        }

    @staticmethod
    def _proxima_execucao(tarefas: Iterable[AutomationTask]) -> datetime | None:
        proximas = [
            tarefa.agendamento
            for tarefa in tarefas
            if tarefa.status == "Agendado"
        ]
        return min(proximas) if proximas else None
