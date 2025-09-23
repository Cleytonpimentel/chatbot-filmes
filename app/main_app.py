# main_app.py

import streamlit as st
import pandas as pd
import core.database_manager as db
import core.data_processing as dp
import core.model_trainer as mt
import core.classification_model as cm
import os
import time
import json
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURAÇÃO E INICIALIZAÇÃO ---
CSV_MOVIES_PATH = 'data/tmdb_5000_movies.csv'
CSV_CREDITS_PATH = 'data/tmdb_5000_credits.csv'
st.set_page_config(page_title="CineBot", layout="centered")

# Dicionário para traduzir gêneros de Português para Inglês
GENRE_TRANSLATIONS = {
    "ação": "Action", "aventura": "Adventure", "animação": "Animation", "comédia": "Comedy",
    "crime": "Crime", "documentário": "Documentary", "drama": "Drama", "família": "Family",
    "fantasia": "Fantasy", "história": "History", "terror": "Horror", "música": "Music",
    "mistério": "Mystery", "romance": "Romance", "ficção científica": "Science Fiction",
    "cinema tv": "TV Movie", "suspense": "Thriller", "guerra": "War", "faroeste": "Western"
}

# Lista de saudações que o bot vai reconhecer
GREETINGS = ["olá", "ola", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "eae"]

# Função para configurar tudo na primeira execução
def setup():
    st.info("Primeira execução: Preparando o banco de dados e as análises...")

    # Tabela de Filmes
    db.execute_sql_from_file('core/data/sor_movies.sql')
    db.insert_csv_to_db(CSV_MOVIES_PATH, 'sor_movies', ['id', 'title', 'genres', 'vote_average', 'vote_count'])

    # Tabela de Créditos (Elenco)
    db.execute_sql_from_file('core/data/sor_credits.sql')
    db.insert_csv_to_db(CSV_CREDITS_PATH, 'sor_credits', ['movie_id', 'title', 'cast', 'crew'])

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
        genre_pt = next((pt for pt, en in GENRE_TRANSLATIONS.items() if en == genre_en), genre_en)
        return f"O gênero com a melhor avaliação média é **{genre_pt.capitalize()}**, com nota **{rating:.2f}**!"
    return "Não consegui encontrar o melhor gênero."

def get_actors_by_movie(movie_title):
    query = "SELECT cast FROM sor_credits WHERE title LIKE ?"
    params = (f'%{movie_title}%',)
    df = db.query_db(query, params=params)
    if df is not None and not df.empty:
        try:
            cast_list = json.loads(df.iloc[0]['cast'])
            top_actors = [actor['name'] for actor in cast_list[:5]]
            if top_actors:
                response = f"O elenco principal de **{movie_title}** inclui:\n"
                for actor in top_actors:
                    response += f"- {actor}\n"
                return response
            else: return f"Não encontrei informações de elenco para '{movie_title}'."
        except (json.JSONDecodeError, TypeError): return "Houve um erro ao processar as informações de elenco."
    return f"Não consegui encontrar o filme '{movie_title}'. Por favor, verifique o nome."

def get_top_movies_by_genre(genre_name_en):
    query = f"""
    SELECT m.title, m.vote_average
    FROM sot_movies_clean m JOIN sot_movie_genres g ON m.movie_id = g.movie_id
    WHERE g.genre_name = ? ORDER BY m.vote_average DESC LIMIT 5;
    """
    df = db.query_db(query, params=(genre_name_en,))
    genre_pt = next((pt for pt, en in GENRE_TRANSLATIONS.items() if en == genre_name_en), genre_name_en)
    if df is not None and not df.empty:
        response = f"Aqui estão os 5 filmes de **{genre_pt.capitalize()}** mais bem avaliados:\n"
        for index, row in df.iterrows():
            response += f"- {row['title']} (Nota: {row['vote_average']:.1f})\n"
        return response
    return f"Não encontrei filmes para o gênero '{genre_pt}'. Tente outro."

def get_recommendations(title, with_scores=False):
    if cosine_sim is None or df_rec is None: return "Desculpe, o modelo de recomendação não está disponível no momento."
    try:
        # Encontra o índice do filme no DataFrame
        idx_list = df_rec.index[df_rec['title'] == title].tolist()
        if not idx_list:
            raise IndexError
        idx = idx_list[0]

        sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)[1:6]

        if with_scores:
            response = f"Analisando a similaridade para **{title}**:\n"
            for score_tuple in sim_scores:
                response += f"- **{df_rec['title'].iloc[score_tuple[0]]}** (Score: {score_tuple[1]:.2f})\n"
        else:
            response = f"Se você gostou de **{title}**, talvez também goste de:\n"
            for movie_idx in [i[0] for i in sim_scores]:
                response += f"- {df_rec['title'].iloc[movie_idx]}\n"
        return response
    except IndexError: return f"Não encontrei o filme '{title}' na minha base de dados."

# --- INTERFACE ---
st.title("🎬 CineBot")
st.caption("Seu assistente de filmes pessoal. Use o menu à esquerda para treinar modelos.")

# --- MENU LATERAL (SIDEBAR) ---
st.sidebar.title("Painel de Controle de ML")
st.sidebar.markdown("Use esta seção para gerenciar os modelos.")

st.sidebar.subheader("Modelo de Classificação (Sucesso de Filmes)")
if st.sidebar.button("Treinar Modelo e Gerar Matriz de Confusão"):
    with st.spinner("Treinando novo modelo de classificação... Isso pode levar alguns minutos."):
        conf_matrix, acc_score = cm.train_classification_model()
    st.sidebar.success("Modelo treinado com sucesso! Novo pickle foi salvo.")
    st.sidebar.write(f"**Acurácia do Modelo:** `{acc_score:.2%}`")
    st.session_state.show_confusion_matrix = True
    st.session_state.conf_matrix_data = conf_matrix

if st.session_state.get('show_confusion_matrix', False):
    st.subheader("Resultados da Avaliação do Modelo de Classificação")
    fig, ax = plt.subplots()
    sns.heatmap(st.session_state.conf_matrix_data, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Previsto Não-Sucesso', 'Previsto Sucesso'],
                yticklabels=['Real Não-Sucesso', 'Real Sucesso'])
    ax.set_ylabel('Verdadeiro'); ax.set_xlabel('Previsto')
    st.pyplot(fig)
    # Limpa o estado para não mostrar a matriz em cada rerun
    st.session_state.show_confusion_matrix = False

st.sidebar.markdown("---")

# --- LÓGICA DO CHAT ---
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
        prompt_lower = prompt.lower().strip()

        if prompt_lower in GREETINGS:
            full_response = "Olá! Tudo bem? Estou à disposição para falar sobre filmes."

        elif "melhor gênero" in prompt_lower or "maior avaliação" in prompt_lower:
            full_response = get_best_genre()

        elif "atores de" in prompt_lower or "elenco de" in prompt_lower or "quem atua em" in prompt_lower:
            parts = prompt.split(" de ") if " de " in prompt else prompt.split(" em ")
            if len(parts) > 1:
                movie_title = " ".join(parts[1:]).strip().replace('"', '')
                full_response = get_actors_by_movie(movie_title)
            else:
                full_response = "Por favor, me diga de qual filme você quer saber o elenco."

        elif "filmes de" in prompt_lower or "top 5" in prompt_lower:
            parts = prompt_lower.split("filmes de") if "filmes de" in prompt_lower else prompt_lower.split("top 5")
            if len(parts) > 1:
                genre_pt = parts[1].strip()
                genre_en = GENRE_TRANSLATIONS.get(genre_pt)
                if genre_en:
                    full_response = get_top_movies_by_genre(genre_en)
                else: full_response = f"Não reconheço o gênero '{genre_pt}'."
            else: full_response = "Por favor, especifique um gênero."

        elif "recomende" in prompt_lower or "parecido com" in prompt_lower:
            parts = prompt.split("parecido com") if "parecido com" in prompt_lower else prompt.split("recomende")
            if len(parts) > 1:
                movie_title = parts[1].strip().replace('"', '')
                found_title = next((t for t in df_rec['title'] if movie_title.lower() in t.lower()), None)
                if found_title:
                    full_response = get_recommendations(found_title)
                else: full_response = f"Não encontrei o filme '{movie_title}'."
            else: full_response = "Por favor, diga um filme para eu recomendar similares."

        elif "avaliar" in prompt_lower or "similaridade" in prompt_lower:
            parts = prompt.split("avaliar") if "avaliar" in prompt_lower else prompt.split("similaridade de")
            if len(parts) > 1:
                movie_title = parts[1].strip().replace('"', '')
                found_title = next((t for t in df_rec['title'] if movie_title.lower() in t.lower()), None)
                if found_title:
                    full_response = get_recommendations(found_title, with_scores=True)
                else: full_response = f"Não encontrei o filme '{movie_title}' para avaliar."
            else: full_response = "Por favor, diga um filme para eu avaliar a similaridade."

        elif "treinar o modelo" in prompt_lower or "retreinar" in prompt_lower:
            with st.spinner("Ok, estou retreinando o modelo de recomendação..."):
                mt.train_and_save_model()
            full_response = "Pronto! O modelo de recomendação foi treinado novamente."

        else:
            full_response = "Desculpe, não entendi. Você pode perguntar sobre 'melhor gênero', 'atores de...', 'top 5 filmes de...', 'recomende...', 'avaliar...' ou 'treinar o modelo'."

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})