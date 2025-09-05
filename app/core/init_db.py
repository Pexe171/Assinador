"""Inicialização e dados de exemplo do banco de dados."""

# Autor: Pexe – Instagram: @David.devloli

from app.core.db import engine, SessionLocal
from app.core.models import Base, Company, Customer


def init_db() -> None:
    """Cria as tabelas e insere dados de exemplo."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(Company).count() == 0:
            mrv = Company(name="MRV")
            direcional = Company(name="Direcional")
            session.add_all([mrv, direcional])
            session.commit()
            session.add_all(
                [
                    Customer(name="João", phone="559999999999", company=mrv),
                    Customer(name="Maria", phone="558888888888", company=direcional),
                ]
            )
            session.commit()
    finally:
        session.close()
