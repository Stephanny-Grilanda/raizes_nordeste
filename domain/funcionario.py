from sqlalchemy import Column, ForeignKey, String, Integer, Enum
from sqlalchemy.orm import relationship
from infra.config_db import Base
from .enums import TipoFuncionario

class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    id_unidade = Column("id_unidade", ForeignKey("unidades.id"))
    nome = Column("nome", String)
    email = Column("email", String)
    senha = Column("senha", String)
    tipo_funcionario = Column(Enum(TipoFuncionario), nullable=False)

    pedidos = relationship("Pedido", back_populates="funcionario")
    unidade = relationship("Unidade", back_populates="funcionarios")


    def __init__(self, nome, email, senha, tipo_funcionario, id_unidade):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo_funcionario = tipo_funcionario
        self.id_unidade = id_unidade