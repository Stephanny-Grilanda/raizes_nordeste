from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship
from infra.config_db import Base
from .enums import TipoUsuario

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String)
    senha = Column("senha", String)
    tipo_usuario = Column(Enum(TipoUsuario), nullable=False)
    rua = Column("rua", String, nullable=True)
    numero = Column("numero", String, nullable=True)
    complemento = Column("complemento", String, nullable=True)
    bairro = Column("bairro", String, nullable=True)
    cidade = Column("cidade", String, nullable=True)
    estado = Column("estado", String, nullable=True)
    cep = Column("cep", String, nullable=True)

    pedidos = relationship("Pedido", back_populates="usuario")


    def __init__(self, nome, email, senha, tipo_usuario, rua=None, numero=None, complemento=None, bairro=None, cidade=None, estado=None, cep=None):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo_usuario = tipo_usuario
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        