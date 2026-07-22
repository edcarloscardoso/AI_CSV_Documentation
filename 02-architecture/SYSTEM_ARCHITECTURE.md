# System Architecture

## Visão Geral

A arquitetura é composta por quatro camadas principais com separação clara de responsabilidades. O LLM **nunca acessa os dados diretamente** — toda consulta passa obrigatoriamente pelas Tools.

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Streamlit)                        │
│   Interface A: Upload ZIP    │    Interface B: Chat             │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP
┌──────────────────────────────▼──────────────────────────────────┐
│                       BACKEND (FastAPI)                         │
│   POST /upload  │  POST /ask  │  GET /datasets                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                   ORCHESTRATOR (PydanticAI)                     │
│                                                                 │
│   ┌──────────────┐   ┌────────────┐   ┌──────────────────────┐ │
│   │ Schema Tool  │   │  SQL Tool  │   │  Stats Tool          │ │
│   │              │   │            │   │                      │ │
│   │ lê catálogo  │   │ executa    │   │ métricas             │ │
│   │ semântico    │   │ SQL real   │   │ descritivas          │ │
│   └──────────────┘   └────────────┘   └──────────────────────┘ │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                     Chart Tool                           │  │
│   │  decide tipo de gráfico → serializa spec Plotly JSON     │  │
│   └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                         DuckDB                                  │
│   tabela_1  │  tabela_2  │  ...  │  catalogo (SQLite)           │
└─────────────────────────────────────────────────────────────────┘
```

## Stack Tecnológico

| Camada | Tecnologia | Justificativa |
|--------|------------|---------------|
| Frontend | Streamlit | Rápido de desenvolver; suporte nativo a gráficos Plotly |
| Backend | FastAPI | Async, type-safe, OpenAPI automático |
| Orquestração | PydanticAI | Tool calling estruturado, type-safety nativo |
| LLM | Google Gemini 2.0 Flash | Tool calling nativo; custo/performance; `GOOGLE_API_KEY` via `.env` |
| Banco de Dados | DuckDB | SQL analítico em memória, ideal para CSVs |
| Catálogo | SQLite | Persistência leve dos metadados |

## Princípios Arquiteturais

1. **LLM como cérebro, Tools como mãos:** o LLM decide *o que fazer*, as Tools *fazem de fato*
2. **Schema primeiro:** o agente SEMPRE consulta o schema antes de gerar SQL
3. **Validação de SQL:** SQL gerado é validado (EXPLAIN) antes de executar
4. **Isolamento por dataset_id:** cada upload tem seu namespace isolado no DuckDB
5. **Erros explícitos:** toda exceção tem código, mensagem e sugestão de correção
