import logging
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.cliente import Cliente
from domain.funcionario import Funcionario
from domain.schemas import ClienteSchema, FuncionarioSchema, LoginSchema
from domain.enums import TipoFuncionario
from infra.security import bcrypt_context, criar_token

# rotas de autenticação, criação de usuários (clientes e funcionários) e auditoria.


logger_auditoria = logging.getLogger("auditoria.autenticacao")
if not logger_auditoria.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger_auditoria.addHandler(handler)
    logger_auditoria.setLevel(logging.INFO)


def criar_cliente(cliente_schema: ClienteSchema, session: Session) -> dict:
    """
    Caso de uso: cadastrar novo cliente com senha hasheada (LGPD — armazenamento seguro).
    """
    cliente_existente = session.query(Cliente).filter(
        (Cliente.email == cliente_schema.email) | 
        (Cliente.documento == cliente_schema.documento)
    ).first()

    if cliente_existente:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "DADOS_JA_CADASTRADOS",
                "message": "E-mail ou documento já cadastrado. Verifique e tente novamente.",
                "details": [{"field": "email/documento", "issue": "Já em uso"}],
            },
        )

    senha_criptografada = bcrypt_context.hash(cliente_schema.senha)

    novo_cliente = Cliente(
        nome=cliente_schema.nome,
        documento=cliente_schema.documento,
        email=cliente_schema.email,
        senha=senha_criptografada,
        rua=cliente_schema.rua,
        numero=cliente_schema.numero,
        complemento=cliente_schema.complemento,
        bairro=cliente_schema.bairro,
        cidade=cliente_schema.cidade,
        estado=cliente_schema.estado,
        cep=cliente_schema.cep,
    )

    session.add(novo_cliente)
    session.commit()
    session.refresh(novo_cliente)

    # Log de auditoria: registra cadastro sem expor senha ou dados sensíveis completos
    logger_auditoria.info(
        "Novo cliente cadastrado | acao=CRIAR_CLIENTE | id_cliente=%s | email=%s",
        novo_cliente.id,
        novo_cliente.email,
    )

    return novo_cliente


def criar_funcionario(
    funcionario_schema: FuncionarioSchema,
    funcionario_logado: Funcionario,
    session: Session,
) -> dict:
    """
    Caso de uso: cadastrar funcionário — apenas ADMIN ou GERENTE podem executar (autorização por role).
    """
    if funcionario_logado.tipo_funcionario == TipoFuncionario.GERENTE:
        if funcionario_logado.id_unidade != funcionario_schema.id_unidade:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "ACESSO_NEGADO",
                    "message": "Gerentes só podem cadastrar funcionários para a sua própria unidade.",
                    "details": [{"field": "id_unidade", "issue": "Cadastro não liberado para esta unidade"}],
                },
            )

    funcionario_existente = (
        session.query(Funcionario).filter(Funcionario.email == funcionario_schema.email).first()
    )

    if funcionario_existente:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "EMAIL_JA_CADASTRADO",
                "message": "Este email já está cadastrado. Verifique e tente novamente.",
                "details": [{"field": "email", "issue": "E-mail já em uso"}],
            },
        )

    senha_criptografada = bcrypt_context.hash(funcionario_schema.senha)

    novo_funcionario = Funcionario(
        nome=funcionario_schema.nome,
        email=funcionario_schema.email,
        senha=senha_criptografada,
        tipo_funcionario=funcionario_schema.tipo_funcionario,
        id_unidade=funcionario_schema.id_unidade,
    )

    session.add(novo_funcionario)
    session.commit()
    session.refresh(novo_funcionario)

    logger_auditoria.info(
        "Novo funcionário cadastrado | acao=CRIAR_FUNCIONARIO | id_funcionario=%s | "
        "tipo=%s | cadastrado_por=%s",
        novo_funcionario.id,
        novo_funcionario.tipo_funcionario.value,
        funcionario_logado.id,
    )

    return novo_funcionario


def autenticar_cliente(email: str, senha: str, session: Session) -> Cliente | None:
    """Valida credenciais do cliente no banco (e-mail + senha com bcrypt)."""
    cliente = session.query(Cliente).filter(Cliente.email == email).first()

    if not cliente or not bcrypt_context.verify(senha, cliente.senha):
        return None

    return cliente


def autenticar_funcionario(email: str, senha: str, session: Session) -> Funcionario | None:
    """Valida credenciais do funcionário no banco (e-mail + senha com bcrypt)."""
    funcionario = session.query(Funcionario).filter(Funcionario.email == email).first()

    if not funcionario or not bcrypt_context.verify(senha, funcionario.senha):
        return None

    return funcionario


def _gerar_tokens_cliente(id_cliente: int, incluir_refresh: bool = True) -> dict:
    """Gera access_token e, opcionalmente, refresh_token para cliente."""
    access_token = criar_token(id_cliente)
    resposta = {
        "access_token": access_token,
        "token_type": "Bearer",
    }

    if incluir_refresh:
        resposta["refresh_token"] = criar_token(id_cliente, duracao_token=timedelta(days=7))

    return resposta


def _gerar_tokens_funcionario(id_funcionario: int, incluir_refresh: bool = True) -> dict:
    """Gera access_token e, opcionalmente, refresh_token para funcionário."""
    access_token = criar_token(id_funcionario, funcionario=True)
    resposta = {
        "access_token": access_token,
        "token_type": "Bearer",
    }

    if incluir_refresh:
        resposta["refresh_token"] = criar_token(
            id_funcionario, duracao_token=timedelta(days=7), funcionario=True
        )

    return resposta


def login_cliente(login_schema: LoginSchema, session: Session) -> dict:
    """
    Caso de uso: login de cliente via JSON (email + senha).
    Retorna tokens JWT em caso de sucesso.
    """
    cliente = autenticar_cliente(login_schema.email, login_schema.senha, session)

    if not cliente:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "CREDENCIAIS_INVALIDAS",
                "message": "Usuário não encontrado ou credenciais inválidas.",
                "details": [{"field": "email", "issue": "E-mail ou senha incorretos"}],
            },
        )

    logger_auditoria.info(
        "Login de cliente realizado | acao=LOGIN_CLIENTE | id_cliente=%s",
        cliente.id,
    )

    return _gerar_tokens_cliente(cliente.id)


def login_funcionario(login_schema: LoginSchema, session: Session) -> dict:
    """
    Caso de uso: login de funcionário via JSON (email + senha).
    Retorna tokens JWT em caso de sucesso.
    """
    funcionario = autenticar_funcionario(login_schema.email, login_schema.senha, session)

    if not funcionario:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "CREDENCIAIS_INVALIDAS",
                "message": "Usuário não encontrado ou credenciais inválidas.",
                "details": [{"field": "email", "issue": "E-mail ou senha incorretos"}],
            },
        )

    logger_auditoria.info(
        "Login de funcionário realizado | acao=LOGIN_FUNCIONARIO | id_funcionario=%s | tipo=%s",
        funcionario.id,
        funcionario.tipo_funcionario.value,
    )

    return _gerar_tokens_funcionario(funcionario.id)


def login_form_cliente(email: str, senha: str, session: Session) -> dict:
    """
    Caso de uso: login de cliente via OAuth2PasswordRequestForm (compatível com Swagger Authorize).
    """
    cliente = autenticar_cliente(email, senha, session)

    if not cliente:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "CREDENCIAIS_INVALIDAS",
                "message": "Usuário não encontrado ou credenciais inválidas.",
                "details": [{"field": "username", "issue": "E-mail ou senha incorretos"}],
            },
        )

    logger_auditoria.info(
        "Login de cliente via form realizado | acao=LOGIN_FORM_CLIENTE | id_cliente=%s",
        cliente.id,
    )

    return _gerar_tokens_cliente(cliente.id, incluir_refresh=False)


def login_form_funcionario(email: str, senha: str, session: Session) -> dict:
    """
    Caso de uso: login de funcionário via OAuth2PasswordRequestForm (compatível com Swagger Authorize).
    """
    funcionario = autenticar_funcionario(email, senha, session)

    if not funcionario:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "CREDENCIAIS_INVALIDAS",
                "message": "Usuário não encontrado ou credenciais inválidas.",
                "details": [{"field": "username", "issue": "E-mail ou senha incorretos"}],
            },
        )

    logger_auditoria.info(
        "Login de funcionário via form realizado | acao=LOGIN_FORM_FUNCIONARIO | id_funcionario=%s",
        funcionario.id,
    )

    return _gerar_tokens_funcionario(funcionario.id, incluir_refresh=False)


def refresh_token_cliente(cliente: Cliente) -> dict:
    """Renova o access_token de um cliente já autenticado via refresh token."""
    logger_auditoria.info(
        "Refresh token de cliente | acao=REFRESH_CLIENTE | id_cliente=%s",
        cliente.id,
    )
    return _gerar_tokens_cliente(cliente.id, incluir_refresh=False)


def refresh_token_funcionario(funcionario: Funcionario) -> dict:
    """Renova o access_token de um funcionário já autenticado via refresh token."""
    logger_auditoria.info(
        "Refresh token de funcionário | acao=REFRESH_FUNCIONARIO | id_funcionario=%s",
        funcionario.id,
    )
    return _gerar_tokens_funcionario(funcionario.id, incluir_refresh=False)
