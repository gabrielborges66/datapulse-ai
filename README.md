# 📊 DataPulse AI

> Projeto de portfólio de **Análise de Dados** utilizando Python, Pandas, SQL e IA generativa.

## Sobre o projeto

O **DataPulse AI** transforma dados sintéticos de vendas em indicadores e análises para apoiar decisões de negócio.

O projeto foi construído para demonstrar um fluxo completo de análise de dados:

**dados brutos → tratamento → SQL → indicadores → detecção de anomalias → dashboard → IA**

## O que o projeto demonstra

- Análise exploratória com Pandas
- Consultas SQL
- Criação de KPIs
- Cálculo de ticket médio e margem
- Análise por produto, região e canal
- Detecção de anomalias com IQR
- Dashboard interativo com Streamlit
- Testes automatizados com Pytest
- Integração opcional com IA generativa
- Boas práticas de organização de projeto
- Docker

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python | Lógica e análise |
| Pandas | Tratamento e agregação |
| SQL / SQLite | Consultas analíticas |
| Streamlit | Dashboard |
| Matplotlib | Visualizações |
| Pytest | Testes automatizados |
| OpenAI API | Resumo executivo opcional |
| Docker | Containerização |

## Estrutura do projeto

```text
datapulse-ai/
├── app.py
├── data/
│   └── sales.csv
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── ai_summary.py
│   ├── config.py
│   └── database.py
├── sql/
│   └── business_queries.sql
├── tests/
│   └── test_analysis.py
├── docs/
│   ├── architecture.md
│   └── business_problem.md
├── assets/
├── reports/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md