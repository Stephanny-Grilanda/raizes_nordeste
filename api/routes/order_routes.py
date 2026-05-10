from fastapi import APIRouter
from domain.usuario import Usuario
from infra.config_db import database
from sqlalchemy.orm import sessionmaker

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos_padrao():
    """
    Endpoint padrão para pedidos no sistema
    """
    return {"mensagem": "Você está na rota de pedidos!"}
