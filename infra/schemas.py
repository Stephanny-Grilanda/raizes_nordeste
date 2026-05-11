from pydantic import BaseModel
from typing import Optional
from domain.enums import TipoFuncionario

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

