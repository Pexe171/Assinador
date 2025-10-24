"""Serviços centrais relacionados à extração básica de usuários."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

from sqlalchemy import func, select

from TelegramManager.core.database import Database
from TelegramManager.storage import Account, ExtractionJob, ExtractedUser


@dataclass
class ExtractedUserRecord:
    """Estrutura de dados imutável representando um usuário extraído."""

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
    users: List[ExtractedUserRecord]


@dataclass
class ExtractionOverview:
    """Resumo global do banco de dados de extrações."""

    total_users: int
    total_groups: int


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

        grupos_normalizados = [grupo.strip() for grupo in grupos if grupo.strip()]
        if not grupos_normalizados:
            raise ValueError("É necessário informar ao menos um grupo para extrair dados.")

        filtro_normalizado = filtro.lower().strip() if filtro else ""

        candidatos: List[ExtractedUserRecord] = []
        for indice, grupo in enumerate(grupos_normalizados, start=1):
            base = grupo.lower().replace(" ", "_")
            for incremento in range(1, 6):
                username = f"@{base}_{indice:02d}{incremento:02d}"
                role = secrets.choice(self._ROLES)
                segment = secrets.choice(self._SEGMENTS)
                status = secrets.choice(self._STATUSES)
                registro = ExtractedUserRecord(
                    username=username,
                    role=role,
                    origin_group=grupo,
                    segment=segment,
                    status=status,
                )
                if not filtro_normalizado or filtro_normalizado in " ".join(
                    [registro.username, registro.role, registro.origin_group]
                ).lower():
                    candidatos.append(registro)

        with self._database.session() as sessao:
            account_id = self._resolver_account_id(sessao, conta_phone)
            job = ExtractionJob(
                account_id=account_id,
                status="processing",
                progress=0,
                created_at=datetime.utcnow(),
            )
            sessao.add(job)
            sessao.flush()

            for usuario in candidatos:
                sessao.add(
                    ExtractedUser(
                        job_id=job.id,
                        username=usuario.username,
                        role=usuario.role,
                        origin_group=usuario.origin_group,
                        segment=usuario.segment,
                        status=usuario.status,
                        created_at=datetime.utcnow(),
                    )
                )

            job.status = "completed"
            job.progress = 100 if candidatos else 0
            sessao.commit()

            return ExtractionSummary(job_id=job.id, progress=job.progress, users=candidatos)

    def list_recent_users(self, limite: int = 200) -> List[ExtractedUserRecord]:
        """Retorna os usuários mais recentes armazenados na base local."""

        with self._database.session() as sessao:
            stmt = (
                select(ExtractedUser)
                .order_by(ExtractedUser.created_at.desc())
                .limit(limite)
            )
            registros = sessao.scalars(stmt).all()
            return [
                ExtractedUserRecord(
                    username=item.username,
                    role=item.role,
                    origin_group=item.origin_group,
                    segment=item.segment,
                    status=item.status,
                )
                for item in registros
            ]

    def overview(self) -> ExtractionOverview:
        """Gera um resumo com contagem de usuários e grupos distintos."""

        with self._database.session() as sessao:
            total_usuarios = sessao.scalar(select(func.count(ExtractedUser.id))) or 0
            total_grupos = sessao.scalar(select(func.count(func.distinct(ExtractedUser.origin_group)))) or 0
            return ExtractionOverview(total_users=int(total_usuarios), total_groups=int(total_grupos))

    @staticmethod
    def _resolver_account_id(sessao, phone: Optional[str]) -> Optional[int]:
        """Obtém o ID da conta associada ao telefone, quando possível."""

        if not phone:
            return None

        stmt = select(Account).where(Account.phone == phone)
        conta = sessao.scalars(stmt).first()
        return conta.id if conta else None
