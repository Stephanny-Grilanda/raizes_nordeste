# OBSERVAÇÃO - ARQUIVO GERADO COM INTELIGÊNCIA ARTIFICIAL PARA POPULAR O BANCO DE DADOS E SERVIR DE TESTE PARA O PROJETO.
# APÓS CRIAR O BANCO DE DADOS, RODE ESTE SCRIPT PARA INSERIR DADOS FICTÍCIOS E PODER TESTAR AS FUNCIONALIDADES DA API.

from sqlalchemy.orm import Session
from infra.config_db import database
from sqlalchemy.orm import sessionmaker
from domain import Cliente, Funcionario, Unidade, Produto, Estoque
from domain.enums import TipoFuncionario
from infra.security import bcrypt_context
import random

# Configuração da Sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database)
session = SessionLocal()

def popular():
    print("Iniciando a população do banco de dados...")

    # 1. Criar 5 Unidades (uma em cada região)
    regioes = [
        {"nome": "Norte", "cidade": "Manaus", "estado": "AM"},
        {"nome": "Nordeste", "cidade": "Recife", "estado": "PE"},
        {"nome": "Centro-Oeste", "cidade": "Brasília", "estado": "DF"},
        {"nome": "Sudeste", "cidade": "São Paulo", "estado": "SP"},
        {"nome": "Sul", "cidade": "Curitiba", "estado": "PR"}
    ]
    
    unidades_db = []
    for reg in regioes:
        u = Unidade(
            rua=f"Rua da Unidade {reg['nome']}",
            numero=str(random.randint(1, 1000)),
            bairro="Centro",
            cidade=reg['cidade'],
            estado=reg['estado'],
            cep="00000-000"
        )
        session.add(u)
        unidades_db.append((u, reg['nome']))
    
    session.flush() # Gerar IDs das unidades

    # 2. Criar 20 Clientes (4 por região)
    senha_padrao = bcrypt_context.hash("senha123")
    for unidade_obj, reg_nome in unidades_db:
        for i in range(1, 5):
            c = Cliente(
                nome=f"Cliente {i} do {reg_nome}",
                email=f"cliente{i}.{reg_nome.lower()}@email.com",
                senha=senha_padrao,
                cidade=unidade_obj.cidade,
                estado=unidade_obj.estado
            )
            session.add(c)

    # 3. Criar 6 funcionários por loja
    # (1 Gerente, 3 Cozinheiros, 2 Atendentes)
    for unidade_obj, reg_nome in unidades_db:
        # 1 Gerente
        session.add(Funcionario(f"Gerente {reg_nome}", f"gerente.{reg_nome.lower()}@loja.com", senha_padrao, TipoFuncionario.GERENTE, unidade_obj.id))
        # 3 Cozinheiros
        for i in range(1, 4):
            session.add(Funcionario(f"Cozinheiro {i} {reg_nome}", f"chef{i}.{reg_nome.lower()}@loja.com", senha_padrao, TipoFuncionario.COZINHA, unidade_obj.id))
        # 2 Atendentes
        for i in range(1, 3):
            session.add(Funcionario(f"Atendente {i} {reg_nome}", f"atendente{i}.{reg_nome.lower()}@loja.com", senha_padrao, TipoFuncionario.ATENDENTE, unidade_obj.id))

    # 4. Criar 50 Produtos
    produtos_db = []
    
    # 10 Bebidas
    for i in range(1, 11):
        p = Produto(f"Bebida {i}", "Descrição da bebida", "Bebida", round(random.uniform(5, 15), 2))
        session.add(p)
        produtos_db.append(p)
        
    # 20 Pratos Salgados (Geral)
    for i in range(1, 21):
        p = Produto(f"Prato Salgado {i}", "Descrição do prato", "Salgado", round(random.uniform(25, 60), 2))
        session.add(p)
        produtos_db.append(p)

    # 10 Sobremesas
    for i in range(1, 11):
        p = Produto(f"Sobremesa {i}", "Descrição da sobremesa", "Sobremesa", round(random.uniform(10, 25), 2))
        session.add(p)
        produtos_db.append(p)

    # 10 Pratos Tipicamente Nordestinos
    pratos_ne = ["Baião de Dois", "Moqueca", "Vatapá", "Acarajé", "Carne de Sol", "Sarapatel", "Buchada", "Paçoca de Carne", "Tapioca Recheada", "Cuscuz Nordestino"]
    produtos_ne_obj = []
    for nome_ne in pratos_ne:
        p = Produto(nome_ne, f"Prato típico do Nordeste: {nome_ne}", "Especial Nordeste", round(random.uniform(30, 70), 2))
        session.add(p)
        produtos_ne_obj.append(p)
        produtos_db.append(p)

    session.flush()

    # 5. Estoque variável
    # Apenas a loja do Nordeste deve ter os pratos especiais
    for unidade_obj, reg_nome in unidades_db:
        for p in produtos_db:
            # Regra: Se for prato especial NE e não for a loja NE, pula
            if p.categoria == "Especial Nordeste" and reg_nome != "Nordeste":
                continue
            
            qtd = random.randint(10, 100)
            session.add(Estoque(qtd, p.id, unidade_obj.id))

    session.commit()
    print("Banco de dados populado com sucesso!")

if __name__ == "__main__":
    popular()