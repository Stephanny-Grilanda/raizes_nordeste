import logging
from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.cliente import Cliente
from domain.pedido import Pedido
from domain.pagamento import Pagamento
from domain.enums import StatusPedido, StatusPagamento, MetodoPagamento
from api.services.estoque_service import baixar_estoque_pedido

# Auditoria para rastreio de ações
logger_auditoria = logging.getLogger("auditoria.pagamento")
if not logger_auditoria.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger_auditoria.addHandler(handler)
    logger_auditoria.setLevel(logging.INFO)


def processar_pagamento_mock(
    id_pedido: int,
    metodo_pagamento: MetodoPagamento,
    simular_falha: bool,
    cliente_logado: Cliente,
    session: Session,
) -> dict:
    """
    Caso de uso: simular transação de pagamento e atualizar status do pedido.

    Fluxo de negócio:
    1. Busca pedido pelo ID
    2. Valida se pertence ao cliente autenticado
    3. Valida se status é PENDENTE
    4. Se simular_falha=False → altera status do pagamento e pedido para pago e baixa o estoque.
    5. Se simular_falha=True  → altera status do pagamento para recusado e mantém pedido pendente, sem baixar estoque.
    6. Registra log de auditoria com ID do cliente (ação sensível)
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": f"Pedido com ID {id_pedido} não encontrado.",
                "details": [{"field": "id_pedido", "issue": "Pedido inexistente"}],
            },
        )

    # Cliente só pode pagar seus próprios pedidos
    if pedido.id_cliente != cliente_logado.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "ACESSO_NEGADO",
                "message": "Você não tem permissão para pagar este pedido.",
                "details": [{"field": "id_pedido", "issue": "Pedido pertence a outro cliente"}],
            },
        )

    # Pagamento aceito somente para pedidos pendentes
    if pedido.status != StatusPedido.PENDENTE:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "PEDIDO_NAO_PENDENTE",
                "message": f"Pedido {id_pedido} não está pendente. Status atual: {pedido.status.value}.",
                "details": [
                    {
                        "field": "status",
                        "issue": f"Esperado PENDENTE, recebido {pedido.status.value}",
                    }
                ],
            },
        )

    # Evita duplicidade de pagamento para o mesmo pedido.
    if pedido.pagamento is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "PAGAMENTO_JA_REGISTRADO",
                "message": f"O pedido {id_pedido} já possui um pagamento registrado.",
                "details": [{"field": "id_pedido", "issue": "Pagamento duplicado não permitido"}],
            },
        )

    if simular_falha:
        # Cenário negativo
        novo_pagamento = Pagamento(
            id_pedido=pedido.id,
            status=StatusPagamento.RECUSADO,
            data_transacao=date.today(),
            valor=pedido.valor_total,
            metodo_pagamento=metodo_pagamento,
        )
        session.add(novo_pagamento)
        session.commit()
        session.refresh(novo_pagamento)

        # Auditoria LGPD: registra ação sensível sem expor dados pessoais completos
        logger_auditoria.info(
            "Transação de pagamento processada e status do pedido atualizado | "
            "acao=PAGAMENTO_RECUSADO | id_cliente=%s | id_pedido=%s | id_pagamento=%s",
            cliente_logado.id,
            id_pedido,
            novo_pagamento.id,
        )

        return {
            "id_pagamento": novo_pagamento.id,
            "id_pedido": pedido.id,
            "status": StatusPagamento.RECUSADO,
            "valor": novo_pagamento.valor,
            "mensagem": "Pagamento recusado pelo gateway mock. O pedido permanece pendente.",
        }

    # Cenário positivo
    novo_pagamento = Pagamento(
        id_pedido=pedido.id,
        status=StatusPagamento.PAGO,
        data_transacao=date.today(),
        valor=pedido.valor_total,
        metodo_pagamento=metodo_pagamento,
    )

    pedido.status = StatusPedido.PAGO

    # Baixa estoque somente após pagamento aprovado
    baixar_estoque_pedido(pedido, session)

    session.add(novo_pagamento)
    session.commit()
    session.refresh(novo_pagamento)

    # log de ação sensível para auditoria (LGPD/Segurança)
    logger_auditoria.info(
        "Transação de pagamento processada e status do pedido atualizado | "
        "acao=PAGAMENTO_APROVADO | id_cliente=%s | id_pedido=%s | id_pagamento=%s | novo_status=%s",
        cliente_logado.id,
        id_pedido,
        novo_pagamento.id,
        pedido.status.value,
    )

    return {
        "id_pagamento": novo_pagamento.id,
        "id_pedido": pedido.id,
        "status": StatusPagamento.PAGO,
        "valor": novo_pagamento.valor,
        "mensagem": "Pagamento aprovado com sucesso. Pedido atualizado para PAGO.",
    }
