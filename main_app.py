import streamlit as st
import pandas as pd
from pathlib import Path
from thefuzz import process

# Módulos principais do projeto
from core.config import engine
import core.database_manager as db
import core.model.model_trainer as mt

# --- CONFIGURAÇÃO E CONSTANTES ---
CSV_FILE_PATH = 'data/tmdb_5000_movies.csv'
SPEC_SCRIPT_PATH = 'core/data/spec_genre_ratings.sql'
st.set_page_config(page_title="CineBot", layout="wide")

GENRE_TRANSLATIONS = {
    "ação": "Action", "aventura": "Adventure", "animação": "Animation",
    "comédia": "Comedy", "crime": "Crime", "documentário": "Documentary",
    "drama": "Drama", "família": "Family", "fantasia": "Fantasy",
    "história": "History", "terror": "Horror", "música": "Music",
    "mistério": "Mystery", "romance": "Romance", "ficção científica": "Science Fiction",
    "cinema tv": "TV Movie", "suspense": "Thriller", "guerra": "War", "faroeste": "Western"
}
GENRE_TRANSLATIONS_INV = {v: k for k, v in GENRE_TRANSLATIONS.items()}

# --- FUNÇÕES DE CACHE ---
@st.cache_data
def get_best_genre_cached():
    df = db.query_db(engine, "SELECT genre_name, average_rating FROM spec_genre_ratings ORDER BY average_rating DESC LIMIT 1")
    return df

@st.cache_data
def get_top_movies_cached(genre_name_en):
    query = "SELECT m.title, m.vote_average FROM sot_movies_clean m JOIN sot_movie_genres g ON m.movie_id = g.movie_id WHERE g.genre_name = :genre ORDER BY m.vote_average DESC LIMIT 5;"
    return db.query_db(engine, query, params={'genre': genre_name_en})

def find_best_movie_match(title, movie_list):
    best_match, score = process.extractOne(title, movie_list)
    return best_match if score > 80 else None

# --- LÓGICA PRINCIPAL DO CHATBOT (FUNÇÃO ATUALIZADA) ---

def handle_user_prompt(prompt, df_rec, cosine_sim):
    """Processa a mensagem do usuário, identifica a intenção e retorna a resposta."""
    prompt_lower = prompt.lower()

    # Intenção 0: Saudações
    saudacoes = ['oi', 'ola', 'olá', 'bom dia']
    if prompt_lower in saudacoes:
        return "Olá! Sou o CineBot. Como posso te ajudar?"

    # Intenção 1: Encontrar o melhor gênero (LÓGICA MELHORADA)
    elif "melhor" in prompt_lower and "gênero" in prompt_lower:
        df = get_best_genre_cached()
        if df is not None and not df.empty:
            genre_en, rating = df.iloc[0]['genre_name'], df.iloc[0]['average_rating']
            genre_pt = GENRE_TRANSLATIONS_INV.get(genre_en, genre_en).capitalize()
            return f"O gênero com a melhor avaliação média é **{genre_pt}**, com nota **{rating:.2f}**!"
        return "Não consegui encontrar o melhor gênero no momento."

    # Intenção 2: Listar top filmes de um gênero (LÓGICA REINTRODUZIDA E CORRIGIDA)
    elif any(keyword in prompt_lower for keyword in ["filmes de", "top filmes"]):
        genre_found = None
        for genre_pt, genre_en in GENRE_TRANSLATIONS.items():
            if genre_pt in prompt_lower:
                genre_found = (genre_pt, genre_en)
                break

        if genre_found:
            genre_pt, genre_en = genre_found
            df = get_top_movies_cached(genre_en)
            if df is not None and not df.empty:
                response = f"Claro! Aqui estão os top 5 filmes de **{genre_pt.capitalize()}** mais bem avaliados:\n"
                for _, row in df.iterrows():
                    response += f"- {row['title']} (Nota: {row['vote_average']:.1f})\n"
                return response
            return f"Não encontrei filmes para o gênero '{genre_pt}'. Tente outro."
        return "Por favor, especifique um gênero. Ex: 'top 5 filmes de suspense'."

    # Intenção 3: Recomendar filmes similares
    elif any(keyword in prompt_lower for keyword in ["recomende", "parecido com", "similar a"]):
        title_to_search = prompt.split("parecido com")[-1].split("recomende")[-1].split("similar a")[-1].strip().replace('"', '')
        if not title_to_search:
            return "Por favor, diga um filme para eu recomendar similares. Ex: 'recomende algo parecido com Avatar'."

        found_title = find_best_movie_match(title_to_search, df_rec['title'].tolist())
        if found_title:
            idx = df_rec[df_rec['title'] == found_title].index[0]
            sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)[1:6]
            movie_indices = [i[0] for i in sim_scores]
            recommended_movies = df_rec['title'].iloc[movie_indices]

            response = f"Se você gostou de **{found_title}**, talvez também goste de:\n"
            for movie in recommended_movies:
                response += f"- {movie}\n"
            return response
        return f"Não encontrei o filme '{title_to_search}' na minha base de dados."

    # Resposta padrão
    else:
        return "Desculpe, não entendi. Tente perguntar sobre o 'melhor gênero' ou peça 'top 5 filmes de ação'."

# --- INTERFACE GRÁFICA (UI) ---
st.title("🎬 CineBot - Assistente de Filmes")

# Inicialização do estado da aplicação
if 'model_ready' not in st.session_state:
    st.session_state.model_ready = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- LÓGICA DE CONTROLE: TREINAR OU CARREGAR ---
with st.sidebar:
    st.header("Configuração do Modelo")
    choice = st.radio(
        "Escolha uma opção:",
        ('Carregar modelo existente', 'Treinar um novo modelo'),
        index=0,
        key='model_choice'
    )

    if choice == 'Treinar um novo modelo':
        if st.button("Iniciar Treinamento Completo"):
            try:
                with st.spinner("Executando pipeline de dados e treinamento... Por favor, aguarde."):
                    db.run_data_pipeline(engine, CSV_FILE_PATH, 'sor_movies', SPEC_SCRIPT_PATH)
                    mt.train_and_save_model(engine)
                st.success("Treinamento concluído com sucesso!")
                st.session_state.model_ready = True
                st.rerun()
            except Exception as e:
                st.error(f"Ocorreu um erro durante o treinamento: {e}")
    else: # Carregar modelo existente
        st.info("O aplicativo tentará carregar o modelo pré-treinado 'movie_recommender.pkl'.")

# Carrega o modelo quando a aplicação inicia (se não estiver no modo de treino)
# ou depois que o treino for concluído.
if not st.session_state.model_ready:
    cosine_sim, df_rec = mt.load_recommendation_data()
    if cosine_sim is not None and df_rec is not None:
        st.session_state.model_ready = True
        st.session_state.cosine_sim = cosine_sim
        st.session_state.df_rec = df_rec

# --- INTERFACE DO CHAT (só aparece se o modelo estiver pronto) ---
if st.session_state.model_ready:
    st.sidebar.success("Modelo carregado e pronto para uso!")

    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Olá! O modelo está carregado. Como posso ajudar?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Sua mensagem..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                full_response = handle_user_prompt(prompt, st.session_state.df_rec, st.session_state.cosine_sim)
            st.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
else:
    st.warning("O modelo de recomendação ainda não foi carregado ou treinado. Use o menu na barra lateral para começar.")