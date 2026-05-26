from pydantic import BaseModel
from typing import Optional, List
from domain.enums import TipoFuncionario, CanalPedido, StatusPedido

class ClienteSchema(BaseModel):
    nome: str
    email: str
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
    email: str
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
    id_cliente: int
    id_unidade: int
    id_funcionario: Optional[int] = None
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
    email: str
    senha: str
    
    class Config:
        from_atributes = True