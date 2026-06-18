from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from domain import cliente
from domain.schemas import PedidoSchema, PedidoResponseSchema
from infra.dependencies import criar_sessao, verificar_token_cliente
from api.services.pedido_service import criar_pedido as criar_pedido_service

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
    cliente_logado: cliente.Cliente = Depends(verificar_token_cliente),
):
    """
    Endpoint para criar um novo pedido.

    A rota não contém regra de negócio — apenas orquestra a chamada ao service,
    separando responsabilidades entre camada API e camada Application.
    """
    novo_pedido = criar_pedido_service(pedido_schema, cliente_logado, session)
    return novo_pedido
