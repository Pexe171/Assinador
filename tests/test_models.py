import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.models import Base, Company, Customer, Document


def test_relationships_and_defaults():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(bind=engine)

    empresa = Company(name="MRV")
    cliente = Customer(name="João", phone="123", company=empresa)
    documento = Document(customer=cliente, file_path="contrato.pdf")
    session.add_all([empresa, cliente, documento])
    session.commit()

    assert cliente.company.name == "MRV"
    assert cliente.documents[0].status == "pendente"
    assert cliente.documents[0].file_path == "contrato.pdf"

    session.close()
