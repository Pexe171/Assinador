"""Módulo de Adição de Usuários (GerenciadorAdicoes).

Implementa a lógica de negócios para adicionar usuários do banco local
a grupos de destino, com controle de delays, limites e relatórios.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List

from sqlalchemy import func, select

from TelegramManager.core.automation import AutomationEngine, TaskStatus
from TelegramManager.core.database import Database
from TelegramManager.core.session_manager import SessionInfo
from TelegramManager.core.telegram_client import TelegramClientPool
from TelegramManager.storage import Account, AddedUserLog, AdditionJob, ExtractedUser
from TelegramManager.utils.helpers import gerar_identificador

logger = logging.getLogger(__name__)


class AdditionErrorReason(str, Enum):
    """Tipos de erros tratados durante a adição."""

    USER_ALREADY_IN_GROUP = "Usuário já está no grupo"
    USER_BLOCKED_ADDITIONS = "Usuário bloqueou adições"
    GROUP_LIMIT_REACHED = "Limite de grupo atingido"
    PRIVACY_RESTRICTIONS = "Restrições de privacidade"
    TELEGRAM_API_LIMIT = "Limites da API do Telegram (Flood)"
    CONNECTION_ERROR = "Problemas de conexão"
    UNKNOWN_ERROR = "Erro desconhecido"


@dataclass
class AdditionJobConfig:
    """Configurações de segurança e operação para um Job de Adição."""

    account_phone: str
    target_group: str
    user_ids: List[int]
    delay_min: int = 30
    delay_max: int = 120
    max_add_per_day: int = 200
    stop_on_consecutive_errors: int = 5
    status: TaskStatus = TaskStatus.SCHEDULED


@dataclass
class AdditionJobMonitor:
    """Dados de monitoramento em tempo real para a UI."""

    job_id: int
    status: TaskStatus
    progress: int = 0
    total_users: int = 0
    success_count: int = 0
    fail_count: int = 0
    logs: List[str] = field(default_factory=list)
    current_user: str | None = None
    next_add_in_seconds: int = 0


@dataclass(frozen=True)
class AdditionOverview:
    """Resumo agregado das operações de adição executadas."""

    total_jobs: int
    total_success: int
    total_fail: int
    success_rate: float


class AdditionManager:
    """Gerencia o ciclo de vida das operações de adição de usuários."""

    def __init__(
        self,
        database: Database,
        pool: TelegramClientPool,
        engine: AutomationEngine,
    ) -> None:
        self._db = database
        self._pool = pool
        self._engine = engine  # Usamos o worker do engine
        self._active_jobs: Dict[int, AdditionJobMonitor] = {}

    def get_job_monitor(self, job_id: int) -> AdditionJobMonitor | None:
        """Retorna o monitor de um job ativo."""
        return self._active_jobs.get(job_id)

    def list_recent_jobs(self, limit: int = 50) -> List[AdditionJob]:
        """Lista os jobs de adição mais recentes do banco."""
        with self._db.session() as session:
            stmt = select(AdditionJob).order_by(AdditionJob.created_at.desc()).limit(limit)
            return list(session.scalars(stmt).all())

    def overview(self) -> AdditionOverview:
        """Calcula estatísticas consolidadas das adições já registradas."""

        with self._db.session() as session:
            total_jobs, total_success, total_fail = session.execute(
                select(
                    func.count(AdditionJob.id),
                    func.sum(AdditionJob.success_count),
                    func.sum(AdditionJob.fail_count),
                )
            ).one()

        total_jobs = int(total_jobs or 0)
        total_success = int(total_success or 0)
        total_fail = int(total_fail or 0)
        total_operacoes = total_success + total_fail
        taxa_sucesso = (
            (total_success / total_operacoes) * 100 if total_operacoes else 0.0
        )

        return AdditionOverview(
            total_jobs=total_jobs,
            total_success=total_success,
            total_fail=total_fail,
            success_rate=round(taxa_sucesso, 2),
        )

    def create_job(self, config: AdditionJobConfig) -> AdditionJob:
        """Cria e persiste um novo Job de Adição, pronto para ser executado."""
        with self._db.session() as session:
            # 1. Resolver ID da conta
            account_stmt = select(Account).where(Account.phone == config.account_phone)
            account = session.scalar(account_stmt)
            if not account:
                logger.error("Conta %s não encontrada para criar job.", config.account_phone)
                raise ValueError(f"Conta {config.account_phone} não encontrada.")

            # 2. Criar o Job principal
            job = AdditionJob(
                account_id=account.id,
                target_group=config.target_group,
                status=config.status.value,
                total_users=len(config.user_ids),
                delay_min=config.delay_min,
                delay_max=config.delay_max,
                max_add_per_day=config.max_add_per_day,
                stop_on_consecutive_errors=config.stop_on_consecutive_errors,
            )
            session.add(job)
            session.flush()  # Para obter o job.id

            # 3. Criar os logs de usuários (fila de trabalho)
            for user_id in config.user_ids:
                log_entry = AddedUserLog(
                    job_id=job.id,
                    user_id=user_id,
                    status=TaskStatus.SCHEDULED.value,
                )
                session.add(log_entry)

            session.commit()
            logger.info("Job de Adição %d criado com %d usuários.", job.id, job.total_users)
            return job

    def start_job(self, job_id: int, on_update: Callable[[AdditionJobMonitor], None]) -> None:
        """Inicia a execução de um job em background."""

        job_monitor = self._prepare_monitor(job_id)
        if not job_monitor:
            logger.warning("Tentativa de iniciar job %d inválido.", job_id)
            return

        self._active_jobs[job_id] = job_monitor

        # A função real que roda no worker
        def _job_runner() -> None:
            try:
                self._run_job_loop(job_monitor, on_update)
            except Exception as e:
                logger.exception("Erro fatal no runner do Job de Adição %d", job_id)
                self._update_monitor_status(
                    job_monitor, TaskStatus.FAILED, f"Erro fatal: {e}"
                )
            finally:
                self._active_jobs.pop(job_id, None)
                on_update(job_monitor)  # Envia o estado final

        self._engine.executar_em_background(
            identificador=f"addition-job-{job_id}",
            acao=_job_runner,
        )

    def _prepare_monitor(self, job_id: int) -> AdditionJobMonitor | None:
        """Carrega dados do banco para criar um monitor em memória."""
        with self._db.session() as session:
            job = session.get(AdditionJob, job_id)
            if not job:
                return None

            return AdditionJobMonitor(
                job_id=job.id,
                status=TaskStatus(job.status),
                total_users=job.total_users,
                success_count=job.success_count,
                fail_count=job.fail_count,
            )

    def _run_job_loop(
        self,
        monitor: AdditionJobMonitor,
        on_update: Callable[[AdditionJobMonitor], None],
    ) -> None:
        """Loop principal de execução do job."""
        self._update_monitor_status(monitor, TaskStatus.RUNNING, "Iniciando operação...")
        on_update(monitor)

        # TODO: Implementar lógica de pausa/retomada (ex: via flag no monitor)
        # TODO: Implementar lógica de cliente Telegram (ex: self._pool.get_or_create)

        # Esta é uma SIMULAÇÃO da lógica que você especificou
        with self._db.session() as session:
            job = session.get(AdditionJob, monitor.job_id)
            if not job:
                return

            # Busca a fila de trabalho (usuários agendados)
            stmt = (
                select(AddedUserLog, ExtractedUser)
                .join(ExtractedUser, AddedUserLog.user_id == ExtractedUser.id)
                .where(AddedUserLog.job_id == job.id)
                .where(AddedUserLog.status == TaskStatus.SCHEDULED.value)
            )
            fila_trabalho = session.execute(stmt).all()

            consecutive_errors = 0

            for log_entry, user in fila_trabalho:
                delay = secrets.randbelow(job.delay_max - job.delay_min + 1) + job.delay_min
                monitor.current_user = user.username
                monitor.next_add_in_seconds = delay

                # Simula o "countdown" do delay
                for i in range(delay, 0, -1):
                    monitor.next_add_in_seconds = i
                    on_update(monitor)
                    time.sleep(1)

                # Simula a tentativa de adição
                # 80% Sucesso, 15% Falha tratável, 5% Falha grave (limite)
                resultado = secrets.choice(
                    [TaskStatus.COMPLETED] * 80
                    + [TaskStatus.FAILED] * 15
                    + [AdditionErrorReason.TELEGRAM_API_LIMIT] * 5
                )

                if resultado == TaskStatus.COMPLETED:
                    consecutive_errors = 0
                    log_entry.status = TaskStatus.COMPLETED.value
                    log_entry.completed_at = datetime.utcnow()
                    monitor.success_count += 1
                    self._update_monitor_status(
                        monitor,
                        TaskStatus.RUNNING,
                        f"Sucesso: {user.username} adicionado.",
                    )
                else:
                    consecutive_errors += 1
                    log_entry.status = TaskStatus.FAILED.value
                    # Simula a razão da falha
                    reason = (
                        resultado
                        if isinstance(resultado, AdditionErrorReason)
                        else secrets.choice(
                            [
                                AdditionErrorReason.USER_ALREADY_IN_GROUP,
                                AdditionErrorReason.PRIVACY_RESTRICTIONS,
                                AdditionErrorReason.USER_BLOCKED_ADDITIONS,
                            ]
                        )
                    )
                    log_entry.error_reason = reason.value
                    monitor.fail_count += 1
                    self._update_monitor_status(
                        monitor,
                        TaskStatus.RUNNING,
                        f"Falha: {user.username} ({reason.value}).",
                    )

                # Atualiza progresso e persiste no DB
                monitor.progress = int(
                    ((monitor.success_count + monitor.fail_count) / monitor.total_users) * 100
                )
                session.commit()
                on_update(monitor)

                # Verifica limites de segurança
                if consecutive_errors >= job.stop_on_consecutive_errors:
                    self._update_monitor_status(
                        monitor,
                        TaskStatus.FAILED,
                        f"Parado por {consecutive_errors} erros consecutivos.",
                    )
                    break
                if reason == AdditionErrorReason.TELEGRAM_API_LIMIT:
                    self._update_monitor_status(
                        monitor,
                        TaskStatus.FAILED,
                        "Detectado Flood Wait (API Limit). Job pausado.",
                    )
                    break  # TODO: Pausar em vez de falhar

            # Finaliza o Job
            final_status = (
                TaskStatus.COMPLETED if monitor.status == TaskStatus.RUNNING else monitor.status
            )
            self._update_monitor_status(
                monitor, final_status, "Operação de adição concluída."
            )
            session.query(AdditionJob).filter(AdditionJob.id == job.id).update(
                {
                    "status": monitor.status.value,
                    "progress": monitor.progress,
                    "success_count": monitor.success_count,
                    "fail_count": monitor.fail_count,
                    "completed_at": datetime.utcnow(),
                }
            )
            session.commit()

    def _update_monitor_status(
        self, monitor: AdditionJobMonitor, status: TaskStatus, log: str
    ) -> None:
        """Atualiza o monitor e loga a mensagem."""
        monitor.status = status
        monitor.logs.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
        if len(monitor.logs) > 100:
            monitor.logs.pop()
        logger.info("Job %d: %s", monitor.job_id, log)
