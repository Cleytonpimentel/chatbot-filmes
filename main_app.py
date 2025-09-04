# main_app.py

import streamlit as st
import pandas as pd
import core.database_manager as db
import core.data_processing as dp
import core.model.model_trainer as mt
import os
import time

# --- CONFIGURAÇÃO E INICIALIZAÇÃO ---
CSV_FILE_PATH = 'data/tmdb_5000_movies.csv'
st.set_page_config(page_title="CineBot", layout="centered")

# Dicionário para traduzir gêneros de Português para Inglês
GENRE_TRANSLATIONS = {
    "ação": "Action",
    "aventura": "Adventure",
    "animação": "Animation",
    "comédia": "Comedy",
    "crime": "Crime",
    "documentário": "Documentary",
    "drama": "Drama",
    "família": "Family",
    "fantasia": "Fantasy",
    "história": "History",
    "terror": "Horror",
    "música": "Music",
    "mistério": "Mystery",
    "romance": "Romance",
    "ficção científica": "Science Fiction",
    "cinema tv": "TV Movie",
    "suspense": "Thriller",
    "guerra": "War",
    "faroeste": "Western"
}

# Função para configurar tudo na primeira execução
def setup():
    st.info("Primeira execução: Preparando o banco de dados e as análises...")
    db.execute_sql_from_file('core/data/sor_movies.sql')
    db.insert_csv_to_db(CSV_FILE_PATH, 'sor_movies')
    db.execute_sql_from_file('core/data/sot_tables.sql')
    dp.process_and_normalize_data()
    db.execute_sql_from_file('core/data/spec_genre_ratings.sql')

    st.info("Treinando o modelo de recomendação...")
    mt.train_and_save_model()

    st.success("Tudo pronto! O CineBot está online.")
    st.balloons()
    time.sleep(2)
    st.rerun()

# Verifica se a configuração inicial já foi feita
if 'setup_done' not in st.session_state:
    if not os.path.exists(db.DB_NAME) or not os.path.exists(os.path.join(mt.MODEL_PATH, mt.MODEL_NAME)):
        setup()
    st.session_state.setup_done = True

# Carregar dados de recomendação
cosine_sim, df_rec = mt.load_recommendation_data()

# --- FUNÇÕES DO CHATBOT ---

def get_best_genre():
    df = db.query_db("SELECT genre_name, average_rating FROM spec_genre_ratings ORDER BY average_rating DESC LIMIT 1")
    if not df.empty:
        genre_en = df.iloc[0]['genre_name']
        rating = df.iloc[0]['average_rating']
        # Traduzindo a resposta para o usuário
        genre_pt = next((pt for pt, en in GENRE_TRANSLATIONS.items() if en == genre_en), genre_en)
        return f"O gênero com a melhor avaliação média é **{genre_pt.capitalize()}**, com nota **{rating:.2f}**!"
    return "Não consegui encontrar o melhor gênero."

def get_top_movies_by_genre(genre_name_en):
    query = f"""
    SELECT m.title, m.vote_average
    FROM sot_movies_clean m
    JOIN sot_movie_genres g ON m.movie_id = g.movie_id
    WHERE g.genre_name = '{genre_name_en}' 
    ORDER BY m.vote_average DESC
    LIMIT 5;
    """
    df = db.query_db(query)
    genre_pt = next((pt for pt, en in GENRE_TRANSLATIONS.items() if en == genre_name_en), genre_name_en)
    if not df.empty:
        response = f"Aqui estão os 5 filmes de **{genre_pt.capitalize()}** mais bem avaliados:\n"
        for index, row in df.iterrows():
            response += f"- {row['title']} (Nota: {row['vote_average']:.1f})\n"
        return response
    return f"Não encontrei filmes para o gênero '{genre_pt}'. Tente outro."

def get_recommendations(title):
    if cosine_sim is None or df_rec is None:
        return "Desculpe, o modelo de recomendação não está disponível."

    try:
        idx = df_rec[df_rec['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]
        movie_indices = [i[0] for i in sim_scores]

        recommended_movies = df_rec['title'].iloc[movie_indices]
        response = f"Se você gostou de **{title}**, talvez também goste de:\n"
        for movie in recommended_movies:
            response += f"- {movie}\n"
        return response
    except IndexError:
        return f"Não encontrei o filme '{title}' na minha base de dados."

# --- LÓGICA DA INTERFACE DE CHAT ---
st.title("🎬 CineBot")
st.caption("Seu assistente de filmes pessoal. Pergunte-me sobre o melhor gênero, top filmes ou peça uma recomendação!")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar você hoje?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Sua mensagem"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        prompt_lower = prompt.lower()

        if "melhor gênero" in prompt_lower or "maior avaliação" in prompt_lower:
            full_response = get_best_genre()

        elif "filmes de" in prompt_lower or "top 5" in prompt_lower:
            parts = prompt_lower.split("filmes de")
            if len(parts) < 2:
                parts = prompt_lower.split("top 5")

            if len(parts) > 1:
                genre_pt = parts[1].strip()
                genre_en = GENRE_TRANSLATIONS.get(genre_pt)

                if genre_en:
                    full_response = get_top_movies_by_genre(genre_en)
                else:
                    full_response = f"Não reconheço o gênero '{genre_pt}'. Tente um destes: {', '.join(GENRE_TRANSLATIONS.keys())}."
            else:
                full_response = "Por favor, especifique um gênero. Ex: 'top 5 filmes de Ação'."

        elif "recomende" in prompt_lower or "parecido com" in prompt_lower:
            parts = prompt.split("parecido com")
            if len(parts) < 2: parts = prompt.split("recomende")

            if len(parts) > 1:
                movie_title = parts[1].strip().replace('"', '')
                titles = df_rec['title'].tolist()
                found_title = next((t for t in titles if movie_title.lower() in t.lower()), None)

                if found_title:
                    full_response = get_recommendations(found_title)
                else:
                    full_response = f"Não encontrei o filme '{movie_title}'. Tente digitar o título completo."
            else:
                full_response = "Por favor, me diga um filme para eu recomendar similares. Ex: 'recomende algo parecido com Avatar'."

        else:
            full_response = "Desculpe, não entendi. Você pode perguntar sobre:\n- 'Qual o melhor gênero?'\n- 'Top 5 filmes de Ação'\n- 'Recomende algo parecido com \"The Dark Knight\"'"

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})