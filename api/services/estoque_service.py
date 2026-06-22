import logging
from typing import Iterable

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.estoque import Estoque
from domain.pedido import Pedido
from domain.produto import Produto

logger_auditoria = logging.getLogger("auditoria.estoque")
if not logger_auditoria.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger_auditoria.addHandler(handler)
    logger_auditoria.setLevel(logging.INFO)


def _agrupar_quantidade_por_produto(itens: Iterable) -> dict[int, int]:
    """
    Soma quantidades quando o mesmo produto aparece mais de uma vez no pedido.
    Ex.: [{produto 1, qtd 20}, {produto 1, qtd 15}] → {1: 35}
    """
    quantidade_por_produto = {}

    for item in itens:
        id_produto = item.id_produto
        quantidade_por_produto[id_produto] = (
            quantidade_por_produto.get(id_produto, 0) + item.quantidade
        )

    return quantidade_por_produto


def validar_estoque_disponivel(id_unidade: int, itens: Iterable, session: Session) -> None:
    """
    Verifica se a unidade possui saldo suficiente para todos os itens solicitados.
    Lança HTTP 409 se um ou mais produtos não tiverem estoque disponível.
    """
    quantidade_por_produto = _agrupar_quantidade_por_produto(itens)
    detalhes_erro = []

    for id_produto, quantidade_solicitada in quantidade_por_produto.items():
        estoque = (
            session.query(Estoque)
            .filter(
                Estoque.id_produto == id_produto,
                Estoque.id_unidade == id_unidade,
            )
            .first()
        )

        quantidade_disponivel = estoque.quantidade if estoque else 0

        if quantidade_solicitada > quantidade_disponivel:
            detalhes_erro.append(
                {
                    "field": f"itens[{id_produto}].quantidade",
                    "issue": (
                        f"Disponível: {quantidade_disponivel}, "
                        f"solicitado: {quantidade_solicitada}"
                    ),
                }
            )

    if detalhes_erro:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "ESTOQUE_INSUFICIENTE",
                "message": "Não há quantidade suficiente para um ou mais itens.",
                "details": detalhes_erro,
            },
        )


def baixar_estoque_pedido(pedido: Pedido, session: Session) -> None:
    """
    Debita o estoque da unidade após pagamento aprovado.
    Revalida o saldo no momento da baixa (evita inconsistência se o estoque mudou).
    """
    for item in pedido.itens:
        estoque = (
            session.query(Estoque)
            .filter(
                Estoque.id_produto == item.id_produto,
                Estoque.id_unidade == pedido.id_unidade,
            )
            .first()
        )

        if not estoque or estoque.quantidade < item.quantidade:
            quantidade_disponivel = estoque.quantidade if estoque else 0
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "ESTOQUE_INSUFICIENTE",
                    "message": (
                        "Estoque insuficiente para concluir o pagamento do pedido. "
                        "Faça um novo pedido ajustando a quantidade."
                    ),
                    "details": [
                        {
                            "field": f"itens[{item.id_produto}].quantidade",
                            "issue": (
                                f"Disponível: {quantidade_disponivel}, "
                                f"solicitado: {item.quantidade}"
                            ),
                        }
                    ],
                },
            )

        estoque.quantidade -= item.quantidade

        logger_auditoria.info(
            "Baixa de estoque realizada | acao=BAIXA_ESTOQUE | id_pedido=%s | "
            "id_unidade=%s | id_produto=%s | quantidade=%s | saldo_restante=%s",
            pedido.id,
            pedido.id_unidade,
            item.id_produto,
            item.quantidade,
            estoque.quantidade,
        )

def listar_produtos_por_unidade(id_unidade: int, session: Session) -> list[dict]:
    """
    Retorna o cardápio e a quantidade em estoque para uma unidade específica.
    """
    resultados = (
        session.query(Produto, Estoque.quantidade)
        .join(Estoque, Produto.id == Estoque.id_produto)
        .filter(Estoque.id_unidade == id_unidade)
        .all()
    )
    
    lista_produtos = []
    for produto, quantidade in resultados:
        lista_produtos.append({
            "id_produto": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "categoria": produto.categoria,
            "preco": produto.preco,
            "quantidade_disponivel": quantidade
        })
        
    if not lista_produtos:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "CARDAPIO_NAO_ENCONTRADO",
                "message": f"Nenhum produto em estoque encontrado para a unidade {id_unidade}.",
                "details": []
            }
        )
        
    return lista_produtos