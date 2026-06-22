from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from domain import cliente
from domain.enums import CanalPedido
from domain.schemas import PedidoSchema, PedidoResponseSchema
from infra.dependencies import criar_sessao, verificar_usuario_logado
from api.services.pedido_service import criar_pedido as criar_pedido_service, listar_pedidos as listar_pedidos_service
from domain.schemas import AtualizarStatusSchema
from domain.enums import StatusPedido
from api.services.pedido_service import atualizar_status as atualizar_status_service

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.post(
    "/pedido",
    response_model=PedidoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
    description=(
        "Cria um novo pedido com itens e valor total calculado, validando estoque da unidade.\n\n "
        "Requer autenticação JWT.\n\n"
        "Clientes podem criar pedidos através dos canais APP, WEB e TOTEM.\n\n Funcionários podem criar pedidos apenas no canal BALCAO."
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
    return await listar_pedidos_service(canal_pedido, dados_usuario, session)

@order_router.patch(
    "/{id_pedido}/status",
    response_model=PedidoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Atualizar status do pedido (Painel da Cozinha)",
)
async def atualizar_status_pedido(
    id_pedido: int,
    status_schema: AtualizarStatusSchema,
    session: Session = Depends(criar_sessao),
    dados_usuario: dict = Depends(verificar_usuario_logado),
):
    """Atualiza o status de um pedido. Acesso restrito à Cozinha, Gerência e Admin."""
    return atualizar_status_service(id_pedido, status_schema.status, dados_usuario, session)