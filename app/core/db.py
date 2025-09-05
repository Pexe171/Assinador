"""Configuração do banco de dados SQLite local."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import load_settings

settings = load_settings()
DATABASE_URL = f"sqlite:///./assinar.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    """Cria uma sessão de banco de dados."""
    with SessionLocal() as session:
        yield session
