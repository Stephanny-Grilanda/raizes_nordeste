from fastapi import Depends, HTTPException
from infra.security import SECRET_KEY, ALGORITHM, oauth2_schema_cliente, oauth2_schema_funcionario
from infra import config_db
from sqlalchemy.orm import sessionmaker, Session
from domain import Cliente, Funcionario
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_bearer = HTTPBearer()

def criar_sessao():
    try:
        Session = sessionmaker(bind=config_db.database)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token_cliente(token: str = Depends(oauth2_schema_cliente), session: Session = Depends(criar_sessao)):
    """
    Verifica a validade dos tokens para clientes.
    Garante que o cliente existe e que apenas tokens com este perfil sejam aceitos para rotas de clientes.
    """
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_cliente = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "TOKEN_INVALIDO",
                "message": "Acesso negado. Verifique a validade do token.",
                "details": [],
            },
        )

    if dic_info.get("role") != "cliente":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "PERFIL_INVALIDO",
                "message": "Token inválido para este perfil. Use autenticação de cliente.",
                "details": [{"field": "role", "issue": "Perfil do token não é cliente"}],
            },
        )

    cliente = session.query(Cliente).filter(Cliente.id == id_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "ACESSO_INVALIDO",
                "message": "Cliente não encontrado para o token informado.",
                "details": [],
            },
        )
    return cliente


def verificar_token_funcionario(token: str = Depends(oauth2_schema_funcionario), session: Session = Depends(criar_sessao)):
    """
    Verifica a validade dos tokens para funcionarios.
    Garante que o funcionario existe e que apenas tokens com este perfil sejam aceitos para rotas de funcionarios.
    """
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_funcionario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "TOKEN_INVALIDO",
                "message": "Acesso negado. Verifique a validade do token.",
                "details": [],
            },
        )
    
    if dic_info.get("role") != "funcionario":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "PERFIL_INVALIDO",
                "message": "Token inválido para este perfil. Use autenticação de funcionário.",
                "details": [{"field": "role", "issue": "Perfil do token não é funcionário"}],
            },
        )

    funcionario = session.query(Funcionario).filter(Funcionario.id == id_funcionario).first()
    if not funcionario:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "ACESSO_INVALIDO",
                "message": "Funcionário não encontrado para o token informado.",
                "details": [],
            },
        )
    return funcionario

def verificar_usuario_logado(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), 
    session: Session = Depends(criar_sessao)
):
    """
    Verifica o token independentemente de ser cliente ou funcionário.
    Retorna um dicionário com a instância do usuário e o seu 'role'.
    Essencial para rotas de multicanalidade onde Atendente ou Cliente podem agir.
    """
    token = credentials.credentials
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
        role = dic_info.get("role")
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "TOKEN_INVALIDO",
                "message": "Acesso negado. Verifique a validade do token.",
                "details": [],
            },
        )

    if role == "cliente":
        usuario = session.query(Cliente).filter(Cliente.id == id_usuario).first()
    elif role == "funcionario":
        usuario = session.query(Funcionario).filter(Funcionario.id == id_usuario).first()
    else:
        raise HTTPException(status_code=401, detail="Perfil desconhecido.")

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")

    return {"usuario": usuario, "role": role}