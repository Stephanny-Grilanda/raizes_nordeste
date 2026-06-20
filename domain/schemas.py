from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from domain.enums import TipoFuncionario, CanalPedido, StatusPedido, StatusPagamento, MetodoPagamento


class ClienteSchema(BaseModel):
    nome: str
    documento: int = Field(..., ge=10000000000, le=99999999999, description="CPF do cliente (11 dígitos numéricos)")
    email: EmailStr
    senha: str
    rua: Optional[str]
    numero: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    cep: Optional[str]

    class Config:
        from_attributes = True

class FuncionarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo_funcionario: TipoFuncionario
    id_unidade: int

    class Config:
        from_attributes = True

class ItemPedidoSchema(BaseModel):
    id_produto: int
    quantidade: int

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    documento_cliente: Optional[int] = Field(
        default=None, 
        description="Obrigatório apenas no BALCAO. Clientes logados no APP/WEB/TOTEM não precisam enviar."
    )
    id_unidade: int
    canal_pedido: CanalPedido
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True

class PedidoResponseSchema(BaseModel):
    id: int
    id_cliente: int
    id_unidade: int
    id_funcionario: Optional[int]
    canal_pedido: CanalPedido
    status: StatusPedido
    valor_total: float

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str
    
    class Config:
        from_attributes = True

class PagamentoRequestSchema(BaseModel):
    """
    Simula a entrada do processamento do mock de pagamento.
    Usado no endpoint POST /pagamentos/mock.
    """
    id_pedido: int
    metodo_pagamento: MetodoPagamento
    simular_falha: bool = Field(
        default=False,
        description="Quando True, simula recusa do pagamento, alterando o status para 'RECUSADO'; quando False, aprova o pagamento.",
    )

    class Config:
        from_attributes = True

class PagamentoResponseSchema(BaseModel):
    """
    Simula a saída do processamento do mock de pagamento. 
    Retorna identificadores, status, valor e mensagem descritiva para o cliente.
    """
    id_pagamento: int
    id_pedido: int
    status: StatusPagamento
    valor: float
    mensagem: str

    class Config:
        from_attributes = True

class ClienteResponseSchema(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True

class FuncionarioResponseSchema(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True

class AtualizarStatusSchema(BaseModel):
    status: StatusPedido

    class Config:
        from_attributes = True