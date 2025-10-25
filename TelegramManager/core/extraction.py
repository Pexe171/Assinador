# Caminho: TelegramManager/core/extraction.py
"""Serviços centrais relacionados à extração básica de usuários."""

from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import func, select

from TelegramManager.core.database import Database
from TelegramManager.storage import Account, ExtractionJob, ExtractedUser

logger = logging.getLogger(__name__)


@dataclass
class ExtractedUserRecord:
    """Estrutura de dados imutável representando um usuário extraído."""
    # Adicionando ID para referência
    id: int
    username: str
    role: str
    origin_group: str
    segment: str
    status: str


@dataclass
class ExtractionSummary:
    """Informações retornadas após a execução de uma extração."""

    job_id: int
    progress: int
    users: List[ExtractedUserRecord] # Mantém o Record para a UI inicial


@dataclass
class ExtractionOverview:
    """Resumo global do banco de dados de extrações."""

    total_users: int
    total_groups: int


@dataclass(frozen=True)
class SyncedGroup:
    """Representa um grupo já sincronizado com o banco local."""

    name: str
    total_members: int
    last_sync: datetime | None
    account_phone: str | None
    account_display_name: str | None


class ExtractionService:
    """Implementa a extração básica persistindo resultados localmente."""

    _ROLES = [
        "Decisor",
        "Analista",
        "Gestor",
        "Especialista",
    ]
    _SEGMENTS = [
        "Lançamento",
        "Clientes VIP",
        "Nutrição",
        "Reengajamento",
    ]
    _STATUSES = [
        "Quente",
        "Morno",
        "Frio",
        "Ativo",
    ]

    def __init__(self, database: Database) -> None:
        self._database = database

    def run_basic_extraction(
        self,
        grupos: Iterable[str],
        *,
        filtro: Optional[str] = None,
        conta_phone: Optional[str] = None,
    ) -> ExtractionSummary:
        """Executa uma extração simples, gerando dados sintéticos persistidos."""
        logger.info("Iniciando extração para grupos: %s (filtro: %s)", grupos, filtro)
        grupos_normalizados = [grupo.strip() for grupo in grupos if grupo.strip()]
        if not grupos_normalizados:
            logger.warning("Nenhum grupo válido fornecido para extração.")
            raise ValueError("É necessário informar ao menos um grupo para extrair dados.")

        filtro_normalizado = filtro.lower().strip() if filtro else ""

        # Gera dados sintéticos
        candidatos_sinteticos: List[Tuple[str, str, str, str, str]] = []
        for indice, grupo in enumerate(grupos_normalizados, start=1):
            base = grupo.lower().replace(" ", "_").replace("@","")[:20] # Limita tamanho
            for incremento in range(1, secrets.randint(5, 15)): # Numero variável de usuários
                username = f"@{base}_{indice:02d}{incremento:02d}"
                role = secrets.choice(self._ROLES)
                segment = secrets.choice(self._SEGMENTS)
                status = secrets.choice(self._STATUSES)
                registro_tupla = (username, role, grupo, segment, status)

                if not filtro_normalizado or filtro_normalizado in " ".join(registro_tupla).lower():
                    candidatos_sinteticos.append(registro_tupla)

        logger.debug("%d candidatos sintéticos gerados.", len(candidatos_sinteticos))

        # Persiste no banco de dados
        usuarios_persistidos: List[ExtractedUser] = []
        with self._database.session() as sessao:
            account_id = self._resolver_account_id(sessao, conta_phone)
            job = ExtractionJob(
                account_id=account_id,
                status="processing",
                progress=0,
                created_at=datetime.utcnow(),
            )
            sessao.add(job)
            sessao.flush() # Para obter job.id
            logger.info("Job de extração %d criado.", job.id)

            for username, role, grupo, segment, status in candidatos_sinteticos:
                usuario_db = ExtractedUser(
                        job_id=job.id,
                        username=username,
                        role=role,
                        origin_group=grupo,
                        segment=segment,
                        status=status,
                        created_at=datetime.utcnow(),
                    )
                sessao.add(usuario_db)
                usuarios_persistidos.append(usuario_db) # Guarda o objeto com ID

            # Precisa dar flush de novo para obter os IDs dos usuários
            sessao.flush()

            job.status = "completed"
            job.progress = 100 if usuarios_persistidos else 0
            sessao.commit()
            logger.info("Job de extração %d concluído com %d usuários.", job.id, len(usuarios_persistidos))


            # Cria os Records para retornar à UI, agora com ID
            user_records = [
                ExtractedUserRecord(
                    id=u.id,
                    username=u.username,
                    role=u.role,
                    origin_group=u.origin_group,
                    segment=u.segment,
                    status=u.status,
                )
                for u in usuarios_persistidos # Usa a lista que tem os IDs
            ]

            return ExtractionSummary(job_id=job.id, progress=job.progress, users=user_records)

    def list_recent_users(self, limite: int = 200) -> List[ExtractedUserRecord]:
        """Retorna os usuários mais recentes como Records (para UI legada)."""
        registros_db = self.list_recent_users_with_id(limite)
        return [
            ExtractedUserRecord(
                id=item.id,
                username=item.username,
                role=item.role,
                origin_group=item.origin_group,
                segment=item.segment,
                status=item.status,
            )
            for item in registros_db
        ]

    def list_recent_users_with_id(self, limite: int = 5000) -> List[ExtractedUser]:
        """Retorna os usuários mais recentes como objetos ORM (com ID)."""
        logger.debug("Buscando %d usuários recentes do banco.", limite)
        with self._database.session() as sessao:
            stmt = (
                select(ExtractedUser)
                .order_by(ExtractedUser.created_at.desc())
                .limit(limite)
            )
            registros = sessao.scalars(stmt).all()
            logger.debug("%d usuários encontrados.", len(registros))
            return list(registros)


    def overview(self) -> ExtractionOverview:
        """Gera um resumo com contagem de usuários e grupos distintos."""
        logger.debug("Calculando overview da extração.")
        with self._database.session() as sessao:
            total_usuarios = sessao.scalar(select(func.count(ExtractedUser.id))) or 0
            total_grupos = sessao.scalar(select(func.count(func.distinct(ExtractedUser.origin_group)))) or 0
            overview = ExtractionOverview(
                total_users=int(total_usuarios), total_groups=int(total_grupos)
            )
            logger.debug("Overview: %s", overview)
            return overview

    def list_synced_groups(
        self, *, account_phone: Optional[str] = None
    ) -> List[SyncedGroup]:
        """Lista os grupos já sincronizados, opcionalmente filtrando por conta."""

        logger.debug("Listando grupos sincronizados (conta=%s)", account_phone)
        with self._database.session() as sessao:
            stmt = (
                select(
                    ExtractedUser.origin_group.label("group_name"),
                    func.count(ExtractedUser.id).label("member_count"),
                    func.max(ExtractionJob.created_at).label("last_sync"),
                    Account.phone.label("phone"),
                    Account.display_name.label("display_name"),
                )
                .join(ExtractionJob, ExtractedUser.job_id == ExtractionJob.id)
                .join(Account, ExtractionJob.account_id == Account.id, isouter=True)
                .group_by(
                    ExtractedUser.origin_group,
                    Account.phone,
                    Account.display_name,
                )
                .order_by(func.max(ExtractionJob.created_at).desc())
            )
            if account_phone:
                stmt = stmt.where(Account.phone == account_phone)

            resultados = sessao.execute(stmt).all()

        grupos: List[SyncedGroup] = []
        for row in resultados:
            grupos.append(
                SyncedGroup(
                    name=row.group_name,
                    total_members=int(row.member_count or 0),
                    last_sync=row.last_sync,
                    account_phone=row.phone,
                    account_display_name=row.display_name,
                )
            )
        logger.debug("%d grupos sincronizados encontrados.", len(grupos))
        return grupos

    @staticmethod
    def _resolver_account_id(sessao, phone: Optional[str]) -> Optional[int]:
        """Obtém o ID da conta associada ao telefone, quando possível."""
        if not phone:
            return None
        stmt = select(Account).where(Account.phone == phone)
        conta = sessao.scalars(stmt).first()
        return conta.id if conta else None
