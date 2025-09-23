# Data Model: TMDB Movies & Credits  

Este documento descreve a modelagem de dados em três camadas: **System of Record (SOR)**, **System of Truth (SOT)** e **Specification (SPEC)**, utilizando os datasets `tmdb_5000_movies.csv` e `tmdb_5000_credits.csv`.  

---

## 1. System of Record (SOR)  

**Tabelas:**  
- `sor_movies`  
- `sor_credits`  

Representam os dados brutos, exatamente como chegam dos arquivos originais (`tmdb_5000_movies.csv` e `tmdb_5000_credits.csv`). São a primeira camada de armazenamento, garantindo uma cópia fiel dos dados originais.  

- **Propósito:** Ingestão e arquivamento dos dados brutos.  
- **Estrutura:** As colunas e tipos de dados refletem diretamente os arquivos CSV. Nenhuma transformação é aplicada aqui.  

### Estrutura:  

**Tabela `sor_movies`** (tmdb_5000_movies.csv)  

| Coluna | Tipo de Dado (SQL) | Descrição |
|---|---|---|
| budget | INTEGER | Orçamento do filme em dólares. |
| genres | JSON/TEXT | Lista de gêneros do filme (JSON). |
| homepage | TEXT | URL oficial do filme. |
| id | INTEGER | ID único do filme no TMDB. |
| keywords | JSON/TEXT | Lista de palavras-chave associadas ao filme (JSON). |
| original_language | TEXT | Idioma original do filme. |
| original_title | TEXT | Título original. |
| overview | TEXT | Sinopse/resumo do filme. |
| popularity | REAL | Indicador de popularidade. |
| production_companies | JSON/TEXT | Empresas de produção (JSON). |
| production_countries | JSON/TEXT | Países de produção (JSON). |
| release_date | DATE | Data de lançamento. |
| revenue | BIGINT | Receita em dólares. |
| runtime | REAL | Duração em minutos. |
| spoken_languages | JSON/TEXT | Idiomas falados (JSON). |
| status | TEXT | Status do filme (Released, Rumored, etc.). |
| tagline | TEXT | Frase de impacto/promocional. |
| title | TEXT | Título oficial. |
| vote_average | REAL | Média das notas. |
| vote_count | INTEGER | Número de votos. |

**Tabela `sor_credits`** (tmdb_5000_credits.csv)  

| Coluna | Tipo de Dado (SQL) | Descrição |
|---|---|---|
| movie_id | INTEGER | ID do filme (chave estrangeira para `sor_movies.id`). |
| title | TEXT | Título do filme. |
| cast | JSON/TEXT | Lista de atores (JSON). |
| crew | JSON/TEXT | Lista de membros da equipe técnica (JSON). |

---

## 2. System of Truth (SOT)  

**Tabelas:**  
- `sot_movies`  
- `sot_credits`  

Camada onde os dados são **limpos, padronizados e enriquecidos**. É a versão única e confiável para análises.  

- **Propósito:** Fornecer dados consistentes e prontos para exploração.  
- **Transformações Aplicadas:**  
  - Conversão de campos JSON para tabelas relacionais (ex.: gêneros, empresas de produção, idiomas).  
  - Normalização de nomes (ex.: "en" → "English").  
  - Conversão de tipos (ex.: `release_date` para formato `DATE`).  
  - Remoção de colunas redundantes (como `homepage`, se irrelevante para análises).  
  - Tratamento de valores nulos (ex.: `runtime` ausente preenchido com a mediana).  

### Estrutura:  

**Tabela `sot_movies`**  

| Coluna | Tipo de Dado (SQL) | Descrição |
|---|---|---|
| movie_id | INTEGER | ID único do filme. |
| title | TEXT | Título oficial. |
| original_language | TEXT | Idioma original padronizado. |
| release_date | DATE | Data de lançamento. |
| budget | INTEGER | Orçamento do filme. |
| revenue | BIGINT | Receita. |
| runtime | REAL | Duração, com nulos preenchidos. |
| popularity | REAL | Popularidade. |
| vote_average | REAL | Média de notas. |
| vote_count | INTEGER | Número de votos. |
| genres | TEXT | Lista de gêneros padronizados. |
| production_companies | TEXT | Lista de produtoras. |
| production_countries | TEXT | Lista de países. |
| spoken_languages | TEXT | Idiomas falados padronizados. |
| status | TEXT | Status (Released, etc.). |

**Tabela `sot_credits`**  

| Coluna | Tipo de Dado (SQL) | Descrição |
|---|---|---|
| movie_id | INTEGER | ID do filme (referência a `sot_movies.movie_id`). |
| title | TEXT | Título do filme. |
| main_cast | TEXT | Principais atores (ex.: top 5 extraídos de `cast`). |
| director | TEXT | Nome do diretor (extraído do `crew`). |
| producers | TEXT | Lista de produtores (extraído do `crew`). |

---

## 3. Specification (SPEC)  

**Tabela:** `spec_movies_features`  

Camada final, usada para **machine learning e análises avançadas**. Contém variáveis (features) derivadas da SOT, já limpas e organizadas.  

- **Propósito:** Fornecer um dataset pronto para treinar modelos de previsão (ex.: prever receita ou popularidade de filmes).  
- **Estrutura:** Inclui features selecionadas, normalizadas e eventualmente novas colunas derivadas (ex.: ROI = revenue/budget).  

### Estrutura:  

**Tabela `spec_movies_features`**  

| Coluna | Tipo de Dado (SQL) | Descrição |
|---|---|---|
| movie_id | INTEGER | ID do filme. |
| title | TEXT | Título oficial. |
| release_year | INTEGER | Ano de lançamento (derivado de `release_date`). |
| budget | INTEGER | Orçamento. |
| revenue | BIGINT | Receita. |
| roi | REAL | Retorno sobre investimento (revenue/budget). |
| runtime | REAL | Duração em minutos. |
| vote_average | REAL | Nota média. |
| vote_count | INTEGER | Número de votos. |
| popularity | REAL | Popularidade normalizada. |
| num_genres | INTEGER | Quantidade de gêneros do filme. |
| main_genre | TEXT | Gênero principal. |
| director | TEXT | Diretor. |
| num_cast | INTEGER | Número de atores principais. |

---

