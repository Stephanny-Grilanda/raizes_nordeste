from sqlalchemy import Column, String, Integer, Float
from infra.config_db import Base
from sqlalchemy.orm import relationship

class Produto(Base):
    __tablename__ = "produtos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    descricao = Column("descricao", String)
    categoria = Column("categoria", String)
    preco = Column("preco", Float)

    itens_pedido = relationship("ItemPedido", back_populates="produto")
    estoques = relationship("Estoque", back_populates="produto")

    def __init__(self, nome, descricao, categoria, preco):
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.preco = preco