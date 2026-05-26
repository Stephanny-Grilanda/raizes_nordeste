from fastapi import APIRouter, Depends, HTTPException as excecao
from domain.cliente import Cliente
from domain.funcionario import Funcionario
from infra.dependencies import criar_sessao, verificar_token_cliente, verificar_token_funcionario
from infra.security import bcrypt_context,SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from domain.schemas import ClienteSchema, FuncionarioSchema, LoginSchema
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from infra.security import criar_token

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
async def criar_funcionario(funcionario_schema: FuncionarioSchema, session: Session = Depends(criar_sessao), funcionario_logado: Funcionario = Depends(verificar_token_funcionario)):
    """
    Endpoint para criar um novo funcionário
    """
    if funcionario_logado.tipo_funcionario not in [funcionario_schema.tipo_funcionario.ADMIN, funcionario_schema.tipo_funcionario.GERENTE]:
        raise excecao(status_code=403, detail="Você não tem permissão para cadastrar funcionários.")
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



def autenticar_cliente(email, senha, session):
    cliente = session.query(Cliente).filter(Cliente.email==email).first()
    if not cliente:
        return False
    elif not bcrypt_context.verify(senha, cliente.senha):
        return False
    return cliente

@auth_router.post("/login-cliente")
async def login(login_schema: LoginSchema, session: Session = Depends(criar_sessao)):
    cliente = autenticar_cliente(login_schema.email, login_schema.senha, session)
    if not cliente:
        raise excecao(status_code=422, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(cliente.id)
        refresh_token = criar_token(cliente.id, duracao_token=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
            }
    
def autenticar_funcionario(email, senha, session):
    funcionario = session.query(Funcionario).filter(Funcionario.email==email).first()
    if not funcionario:
        return False
    elif not bcrypt_context.verify(senha, funcionario.senha):
        return False
    return funcionario

@auth_router.post("/login-funcionario")
async def login(login_schema: LoginSchema, session: Session = Depends(criar_sessao)):
    funcionario = autenticar_funcionario(login_schema.email, login_schema.senha, session)
    if not funcionario:
        raise excecao(status_code=422, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(funcionario.id, funcionario=True)
        refresh_token = criar_token(funcionario.id, duracao_token=timedelta(days=7), funcionario=True)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
            }
    
@auth_router.post("/login-form-cliente")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(criar_sessao)):
    usuario = autenticar_cliente(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise excecao(status_code=422, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
            }


@auth_router.get("/refresh-cliente")
async def use_refresh_token(cliente: Cliente = Depends(verificar_token_cliente)):
    access_token = criar_token(cliente.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
        }

@auth_router.post("/login-form-funcionario")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(criar_sessao)):
    usuario = autenticar_funcionario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise excecao(status_code=422, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(usuario.id, funcionario=True)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
            }


@auth_router.get("/refresh-funcionario")
async def use_refresh_token(funcionario: Funcionario = Depends(verificar_token_funcionario)):
    access_token = criar_token(funcionario.id, funcionario=True)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
        }