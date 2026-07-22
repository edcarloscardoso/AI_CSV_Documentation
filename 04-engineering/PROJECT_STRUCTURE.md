# Project Structure — Estrutura do Projeto

```
ai_csv_query/
│
├── app/
│   └── main.py                   # FastAPI app, registro de routers e handlers
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py           # Orchestrator Agent (PydanticAI) — consultas
│   └── loader.py                 # Loader Agent — processamento do ZIP
│
├── tools/
│   ├── __init__.py
│   ├── schema_tool.py            # Lê schema do catálogo semântico
│   ├── sql_tool.py               # Executa SQL no DuckDB
│   ├── stats_tool.py             # Estatísticas descritivas de colunas
│   └── chart_tool.py             # Gera spec Plotly a partir dos dados
│
├── services/
│   ├── __init__.py
│   ├── zip_service.py            # Extração e validação de arquivos ZIP
│   ├── duckdb_service.py         # Conexão, criação de tabelas e queries no DuckDB
│   └── catalog_service.py        # CRUD do catálogo semântico (SQLite)
│
├── api/
│   ├── __init__.py
│   ├── contracts.py              # Modelos Pydantic (request/response/error)
│   ├── exceptions.py             # Hierarquia de exceções da aplicação
│   └── routes/
│       ├── __init__.py
│       ├── upload.py             # POST /upload
│       ├── query.py              # POST /ask
│       └── datasets.py           # GET /datasets, GET /datasets/{id}, DELETE /datasets/{id}
│
├── frontend/
│   └── app.py                    # Interface Streamlit (Upload + Chat)
│
├── prompts/
│   └── system_prompts.py         # Strings de system prompt dos agentes
│
├── tests/
│   ├── conftest.py               # Fixtures compartilhadas (cliente FastAPI, DuckDB em memória)
│   ├── test_upload.py            # Testes do fluxo de upload
│   ├── test_query.py             # Testes das consultas em linguagem natural
│   └── test_tools.py             # Testes unitários de cada Tool
│
├── data/                         # Dados em runtime (gitignored)
│   ├── uploads/                  # ZIPs temporários durante processamento
│   ├── db.duckdb                 # Banco DuckDB principal
│   └── catalog.sqlite            # Catálogo semântico
│
├── .env                          # Variáveis de ambiente (gitignored)
├── .env.example                  # Template de variáveis (versionado)
├── .gitignore
├── pyproject.toml                # Configuração de ruff, mypy, pytest
├── requirements.txt
└── README.md
```

---

## Variáveis de Ambiente (.env.example)

```env
# LLM
GOOGLE_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.0-flash

# Banco de dados
DUCKDB_PATH=data/db.duckdb
CATALOG_PATH=data/catalog.sqlite

# Upload
UPLOAD_DIR=data/uploads
MAX_ZIP_SIZE_MB=200

# API
API_HOST=0.0.0.0
API_PORT=8000

# Agente
SQL_MAX_ROWS=500
SQL_TIMEOUT_SECONDS=30
LLM_TIMEOUT_SECONDS=60
```

---

## Como Executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env
# editar .env com sua GOOGLE_API_KEY

# 3. Iniciar backend
uvicorn app.main:app --reload --port 8000

# 4. Iniciar frontend (em outro terminal)
streamlit run frontend/app.py

# 5. Rodar testes
pytest tests/ -v
```
