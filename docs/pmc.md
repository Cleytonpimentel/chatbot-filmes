# Project Model Canvas — Kaggle Chatbot MVP (Exemplo Filmes TMDB)

## Contexto
O dataset TMDB 5000 Movies reúne informações sobre milhares de filmes, incluindo título, gêneros, orçamento, receita, popularidade, votos e descrições.
Ele é amplamente usado em ciência de dados para análises exploratórias, previsões de sucesso de filmes e recomendações.
O objetivo educacional aqui é usar esse conjunto como base para treinar modelos simples e construir um chatbot interativo.
---

## Problema a ser Respondido
Que tipo de filme tende a ter melhores avaliações?

---

## Pergunta Norteadora
- Qual genero de filme tem a melhor avaliação?

---

## Solução Proposta
Desenvolver um **chatbot educacional em Streamlit** que:  
1. Permita upload do arquivo tmdb_5000_movies.csv.
2. Treine modelos de
   - Regressão linear (predição de receita do filme).
   - Regressão logística/classificação (filme “bem avaliado” ou não, baseado em nota > 7, por exemplo).  
   - Modelo de recomendação baseado em similaridade de gêneros/descrições.
3. Mostre métricas de avaliação (R², RMSE, acurácia, f1-score).
4. Explique a importância das variáveis (ex.: orçamento influencia receita? gêneros influenciam avaliação?) 
5. Responda perguntas do usuário via chatbot regrado (ex.: “quais os 5 filmes mais populares de ação?”).

---

## Desenho de Arquitetura
O sistema será estruturado em camadas:  

- **Interface (app/):** Streamlit como front-end para upload, treino e perguntas.  
- **Core (core/):** módulos para dados, features, modelos, explicabilidade e chatbot.  
- **Dados (data/):** pastas para armazenar arquivos brutos, tratados e modelos treinados.  
- **Documentação (docs/):** PMC, arquitetura, governança e testes.  

---

## Resultados Esperados
- Modelo de regressão com R² acima de 0.70 para prever receita. 
- Classificador com acurácia próxima de 75% para identificar filmes bem avaliados.  
- Protótipo de sistema de recomendação funcional.  
- Deploy em **Streamlit Cloud** com documentação completa no GitHub.  

---

## Observação Didática
O PMC é o mapa inicial do projeto, conectando contexto, problema e solução a uma aplicação prática.
Ele permite alinhar objetivos antes da programação e serve como documento pedagógico para mostrar como ciência de dados pode ser aplicada em entretenimento e mídia.
