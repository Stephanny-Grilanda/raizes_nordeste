from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from domain.schemas import ProdutoEstoqueResponseSchema
from infra.dependencies import criar_sessao, verificar_usuario_logado
from api.services.estoque_service import listar_produtos_por_unidade

product_router = APIRouter(prefix="/produtos", tags=["produtos"])

@product_router.get(
    "/unidade/{id_unidade}",
    response_model=List[ProdutoEstoqueResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar cardápio e estoque por unidade",
    description="Retorna a lista de produtos disponíveis para a unidade solicitada, incluindo a quantidade atual em estoque. Requer autenticação."
)
async def listar_produtos_unidade(
    id_unidade: int,
    session: Session = Depends(criar_sessao),
    dados_usuario: dict = Depends(verificar_usuario_logado)
):
    """Retorna os produtos e estoques para a montagem de pedidos."""
    return listar_produtos_por_unidade(id_unidade, session)