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
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_cliente= int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    cliente = session.query(Cliente).filter(Cliente.id==id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return cliente


def verificar_token_funcionario(token: str = Depends(oauth2_schema_funcionario), session: Session = Depends(criar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_funcionario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    funcionario = session.query(Funcionario).filter(Funcionario.id==id_funcionario).first()
    if not funcionario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return funcionario
