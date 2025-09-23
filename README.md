# 🤖 Chatbot de Análise de Filmes

**Projeto desenvolvido para a disciplina de Inteligência Artificial do curso de Sitema de Informação .**

* **Autores:** Cleyton Santos, Luís Fernando.
* **Professor:** Cayo Felipe.

---

## 🎯 Objetivo do Projeto

Este projeto responde à pergunta: **"Qual gênero de filme possui a melhor avaliação média?"**. Para isso, foi desenvolvido um chatbot interativo que utiliza um pipeline de dados para processar, analisar e apresentar insights a partir do dataset "TMDB 5000 Movie Dataset".

O sistema realiza todo o tratamento dos dados, desde a leitura de um arquivo CSV até a estruturação em um banco de dados SQL e o treinamento de um modelo de Machine Learning para recomendações.

## ✨ Funcionalidades

* **Interface de Chat Conversacional:** Interaja com o bot usando linguagem natural.
* **Análise do Melhor Gênero:** Pergunte "qual o melhor gênero?" para obter uma resposta direta e baseada em dados.
* **Top 5 Filmes por Gênero:** Peça para ver os filmes mais bem avaliados de um gênero específico (ex: "top 5 filmes de ação").
* **Recomendações de Filmes:** Peça uma recomendação baseada em um filme que você gosta (ex: "recomende algo parecido com Avatar").

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface:** Streamlit
* **Manipulação de Dados:** Pandas
* **Banco de Dados:** SQLite
* **Machine Learning:** Scikit-learn (para o sistema de recomendação)
* **Controle de Versão:** Git & GitHub

## 🚀 Como Executar o Projeto

Siga os passos abaixo para rodar o projeto em sua máquina local.

### **Pré-requisitos**

* [Python 3.8+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads/)

### **Instalação e Execução**

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Cleytonpimentel/chatbot-filmes.git](https://github.com/Cleytonpimentel/chatbot-filmes.git)
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd chatbot-filmes
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    # Criar o ambiente
    python -m venv .venv

    # Ativar no Windows
    .venv\Scripts\activate

    # Ativar no macOS/Linux
    source .venv/bin/activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run main_app.py
    ```

A aplicação será aberta automaticamente no seu navegador! Na primeira execução, o sistema irá criar o banco de dados e treinar o modelo, o que pode levar um minuto.

## 🏗️ Estrutura do Projeto

```
├── core/               # Contém toda a lógica principal da aplicação
│   ├── data/           # Scripts SQL para criação das tabelas
│   ├── __init__.py
│   ├── data_processing.py  # Funções para normalizar e limpar os dados
│   ├── database_manager.py # Funções para gerenciar o banco de dados
│   └── model_trainer.py    # Script para treinar o modelo de ML
│
├── data/               # Onde o dataset .csv original é armazenado
│
├── model/              # Onde o modelo treinado (.pkl) é salvo
│
├── .venv/              # Pasta do ambiente virtual (ignorada pelo Git)
│
├── main_app.py         # Arquivo principal da aplicação Streamlit
│
├── requirements.txt    # Lista de dependências Python
│
└── README.md           # Este arquivo :)
```
