from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship
from .config_db import Base
from .enums import TipoUsuario

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String)
    senha = Column("senha", String)
    tipo_usuario = Column(Enum(TipoUsuario), nullable=False)
    rua = Column("rua", String)
    numero = Column("numero", String)
    complemento = Column("complemento", String)
    bairro = Column("bairro", String)
    cidade = Column("cidade", String)
    estado = Column("estado", String)
    cep = Column("cep", String)

    pedidos = relationship("Pedido", back_populates="usuario")


    def __init__(self, nome, email, senha, tipo_usuario, rua, numero, complemento, bairro, cidade, estado, cep):
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
        