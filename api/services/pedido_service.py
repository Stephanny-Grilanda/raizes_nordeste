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

    cliente_id = None
    
    if role == "cliente":
        cliente_id = usuario.id
    else:
        # Se o perfil for de funcionário, o campo documento_cliente é opcional. Se for fornecido, deve ser validado. Se não for fornecido, o pedido será registrado como anônimo.
        if pedido_schema.documento_cliente:
            cliente_db = session.query(Cliente).filter(Cliente.documento == pedido_schema.documento_cliente).first()
            if not cliente_db:
                raise HTTPException(
                    status_code=404, 
                    detail={
                        "error": "CLIENTE_NAO_ENCONTRADO", 
                        "message": "Cliente não cadastrado. Para registrar um pedido sem cadastrá-lo, não envie o campo documento_cliente."
                    }
                )
            cliente_id = cliente_db.id

    unidade = session.query(Unidade).filter(Unidade.id == pedido_schema.id_unidade).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={"error": "UNIDADE_NAO_ENCONTRADA", "message": "Unidade não encontrada."}
        )
    
    if role == "funcionario" and usuario.tipo_funcionario != TipoFuncionario.ADMIN:
        if usuario.id_unidade != pedido_schema.id_unidade:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "ACESSO_NEGADO", 
                    "message": "Você só tem permissão para registrar pedidos na sua própria unidade de trabalho."
                }
            )

    for item_schema in pedido_schema.itens:
        produto = session.query(Produto).filter(Produto.id == item_schema.id_produto).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail={"error": "PRODUTO_NAO_ENCONTRADO", "message": f"Produto com ID {item_schema.id_produto} não encontrado."}
            )

    validar_estoque_disponivel(pedido_schema.id_unidade, pedido_schema.itens, session)

    # identifica tipo funcionario
    id_func = usuario.id if role == "funcionario" else None


    novo_pedido = Pedido(
        cliente=cliente_id,
        unidade=pedido_schema.id_unidade,
        funcionario=id_func,
        canal_pedido=pedido_schema.canal_pedido,
        valor_total=0.0,
        status=StatusPedido.PENDENTE,
    )

    session.add(novo_pedido)
    session.flush()

    # adiciona os itens do pedido e calcula o total
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


async def listar_pedidos(canal_pedido: CanalPedido, dados_usuario: dict, session: Session):
    usuario = dados_usuario["usuario"]
    role = dados_usuario["role"]

    query = session.query(Pedido)

    if role == "cliente":
        query = query.filter(Pedido.id_cliente == usuario.id)

    elif role == "funcionario":
        if usuario.tipo_funcionario != TipoFuncionario.ADMIN:
            query = query.filter(Pedido.id_unidade == usuario.id_unidade)

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

    if usuario.tipo_funcionario == TipoFuncionario.COZINHA:
        if novo_status not in [StatusPedido.PREPARACAO, StatusPedido.PRONTO]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "STATUS_NAO_PERMITIDO", 
                    "message": "Funcionarios da conzinha só podem alterar o status do pedido para PREPARACAO ou PRONTO.."
                }
            )

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=404, 
            detail={"error": "PEDIDO_NAO_ENCONTRADO", "message": f"Pedido com ID {id_pedido} não encontrado."}
        )

    if usuario.tipo_funcionario != TipoFuncionario.ADMIN and pedido.id_unidade != usuario.id_unidade:
        raise HTTPException(
            status_code=403, 
            detail={"error": "ACESSO_NEGADO", "message": "Você não pode alterar o status de um pedido de outra unidade."}
        )
    
    pedido.status = novo_status
    session.commit()
    session.refresh(pedido)

    return pedido