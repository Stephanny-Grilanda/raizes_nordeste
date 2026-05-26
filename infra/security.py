from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
load_dotenv()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema_cliente = OAuth2PasswordBearer(tokenUrl="autenticacao/login-form-cliente", scheme_name="login_cliente")
oauth2_schema_funcionario = OAuth2PasswordBearer(tokenUrl="autenticacao/login-form-funcionario", scheme_name="login_funcionario")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), funcionario:bool=False):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao, "role": "funcionario" if funcionario else "cliente"}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado