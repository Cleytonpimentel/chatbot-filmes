# core/database_manager.py
import pandas as pd
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def recreate_database(engine, metadata):
    """Dropa todas as tabelas e as cria novamente a partir dos metadados."""
    try:
        logging.info("Iniciando a recriação do banco de dados...")
        metadata.drop_all(engine)
        metadata.create_all(engine)
        logging.info("Banco de dados recriado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao recriar o banco de dados: {e}")
        raise

def execute_sql_from_file(engine, filepath):
    """Executa um script SQL a partir de um arquivo."""
    try:
        with open(filepath, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        with engine.connect() as connection:
            connection.execute(text(sql_script))
            connection.commit() # SQLAlchemy 2.0 style commit

        logging.info(f"SQL script '{filepath}' executado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao executar o script SQL '{filepath}': {e}")
        raise

def run_data_pipeline(engine, csv_path, sor_table_name, spec_script_path):
    """Executa o pipeline completo: CSV -> SOR -> SOT -> SPEC."""
    from core.data_processing import process_and_normalize_data # Importação local

    logging.info("Iniciando pipeline de dados...")

    # 1. Inserir CSV na SOR
    try:
        colunas_necessarias = ['id', 'title', 'genres', 'vote_average', 'vote_count']
        df_sor = pd.read_csv(csv_path, usecols=colunas_necessarias)
        df_sor.to_sql(sor_table_name, engine, if_exists='replace', index=False)
        logging.info(f"Dados de '{csv_path}' inseridos na tabela '{sor_table_name}'.")
    except Exception as e:
        logging.error(f"Falha ao inserir CSV na SOR: {e}")
        raise

    # 2. Processar SOR para SOT
    process_and_normalize_data(engine)

    # 3. Criar a tabela SPEC a partir da SOT
    execute_sql_from_file(engine, spec_script_path)

    logging.info("Pipeline de dados concluído com sucesso.")


def query_db(engine, query, params=None):
    """Executa uma query e retorna os resultados como DataFrame."""
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(query), connection, params=params)
        return df
    except Exception as e:
        logging.error(f"Erro ao executar a query: {e}")
        return None