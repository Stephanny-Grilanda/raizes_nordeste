from fastapi import APIRouter, Depends, HTTPException as excecao
from domain.pedido import Pedido
from infra.schemas import PedidoSchema
from infra.config_db import database
from sqlalchemy.orm import sessionmaker
from infra.dependencies import criar_sessao
from sqlalchemy.orm import Session

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos_padrao():
    """
    Endpoint padrão para pedidos no sistema
    """
    return {"mensagem": "Você está na rota de pedidos!"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(criar_sessao)):
    """
    Endpoint para criar um novo pedido
    """
    novo_pedido = Pedido(
        id_cliente=pedido_schema.id_cliente, 
        id_unidade=pedido_schema.id_unidade,
        id_funcionario=pedido_schema.id_funcionario, 
        canal_pedido=pedido_schema.canal_pedido, 
        itens_pedido=pedido_schema.itens
    )
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": "Pedido criado com sucesso!", "pedido_id": novo_pedido.id}