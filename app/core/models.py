"""Modelos do banco de dados."""

from sqlalchemy.orm import (
    declarative_base,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import Integer, String, Text, ForeignKey

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    customers: Mapped[list["Customer"]] = relationship(
        "Customer", back_populates="company", cascade="all, delete-orphan"
    )


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="customers")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="customer", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pendente", nullable=False)
    customer: Mapped["Customer"] = relationship("Customer", back_populates="documents")


class Conversation(Base):
    """Conversa com usuário no WhatsApp."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wa_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="novo", nullable=False)


class AuditLog(Base):
    """Registro simplificado de eventos para auditoria."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
