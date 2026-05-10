from sqlalchemy import Column, String, Integer
from infra.config_db import Base
from sqlalchemy.orm import relationship

class Unidade(Base):
    __tablename__ = "unidades"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    rua = Column("rua", String)
    numero = Column("numero", String)
    bairro = Column("bairro", String)
    cidade = Column("cidade", String)
    estado = Column("estado", String)
    cep = Column("cep", String)

    pedidos = relationship("Pedido", back_populates="unidade")
    estoques = relationship("Estoque", back_populates="unidade")

    def __init__(self, rua, numero, bairro, cidade, estado, cep):
        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep