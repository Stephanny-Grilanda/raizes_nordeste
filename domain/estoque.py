from sqlalchemy import Column, Integer, ForeignKey
from .config_db import Base
from sqlalchemy.orm import relationship

class Estoque(Base):
    __tablename__ = "estoque"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    id_produto = Column("id_produto", Integer, ForeignKey("produtos.id"))
    id_unidade = Column("id_unidade", Integer, ForeignKey("unidades.id"))

    produto = relationship("Produto", back_populates="estoques")
    unidade = relationship("Unidade", back_populates="estoques")

    def __init__(self, quantidade, produto, unidade):
        self.quantidade = quantidade
        self.id_produto = produto
        self.id_unidade = unidade