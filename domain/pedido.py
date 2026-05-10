from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum
from infra.config_db import Base
from .enums import CanalPedido, StatusPedido
from sqlalchemy.orm import relationship

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    id_usuario = Column("id_usuario", ForeignKey("usuarios.id"))
    id_unidade = Column("id_unidade", ForeignKey("unidades.id"))
    canal_pedido = Column(Enum(CanalPedido), nullable=False)
    status = Column(Enum(StatusPedido), nullable=False, default=StatusPedido.PENDENTE)
    valor_total = Column("valor_total", Float)
    usuario = relationship("Usuario", back_populates="pedidos")
    unidade = relationship("Unidade", back_populates="pedidos")
    itens = relationship("ItemPedido", cascade="all, delete-orphan", back_populates="pedido")
    pagamento = relationship("Pagamento", uselist=False, back_populates="pedido")

    def __init__(self, usuario, unidade, canal_pedido, valor_total, status=StatusPedido.PENDENTE):
        self.id_usuario = usuario
        self.id_unidade = unidade
        self.canal_pedido = canal_pedido
        self.valor_total = valor_total
        self.status = status

    def calcular_valor_total(self):
        self.valor_total = sum(item.preco_unitario * item.quantidade for item in self.itens)