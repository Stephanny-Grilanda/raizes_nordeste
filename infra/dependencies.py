from infra.config_db import database
from sqlalchemy.orm import sessionmaker

def criar_sessao():
    try:
        Session = sessionmaker(bind=database)
        session = Session()
        yield session
    finally:
        session.close()