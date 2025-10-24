"""Modelos ORM da aplicação."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="offline")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
