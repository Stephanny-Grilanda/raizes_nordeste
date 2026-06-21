# importação libs

from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from datetime import datetime, timezone


# importação rotas da api

from api.routes import auth_routes
from api.routes import order_routes
from api.routes import payment_routes

load_dotenv()

app = FastAPI(
    title="API Raízes do Nordeste",
    description="""
API para o projeto Raízes do Nordeste, uma rede de restaurantes com comidas típicas do Nordeste.

A API possui rotas responsáveis por realizar o registro e autenticação de usuários, realizar e listar pedidos e processar pagamentos.
    """,
    version="1.0.0",
)

def _mapear_codigos_erro(status_code: int) -> str:
    """Função para mapear e padronizar mensagens de erro de acordo com o status HTTP."""
    codigos_erro = {
        400: "REQUISIÇÃO INVALIDA",
        401: "USUARIO NÃO AUTENTICADO",
        403: "ACESSO NEGADO",
        404: "RECURSO NÃO ENCONTRADO",
        409: "CONFLITO DE RECURSO",
        422: "ERRO DE VALIDACAO",
    }

    return codigos_erro.get(status_code, "ERRO INTERNO")

@app.exception_handler(HTTPException)
async def tratar_excecao(request: Request, exc: HTTPException):
    """Garante que as mensagens de erro retorne um json padronizado."""
    if isinstance(exc.detail, dict):
        codigo_erro = exc.detail.get("error", _mapear_codigos_erro(exc.status_code))
        mensagem = exc.detail.get("message", "Ocorreu um erro durante a requisição.")
        detalhes = exc.detail.get("details", [])
    else:
        codigo_erro = _mapear_codigos_erro(exc.status_code)
        mensagem = str(exc.detail) if exc.detail else "Ocorreu um erro durante a requisição."
        detalhes = []
    
    return JSONResponse(
        status_code = exc.status_code,
        content = {
            "error": {
                "error": codigo_erro,
                "message": mensagem,
                "details": detalhes,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": str(request.url.path)
            },
        }
    )

app.include_router(auth_routes.auth_router)
app.include_router(order_routes.order_router)
app.include_router(payment_routes.payment_router)

@app.get("/")
def root():
    return {"message": "Projeto Raízes do Nordeste! Acesse /docs para consultar a documentação da API."}