import pandas as pd
import sqlite3
import json

DB_NAME = "movies_database.db"
MIN_VOTE_COUNT = 500 # Filtro de relevância para filmes significativos

def process_and_normalize_data():
    """
    Função principal que transforma os dados da SOR para SOT.
    """
    conn = sqlite3.connect(DB_NAME)

    # 1. Ler dados brutos da SOR e aplicar o filtro de relevância
    df_sor = pd.read_sql_query(
        f"SELECT id, title, genres, vote_average FROM sor_movies WHERE vote_count >= {MIN_VOTE_COUNT}",
        conn
    )

    # 2. Popular a tabela sot_movies_clean
    df_sot_movies = df_sor[['id', 'title', 'vote_average']].rename(columns={'id': 'movie_id'})
    df_sot_movies.to_sql('sot_movies_clean', conn, if_exists='replace', index=False)
    print(f"Tabela 'sot_movies_clean' populada com {len(df_sot_movies)} filmes.")

    # 3. Processar e normalizar os gêneros para popular sot_movie_genres
    df_sor.dropna(subset=['genres'], inplace=True)

    all_genres = []
    for index, row in df_sor.iterrows():
        movie_id = row['id']
        try:
            # A coluna 'genres' é uma string que precisa ser convertida para uma lista de dicionários
            genres_list = json.loads(row['genres'])
            for genre in genres_list:
                if genre and 'name' in genre:
                    all_genres.append({'movie_id': movie_id, 'genre_name': genre['name']})
        except (json.JSONDecodeError, TypeError):
            print(f"Ignorando linha com formato de gênero inválido para o filme ID: {movie_id}")
            continue

    df_genres = pd.DataFrame(all_genres).drop_duplicates()
    df_genres.to_sql('sot_movie_genres', conn, if_exists='replace', index=False)
    print(f"Tabela 'sot_movie_genres' populada com {len(df_genres)} relações filme-gênero.")

    conn.close()