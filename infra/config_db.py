from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

database = create_engine("sqlite:///infra/raizes_nordeste.db")

Base = declarative_base()
