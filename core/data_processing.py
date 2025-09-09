# core/data_processing.py
import pandas as pd
import json
import logging

MIN_VOTE_COUNT = 500

def _parse_json_genres(genre_str):
    """Função auxiliar para converter a string JSON de gêneros em uma lista de nomes."""
    try:
        genres_list = json.loads(genre_str)
        return [genre['name'] for genre in genres_list if isinstance(genre, dict) and 'name' in genre]
    except (json.JSONDecodeError, TypeError):
        return []

def process_and_normalize_data(engine):
    """Lê da SOR, normaliza os dados e insere na SOT usando um engine SQLAlchemy."""
    logging.info("Iniciando processo de normalização de dados (SOR -> SOT).")

    try:
        # 1. Ler dados brutos da SOR
        query = f"SELECT id, title, genres, vote_average FROM sor_movies WHERE vote_count >= {MIN_VOTE_COUNT}"
        df_sor = pd.read_sql_query(query, engine)

        # 2. Popular a tabela sot_movies_clean
        df_sot_movies = df_sor[['id', 'title', 'vote_average']].rename(columns={'id': 'movie_id'})
        df_sot_movies.to_sql('sot_movies_clean', engine, if_exists='replace', index=False)
        logging.info(f"Tabela 'sot_movies_clean' populada com {len(df_sot_movies)} filmes.")

        # 3. Processar e normalizar os gêneros
        df_genres_raw = df_sor[['id', 'genres']].dropna(subset=['genres'])
        df_genres_raw['genres_list'] = df_genres_raw['genres'].apply(_parse_json_genres)
        df_genres_normalized = df_genres_raw.explode('genres_list')

        df_final_genres = df_genres_normalized[['id', 'genres_list']].rename(columns={'id': 'movie_id', 'genres_list': 'genre_name'})
        df_final_genres.dropna(subset=['genre_name'], inplace=True)
        df_final_genres.drop_duplicates(inplace=True)

        df_final_genres.to_sql('sot_movie_genres', engine, if_exists='replace', index=False)
        logging.info(f"Tabela 'sot_movie_genres' populada com {len(df_final_genres)} relações filme-gênero.")

    except Exception as e:
        logging.error(f"Um erro ocorreu durante a normalização: {e}")
        raise