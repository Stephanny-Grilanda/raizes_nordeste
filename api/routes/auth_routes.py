from fastapi import APIRouter, Depends
from domain.usuario import Usuario
from infra.dependencies import criar_sessao
from domain.enums import TipoUsuario
from infra.security import bcrypt_context

auth_router = APIRouter(prefix="/autenticacao", tags=["autenticacao"])

@auth_router.get("/")
async def autenticacao_padrao():
    """
    Endpoint padrão para autenticação no sistema
    """
    return {"mensagem": "Você está na rota de autenticação!", "autenticado": False}

@auth_router.post("/criar_usuario")
async def criar_usuario(email: str, senha: str, nome: str, tipo_usuario: TipoUsuario, session=Depends(criar_sessao)):
    """
    Endpoint para criar um novo usuário
    """
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if usuario:
        return {"mensagem": "Já existe um usuario com esse email."}
    else:
        senha_criptografada = bcrypt_context.hash(senha)
        novo_usuario = Usuario(nome, email, senha_criptografada, tipo_usuario)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": "Usuário cadastrado com sucesso!"}