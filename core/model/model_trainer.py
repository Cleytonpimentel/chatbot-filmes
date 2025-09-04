# core/model_trainer.py

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import core.database_manager as db
import os

MODEL_PATH = 'model/'
MODEL_NAME = 'movie_recommender.pkl'
VECTORIZER_NAME = 'tfidf_vectorizer.pkl'
DF_NAME = 'movies_df.pkl'

def train_and_save_model():
    """
    Treina um modelo de recomendação baseado em conteúdo (gêneros)
    e o salva em arquivos pickle.
    """
    print("Iniciando o treinamento do modelo de recomendação...")

    # 1. Obter os dados já processados
    # Agrupamos os gêneros de cada filme em uma única string
    query = """
            SELECT m.title, GROUP_CONCAT(g.genre_name, ' ') as genres
            FROM sot_movies_clean m
                     JOIN sot_movie_genres g ON m.movie_id = g.movie_id
            GROUP BY m.title; \
            """
    df = db.query_db(query)

    if df.empty:
        print("Não foi possível treinar o modelo. O DataFrame está vazio.")
        return

    # 2. Criar a matriz TF-IDF a partir dos gêneros
    # TfidfVectorizer transforma texto em uma matriz de features numéricas
    tfidf = TfidfVectorizer(stop_words=None)
    tfidf_matrix = tfidf.fit_transform(df['genres'])

    # 3. Calcular a similaridade de cosseno
    # O kernel linear calcula a similaridade entre todos os filmes
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # 4. Salvar o modelo e os dados necessários
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH)

    recommendation_data = {
        'cosine_sim': cosine_sim,
        'dataframe': df
    }

    with open(os.path.join(MODEL_PATH, MODEL_NAME), 'wb') as f:
        pickle.dump(recommendation_data, f)

    with open(os.path.join(MODEL_PATH, VECTORIZER_NAME), 'wb') as f:
        pickle.dump(tfidf, f)

    print(f"Modelo salvo com sucesso na pasta '{MODEL_PATH}'")

def load_recommendation_data():
    """Carrega os dados de recomendação dos arquivos pickle."""
    try:
        with open(os.path.join(MODEL_PATH, MODEL_NAME), 'rb') as f:
            data = pickle.load(f)
        return data['cosine_sim'], data['dataframe']
    except FileNotFoundError:
        return None, None