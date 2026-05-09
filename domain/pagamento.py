from sqlalchemy import Column, String, Date, Integer, Float, Boolean, ForeignKey, Enum
from .config_db import Base
from .enums import StatusPagamento, MetodoPagamento
from sqlalchemy.orm import relationship

class Pagamento(Base):
   __tablename__ = "pagamentos"

   id = Column("id", Integer, primary_key=True, autoincrement=True)
   id_pedido = Column("id_pedido", ForeignKey("pedidos.id"))
   status = Column(Enum(StatusPagamento), nullable=False)
   data_transacao = Column("data_transacao", Date)
   valor = Column("valor", Float)
   metodo_pagamento = Column(Enum(MetodoPagamento), nullable=False)

   pedido = relationship("Pedido", back_populates="pagamento")

   def __init__(self, id_pedido, status, data_transacao, valor, metodo_pagamento):
      self.id_pedido = id_pedido
      self.status = status
      self.data_transacao = data_transacao
      self.valor = valor
      self.metodo_pagamento = metodo_pagamento
