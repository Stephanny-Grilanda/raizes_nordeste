from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from domain.cliente import Cliente
from domain.funcionario import Funcionario
from domain.schemas import ClienteSchema, FuncionarioSchema, LoginSchema, ClienteResponseSchema, FuncionarioResponseSchema
from infra.dependencies import criar_sessao, verificar_token_cliente, verificar_token_funcionario
from api.services import auth_service


auth_router = APIRouter(prefix="/autenticacao", tags=["autenticacao"])

@auth_router.get("/")
async def autenticacao_padrao():
    """
    Endpoint padrão para autenticação no sistema
    """
    return {"mensagem": "Você está na rota de autenticação!", "autenticado": False}


@auth_router.post(
    "/criar_cliente",
    status_code=status.HTTP_201_CREATED,
    response_model=ClienteResponseSchema,
    #response_model_exclude_none=True,
    summary="Cadastrar cliente",
    responses={
        201: {"description": "Cliente cadastrado com sucesso"},
        422: {"description": "E-mail já cadastrado ou dados inválidos"},
    },
)
async def criar_cliente(
    cliente_schema: ClienteSchema,
    session: Session = Depends(criar_sessao),
):
    """Endpoint para criar um novo cliente — delega ao service."""
    return auth_service.criar_cliente(cliente_schema, session)


@auth_router.post(
    "/criar_funcionario",
    status_code=status.HTTP_201_CREATED,
    response_model=FuncionarioResponseSchema,
    #response_model_exclude_none=True,
    summary="Cadastrar funcionário",
    responses={
        201: {"description": "Funcionário cadastrado com sucesso"},
        403: {"description": "Perfil sem permissão, apenas ADMIN e GERENTE podem criar funcionários"},
        422: {"description": "E-mail já cadastrado ou dados inválidos"},
    },
)
async def criar_funcionario(
    funcionario_schema: FuncionarioSchema,
    session: Session = Depends(criar_sessao),
    funcionario_logado: Funcionario = Depends(verificar_token_funcionario),
):
    """Rota bloqueada para clientes, atendentes e cozinha.
    
    Gerentes podem criar apenas funcionários dos tipos ATENDENTE e COZINHA, enquanto Admins podem criar funcionários de qualquer tipo.

    Gerentes só podem criar funcionários de sua própria unidade."""
    return auth_service.criar_funcionario(funcionario_schema, funcionario_logado, session)


@auth_router.post(
    "/login-cliente",
    summary="Login de cliente (JSON)",
    responses={
        200: {"description": "Login realizado com sucesso."},
        422: {"description": "Credenciais inválidas"},
    },
)
async def login_cliente(
    login_schema: LoginSchema,
    session: Session = Depends(criar_sessao),
):
    """Login de cliente via body JSON — delega ao service."""
    return auth_service.login_cliente(login_schema, session)


@auth_router.post(
    "/login-funcionario",
    summary="Login de funcionário (JSON)",
    responses={
        200: {"description": "Login realizado com sucesso."},
        422: {"description": "Credenciais inválidas"},
    },
)
async def login_funcionario(
    login_schema: LoginSchema,
    session: Session = Depends(criar_sessao),
):
    """Login de funcionário via body JSON — delega ao service."""
    return auth_service.login_funcionario(login_schema, session)


@auth_router.post(
    "/login-form-cliente",
    summary="Login de cliente (OAuth2 Form — Swagger Authorize)",
    responses={
        200: {"description": "Login realizado com sucesso."},
        422: {"description": "Credenciais inválidas"},
    },
)
async def login_form_cliente(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(criar_sessao),
):
    """
    Login via formulário OAuth2 — usado pelo botão Authorize do Swagger.
    Delega ao service.
    """
    return auth_service.login_form_cliente(
        dados_formulario.username,
        dados_formulario.password,
        session,
    )


@auth_router.get(
    "/refresh-cliente",
    summary="Renovar token de cliente",
    responses={
        200: {"description": "Novo access_token gerado"},
        401: {"description": "Token inválido ou expirado"},
    },
)
async def refresh_cliente(cliente: Cliente = Depends(verificar_token_cliente)):
    """Renova access_token do cliente autenticado — delega ao service."""
    return auth_service.refresh_token_cliente(cliente)


@auth_router.post(
    "/login-form-funcionario",
    summary="Login de funcionário (OAuth2 Form — Swagger Authorize)",
    responses={
        200: {"description": "Login realizado — retorna access_token"},
        422: {"description": "Credenciais inválidas"},
    },
)
async def login_form_funcionario(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(criar_sessao),
):
    """Login de funcionário via formulário OAuth2 — delega ao service."""
    return auth_service.login_form_funcionario(
        dados_formulario.username,
        dados_formulario.password,
        session,
    )


@auth_router.get(
    "/refresh-funcionario",
    summary="Renovar token de funcionário",
    responses={
        200: {"description": "Novo access_token gerado"},
        401: {"description": "Token inválido ou expirado"},
    },
)
async def refresh_funcionario(funcionario: Funcionario = Depends(verificar_token_funcionario)):
    """Renova access_token do funcionário autenticado — delega ao service."""
    return auth_service.refresh_token_funcionario(funcionario)
