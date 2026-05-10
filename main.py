# importação libs

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# importação rotas da api

from api.routes import auth_routes
from api.routes import order_routes

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

app.include_router(auth_routes.auth_router)
app.include_router(order_routes.order_router)

@app.get("/")
def root():
    return {"message": "Bem-vindo ao Raízes do Nordeste!"}