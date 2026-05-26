from fastapi import APIRouter, Depends, HTTPException as excecao
from sqlalchemy.orm import Session
from domain import cliente
from domain.pedido import Pedido
from domain.item_pedido import ItemPedido
from domain.produto import Produto
from domain.schemas import PedidoSchema
from infra.dependencies import criar_sessao, verificar_token_cliente, verificar_token_funcionario

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos_padrao():
    """
    Endpoint padrão para pedidos no sistema
    """
    return {"mensagem": "Você está na rota de pedidos!"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(criar_sessao), cliente_logado: cliente = Depends(verificar_token_cliente)):
    """
    Endpoint para criar um novo pedido
    """

    novo_pedido = Pedido(
        cliente=cliente_logado.id,
        unidade=pedido_schema.id_unidade,
        funcionario=pedido_schema.id_funcionario, 
        canal_pedido=pedido_schema.canal_pedido, 
        valor_total=0.0
    )
    
    session.add(novo_pedido)
    session.flush()

    for item_schema in pedido_schema.itens:

        produto = session.query(Produto).filter(Produto.id == item_schema.id_produto).first()
        
        if not produto:
            raise excecao(status_code=404, detail=f"Produto com ID {item_schema.id_produto} não encontrado.")

        novo_item = ItemPedido(
            pedido=novo_pedido.id, 
            produto=produto.id, 
            quantidade=item_schema.quantidade, 
            preco_unitario=produto.preco
        )
        
        novo_pedido.itens.append(novo_item)

    novo_pedido.calcular_valor_total()

    session.commit()
    
    return {"mensagem": "Pedido criado com sucesso!", "pedido_id": novo_pedido.id}

