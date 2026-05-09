from sqlalchemy import Column, Integer, Float, ForeignKey
from .config_db import Base
from sqlalchemy.orm import relationship

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    id_pedido = Column("id_pedido", ForeignKey("pedidos.id"))
    id_produto = Column("id_produto", ForeignKey("produtos.id"))
    quantidade = Column("quantidade", Integer)
    preco_unitario = Column("preco_unitario", Float)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")


    def __init__(self, pedido, produto, quantidade, preco_unitario):
        self.id_pedido = pedido
        self.id_produto = produto
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
