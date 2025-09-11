# core/model/model_trainer.py
import pandas as pd
import pickle
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_PATH = Path('model/')
MODEL_NAME = 'movie_recommender.pkl'

def train_and_save_model(engine):
    """Treina e salva o modelo de recomendação usando um engine SQLAlchemy."""
    logging.info("Iniciando o treinamento do modelo de recomendação...")

    query = """
            SELECT m.title, GROUP_CONCAT(g.genre_name, ' ') as genres
            FROM sot_movies_clean m JOIN sot_movie_genres g ON m.movie_id = g.movie_id
            GROUP BY m.title; \
            """

    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)

    if df.empty:
        logging.error("Não foi possível treinar o modelo. O DataFrame está vazio.")
        return

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['genres'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    MODEL_PATH.mkdir(parents=True, exist_ok=True)
    recommendation_data = {'cosine_sim': cosine_sim, 'dataframe': df}

    with open(MODEL_PATH / MODEL_NAME, 'wb') as f:
        pickle.dump(recommendation_data, f)

    logging.info(f"Modelo salvo com sucesso na pasta '{MODEL_PATH}'")

def load_recommendation_data():
    """Carrega os dados de recomendação do arquivo pickle."""
    model_file = MODEL_PATH / MODEL_NAME
    if not model_file.exists():
        logging.error(f"Arquivo do modelo não encontrado em '{model_file}'.")
        return None, None

    try:
        with open(model_file, 'rb') as f:
            data = pickle.load(f)
        logging.info("Modelo de recomendação carregado do arquivo pickle.")
        return data['cosine_sim'], data['dataframe']
    except Exception as e:
        logging.error(f"Erro ao carregar o arquivo do modelo: {e}")
        return None, None