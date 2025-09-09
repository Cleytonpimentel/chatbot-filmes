# core/config.py
from sqlalchemy import create_engine

# Usando SQLite por padrão, mas pode ser trocado por PostgreSQL, MySQL, etc.
# Ex: "postgresql://user:password@host:port/database"
DATABASE_URL = "sqlite:///movies_database.db"

# O Engine é o ponto central de comunicação com o banco de dados.
engine = create_engine(DATABASE_URL)