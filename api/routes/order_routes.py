from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from domain import cliente
from domain.enums import CanalPedido
from domain.schemas import PedidoSchema, PedidoResponseSchema
from infra.dependencies import criar_sessao, verificar_usuario_logado
from api.services.pedido_service import criar_pedido as criar_pedido_service, listar_pedidos


order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos_padrao():
    """
    Endpoint padrão para pedidos no sistema
    """
    return {"mensagem": "Você está na rota de pedidos!"}

@order_router.post(
    "/pedido",
    response_model=PedidoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
    description=(
        "Cria um novo pedido com itens e valor total calculado, validando estoque da unidade. "
        "Requer autenticação JWT de cliente. Status inicial: PENDENTE (aguardando pagamento mock)."
    ),
    responses={
        201: {
            "description": "Pedido criado com sucesso",
            "model": PedidoResponseSchema,
        },
        401: {"description": "Token inválido ou ausente"},
        404: {"description": "Unidade ou produto não encontrado"},
        409: {"description": "Estoque insuficiente para um ou mais itens"},
        422: {"description": "Dados de entrada inválidos"},
    },
)
async def criar_pedido(
    pedido_schema: PedidoSchema,
    session: Session = Depends(criar_sessao),
    dados_usuario: dict = Depends(verificar_usuario_logado),
):
    """Endpoint para criar um novo pedido."""
    novo_pedido = criar_pedido_service(pedido_schema, dados_usuario, session)
    return novo_pedido

@order_router.get(
    "/",
    response_model=List[PedidoResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar e filtrar pedidos",
)
async def listar_pedidos(
    canal_pedido: Optional[CanalPedido] = Query(None, description="Filtrar por canal (ex: APP, TOTEM, BALCAO)"),
    session: Session = Depends(criar_sessao),
    dados_usuario: dict = Depends(verificar_usuario_logado),
):
    """Retorna os pedidos com base no perfil logado e filtro opcional de multicanalidade."""
    return listar_pedidos(canal_pedido, dados_usuario, session)