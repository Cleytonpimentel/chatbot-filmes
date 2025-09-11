# core/database_manager.py

import sqlite3
import pandas as pd
import os

DB_NAME = "movies_database.db"

def execute_sql_from_file(filepath):
    """Executa um script SQL a partir de um arquivo."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    with open(filepath, 'r', encoding='utf-8') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print(f"SQL script '{filepath}' executado com sucesso.")

def insert_csv_to_db(csv_path, table_name, columns=None):
    """Lê um CSV, seleciona colunas específicas (se fornecido) e insere na tabela."""
    df = pd.read_csv(csv_path)

    # Se uma lista de colunas for fornecida, usa apenas elas
    if columns:
        df_to_insert = df[columns]
    else:
        df_to_insert = df

    conn = sqlite3.connect(DB_NAME)
    df_to_insert.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Dados de '{csv_path}' inseridos na tabela '{table_name}'.")

def query_db(query):
    """Executa uma query e retorna os resultados como DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def drop_database():
    """Remove o arquivo do banco de dados."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Database '{DB_NAME}' removido com sucesso.")