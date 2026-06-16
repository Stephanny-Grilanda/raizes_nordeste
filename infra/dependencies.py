from fastapi import Depends, HTTPException
from infra.security import SECRET_KEY, ALGORITHM, oauth2_schema_cliente, oauth2_schema_funcionario
from infra import config_db
from sqlalchemy.orm import sessionmaker, Session
from domain import Cliente, Funcionario
from jose import jwt, JWTError

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
