# core/classification_model.py

import pandas as pd
import numpy as np
import json
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.preprocessing import MultiLabelBinarizer

# --- Constantes ---
CSV_FILE_PATH = 'data/tmdb_5000_movies.csv'
MODEL_PATH = 'model/'
CLASSIFICATION_MODEL_NAME = 'classification_model.pkl'

# --- Funções ---

def preprocess_data():
    """Lê o CSV e prepara os dados para o modelo de classificação."""
    df = pd.read_csv(CSV_FILE_PATH)

    # 1. Feature Engineering: Gêneros
    # Transforma a string JSON de gêneros em uma lista de nomes
    def parse_genres(genres_str):
        try:
            return [genre['name'] for genre in json.loads(genres_str)]
        except (json.JSONDecodeError, TypeError):
            return []
    df['genres_list'] = df['genres'].apply(parse_genres)

    # Usa MultiLabelBinarizer para criar colunas para cada gênero (One-Hot Encoding)
    mlb = MultiLabelBinarizer()
    genres_encoded = mlb.fit_transform(df['genres_list'])
    genres_df = pd.DataFrame(genres_encoded, columns=mlb.classes_, index=df.index)

    # 2. Seleção de Features (X)
    # Usaremos orçamento, popularidade, tempo de duração e os gêneros
    features_df = df[['budget', 'popularity', 'runtime']].copy()

    # Lida com valores nulos/infinitos
    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.fillna(features_df.mean(), inplace=True)

    # Concatena as features numéricas com os gêneros
    X = pd.concat([features_df, genres_df], axis=1)

    # 3. Criação da Variável Alvo (y)
    # Vamos classificar filmes como "sucesso" (1) se a nota for >= 7.0, e "não sucesso" (0) caso contrário.
    y = (df['vote_average'] >= 7.0).astype(int)

    return X, y, mlb.classes_ # Retornamos as classes dos gêneros para salvar depois

def train_classification_model():
    """
    Executa o pipeline completo: pré-processa, treina, avalia e salva o modelo.
    Retorna a matriz de confusão e a acurácia.
    """
    X, y, genre_columns = preprocess_data()

    # Dividir dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Treinar o modelo (Random Forest é uma boa escolha)
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Fazer previsões no conjunto de teste
    y_pred = model.predict(X_test)

    # Avaliar o modelo
    conf_matrix = confusion_matrix(y_test, y_pred)
    acc_score = accuracy_score(y_test, y_pred)

    # Salvar o modelo treinado e as colunas de gênero em um novo arquivo pickle
    model_data = {
        'model': model,
        'genre_columns': genre_columns
    }

    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH)

    with open(os.path.join(MODEL_PATH, CLASSIFICATION_MODEL_NAME), 'wb') as f:
        pickle.dump(model_data, f)

    print("Novo modelo de classificação treinado e pickle salvo com sucesso.")

    return conf_matrix, acc_score