from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from domain import cliente
from domain.schemas import PagamentoRequestSchema, PagamentoResponseSchema
from infra.dependencies import criar_sessao, verificar_usuario_logado
from api.services.pagamento_service import processar_pagamento_mock

payment_router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])


@payment_router.post(
    "/mock",
    response_model=PagamentoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Simular pagamento através de mock.",
    description=(
        "Simula integração com gateway de pagamento externo através de mock."
        "Aprova ou recusa a transação conforme o campo `simular_falha` e atualiza o status do pedido."
        "Requer que o cliente esteja autenticado."
    ),
    responses={
        200: {
            "description": "Pagamento processado (aprovado ou recusado conforme simulação)",
            "model": PagamentoResponseSchema,
        },
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Cliente não autorizado a pagar este pedido"},
        404: {"description": "Pedido não encontrado"},
        409: {
            "description": (
                "Conflito de regra de negócio "
                "(pedido não pendente, pagamento já registrado ou estoque insuficiente na baixa)"
            )
        },
        422: {"description": "Dados de entrada inválidos"},
    },
)
async def pagamento_mock(
    pagamento_request: PagamentoRequestSchema,
    session: Session = Depends(criar_sessao),
    dados_usuario: dict = Depends(verificar_usuario_logado),
):
    """
    Endpoint de pagamento mock — simula o retorno de um gateway externo.

    Cenários cobertos:
    - simular_falha=False → altera o status do pedido e do pagamento para PAGO
    - simular_falha=True  → altera o status do pagamento para RECUSADO e mantém o pedido como PENDENTE
    """
    resultado = processar_pagamento_mock(
        id_pedido=pagamento_request.id_pedido,
        metodo_pagamento=pagamento_request.metodo_pagamento,
        simular_falha=pagamento_request.simular_falha,
        dados_usuario=dados_usuario,
        session=session,
    )
    return resultado