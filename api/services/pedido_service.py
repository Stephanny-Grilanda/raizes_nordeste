from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.cliente import Cliente
from domain.pedido import Pedido
from domain.item_pedido import ItemPedido
from domain.produto import Produto
from domain.unidade import Unidade
from domain.schemas import PedidoSchema
from domain.enums import StatusPedido
from api.services.estoque_service import validar_estoque_disponivel


def criar_pedido(
    pedido_schema: PedidoSchema,
    cliente_logado: Cliente,
    session: Session,
) -> Pedido:
    """
    Caso de uso: criar um novo pedido com itens e valor total calculado.

    Regras de negócio:
    - Valida existência da unidade
    - Valida existência de cada produto
    - Valida estoque disponível na unidade (tabela estoque)
    - Cria itens do pedido com preço unitário do produto
    - Calcula valor_total via método de domínio calcular_valor_total()
    - Persiste pedido com status inicial PENDENTE (aguardando pagamento mock)
    """
    unidade = session.query(Unidade).filter(Unidade.id == pedido_schema.id_unidade).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_NAO_ENCONTRADA",
                "message": f"Unidade com ID {pedido_schema.id_unidade} não encontrada.",
                "details": [{"field": "id_unidade", "issue": "Unidade inexistente"}],
            },
        )

    # Pré-validação: produtos existem e há estoque — antes de gravar qualquer dado
    for item_schema in pedido_schema.itens:
        produto = session.query(Produto).filter(Produto.id == item_schema.id_produto).first()

        if not produto:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PRODUTO_NAO_ENCONTRADO",
                    "message": f"Produto com ID {item_schema.id_produto} não encontrado.",
                    "details": [
                        {
                            "field": "itens.id_produto",
                            "issue": f"Produto ID {item_schema.id_produto} inexistente",
                        }
                    ],
                },
            )

    # Regra de negócio: estoque por unidade (ex.: 45 unidades com saldo 30 → 409)
    validar_estoque_disponivel(pedido_schema.id_unidade, pedido_schema.itens, session)

    novo_pedido = Pedido(
        cliente=cliente_logado.id,
        unidade=pedido_schema.id_unidade,
        funcionario=pedido_schema.id_funcionario,
        canal_pedido=pedido_schema.canal_pedido,
        valor_total=0.0,
        status=StatusPedido.PENDENTE,
    )

    session.add(novo_pedido)
    session.flush()

    for item_schema in pedido_schema.itens:
        produto = session.query(Produto).filter(Produto.id == item_schema.id_produto).first()

        novo_item = ItemPedido(
            pedido=novo_pedido.id,
            produto=produto.id,
            quantidade=item_schema.quantidade,
            preco_unitario=produto.preco,
        )

        novo_pedido.itens.append(novo_item)

    novo_pedido.calcular_valor_total()

    session.commit()
    session.refresh(novo_pedido)

    return novo_pedido
