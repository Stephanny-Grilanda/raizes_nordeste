from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.cliente import Cliente
from domain.pedido import Pedido
from domain.item_pedido import ItemPedido
from domain.produto import Produto
from domain.unidade import Unidade
from domain.schemas import PedidoSchema
from domain.enums import StatusPedido, TipoFuncionario, CanalPedido
from api.services.estoque_service import validar_estoque_disponivel


def criar_pedido(
    pedido_schema: PedidoSchema,
    dados_usuario: dict,
    session: Session,
) -> Pedido:
    
    usuario = dados_usuario["usuario"]
    role = dados_usuario["role"]

    # 1. VALIDAÇÃO DE MULTICANALIDADE
    if pedido_schema.canal_pedido == CanalPedido.BALCAO:
        if role != "funcionario" or usuario.tipo_funcionario not in [TipoFuncionario.ATENDENTE, TipoFuncionario.GERENTE, TipoFuncionario.ADMIN]:
            raise HTTPException(
                status_code=403, 
                detail={"error": "ACESSO_NEGADO", "message": "Apenas Atendentes, Gerentes ou Admins podem criar pedidos no balcão."}
            )
    else: 
        if role != "cliente":
            raise HTTPException(
                status_code=403, 
                detail={"error": "ACESSO_NEGADO", "message": f"Funcionários não podem criar pedidos pelo canal {pedido_schema.canal_pedido.value}."}
            )

    # 2. DEFINIR QUEM É O CLIENTE DO PEDIDO
    if role == "cliente":
        cliente_db = usuario
    else:
        if not pedido_schema.documento_cliente:
            raise HTTPException(
                status_code=422, 
                detail={"error": "DOCUMENTO_OBRIGATORIO", "message": "Para pedidos no balcão, o atendente deve informar o documento do cliente."}
            )
        
        cliente_db = session.query(Cliente).filter(Cliente.documento == pedido_schema.documento_cliente).first()
        if not cliente_db:
            raise HTTPException(
                status_code=404, 
                detail={"error": "CLIENTE_NAO_ENCONTRADO", "message": "Cliente inexistente."}
            )

    # 3. VALIDAÇÃO DA UNIDADE
    unidade = session.query(Unidade).filter(Unidade.id == pedido_schema.id_unidade).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={"error": "UNIDADE_NAO_ENCONTRADA", "message": "Unidade não encontrada."}
        )

    # 4. VALIDAÇÃO DE PRODUTOS
    for item_schema in pedido_schema.itens:
        produto = session.query(Produto).filter(Produto.id == item_schema.id_produto).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail={"error": "PRODUTO_NAO_ENCONTRADO", "message": f"Produto com ID {item_schema.id_produto} não encontrado."}
            )

    # 5. VALIDAÇÃO DE ESTOQUE
    validar_estoque_disponivel(pedido_schema.id_unidade, pedido_schema.itens, session)

    # 6. IDENTIFICAR O FUNCIONÁRIO (Se aplicável)
    id_func = usuario.id if role == "funcionario" else None

    # 7. CRIAR O PEDIDO
    novo_pedido = Pedido(
        cliente=cliente_db.id,
        unidade=pedido_schema.id_unidade,
        funcionario=id_func,
        canal_pedido=pedido_schema.canal_pedido,
        valor_total=0.0,
        status=StatusPedido.PENDENTE,
    )

    session.add(novo_pedido)
    session.flush()

    # 8. ADICIONAR ITENS E CALCULAR TOTAL
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


def listar_pedidos(canal_pedido: CanalPedido, dados_usuario: dict, session: Session):
    usuario = dados_usuario["usuario"]
    role = dados_usuario["role"]

    query = session.query(Pedido)

    if role == "cliente":
        query = query.filter(Pedido.id_cliente == usuario.id)

    if canal_pedido:
        query = query.filter(Pedido.canal_pedido == canal_pedido)

    return query.all()

def atualizar_status(id_pedido: int, novo_status: StatusPedido, dados_usuario: dict, session: Session):
    usuario = dados_usuario["usuario"]
    role = dados_usuario["role"]

    if role != "funcionario" or usuario.tipo_funcionario not in [TipoFuncionario.COZINHA, TipoFuncionario.GERENTE, TipoFuncionario.ADMIN]:
        raise HTTPException(
            status_code=403, 
            detail={"error": "ACESSO_NEGADO", "message": "Apenas profissionais da Cozinha, Gerentes ou Administradores podem alterar o status de preparo."}
        )

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=404, 
            detail={"error": "PEDIDO_NAO_ENCONTRADO", "message": f"Pedido com ID {id_pedido} não encontrado."}
        )

    pedido.status = novo_status
    session.commit()
    session.refresh(pedido)

    return pedido