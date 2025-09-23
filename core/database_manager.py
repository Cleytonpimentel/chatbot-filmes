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

    if columns:
        df_to_insert = df[columns]
    else:
        df_to_insert = df

    conn = sqlite3.connect(DB_NAME)
    df_to_insert.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Dados de '{csv_path}' inseridos na tabela '{table_name}'.")

def query_db(query, params=None):
    """
    Executa uma query SQL e retorna os resultados como DataFrame.
    Permite passar parâmetros para queries com placeholders (ex.: ?).

    Args:
        query (str): SQL query a ser executada.
        params (tuple, optional): Parâmetros para a query.

    Returns:
        pd.DataFrame: Resultado da query ou DataFrame vazio em caso de erro.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        # Escapa colunas reservadas automaticamente se estiverem entre aspas
        df = pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        print(f"Erro ao executar query: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def drop_database():
    """Remove o arquivo do banco de dados."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Database '{DB_NAME}' removido com sucesso.")
