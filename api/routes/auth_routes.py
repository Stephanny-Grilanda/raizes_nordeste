from fastapi import APIRouter, Depends, HTTPException as excecao
from domain.cliente import Cliente
from domain.funcionario import Funcionario
from infra.dependencies import criar_sessao
from infra.security import bcrypt_context
from infra.schemas import ClienteSchema, FuncionarioSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/autenticacao", tags=["autenticacao"])

@auth_router.get("/")
async def autenticacao_padrao():
    """
    Endpoint padrão para autenticação no sistema
    """
    return {"mensagem": "Você está na rota de autenticação!", "autenticado": False}

@auth_router.post("/criar_cliente")
async def criar_cliente(cliente_schema: ClienteSchema, session: Session = Depends(criar_sessao)):
    """
    Endpoint para criar um novo cliente
    """
    cliente = session.query(Cliente).filter(Cliente.email==cliente_schema.email).first()
    if cliente:
        raise excecao(status_code=422, detail="Este email já está cadastrado. Verifique e tente novamente")
    else:
        senha_criptografada = bcrypt_context.hash(cliente_schema.senha)
        novo_cliente = Cliente(
            nome=cliente_schema.nome, 
            email=cliente_schema.email, 
            senha=senha_criptografada,
            rua=cliente_schema.rua,
            numero=cliente_schema.numero,
            complemento=cliente_schema.complemento,
            bairro=cliente_schema.bairro,
            cidade=cliente_schema.cidade,
            estado=cliente_schema.estado,
            cep=cliente_schema.cep
        )
        session.add(novo_cliente)
        session.commit()
        return {"mensagem": "Cliente cadastrado com sucesso!"}
    
@auth_router.post("/criar_funcionario")
async def criar_funcionario(funcionario_schema: FuncionarioSchema, session: Session = Depends(criar_sessao)):
    """
    Endpoint para criar um novo funcionário
    """
    funcionario = session.query(Funcionario).filter(Funcionario.email==funcionario_schema.email).first()
    if funcionario:
        raise excecao(status_code=422, detail="Este email já está cadastrado. Verifique e tente novamente")
    else:
        senha_criptografada = bcrypt_context.hash(funcionario_schema.senha)
        novo_funcionario = Funcionario(
            nome=funcionario_schema.nome, 
            email=funcionario_schema.email, 
            senha=senha_criptografada, 
            tipo_funcionario=funcionario_schema.tipo_funcionario, 
            id_unidade=funcionario_schema.id_unidade
        )
        session.add(novo_funcionario)
        session.commit()
        return {"mensagem": "Funcionário cadastrado com sucesso!"}