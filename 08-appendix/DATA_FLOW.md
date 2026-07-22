# Data Flow — Fluxo de Dados

## Fluxo A — Upload e Carga

```
┌─────────────┐
│   Usuário   │
└──────┬──────┘
       │ envia arquivo.zip
       ▼
┌─────────────────────────────────────────┐
│           Frontend (Streamlit)           │
│   Interface A — Upload                   │
└──────────────┬──────────────────────────┘
               │ POST /upload (multipart/form-data)
               ▼
┌─────────────────────────────────────────┐
│            FastAPI Backend               │
│   Valida extensão (.zip)                 │
│   Salva ZIP em data/uploads/             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           zip_service                    │
│   Extrai ZIP para pasta temporária       │
│   Identifica arquivos CSV                │
│   Identifica arquivo de dicionário       │
│   Valida: ≥1 CSV, dicionário presente    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           Loader Agent                   │
│   Lê dicionário → mapeia descrições      │
│   Para cada CSV:                         │
│     → cria tabela no DuckDB              │
│     → registra metadados no catálogo     │
│     → salva preview (5 linhas)           │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
  ┌─────────┐     ┌──────────────┐
  │  DuckDB │     │ catalog.sqlite│
  │ tabelas │     │ metadados    │
  └─────────┘     └──────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Resposta: UploadResponse              │
│   dataset_id + tables + row_counts      │
└─────────────────────────────────────────┘
```

---

## Fluxo B — Consulta em Linguagem Natural

```
┌─────────────┐
│   Usuário   │
└──────┬──────┘
       │ digita pergunta
       ▼
┌─────────────────────────────────────────┐
│           Frontend (Streamlit)           │
│   Interface B — Chat                     │
└──────────────┬──────────────────────────┘
               │ POST /ask {dataset_id, question}
               ▼
┌─────────────────────────────────────────┐
│            FastAPI Backend               │
│   Valida QuestionRequest                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       Orchestrator Agent (PydanticAI)    │
│                                          │
│  1. schema_tool(dataset_id)              │
│     → catálogo → schema + sample         │
│                                          │
│  2. LLM (Gemini) gera SQL               │
│     usando schema como contexto          │
│                                          │
│  3. sql_tool(query, dataset_id)          │
│     → DuckDB executa → retorna DataFrame │
│                                          │
│  4. Valida resultado                     │
│     → vazio? → mensagem "sem dados"      │
│     → erro?  → retry → ou erro explícito │
│                                          │
│  5. Decide formato                       │
│     texto / tabela / gráfico             │
│                                          │
│  6. [se gráfico] chart_tool(data, q)     │
│     → retorna Plotly JSON spec           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         QuestionResponse                 │
│   answer_text + answer_type             │
│   table_data + chart_spec + sql_used    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           Frontend (Streamlit)           │
│   Texto → st.markdown()                 │
│   Tabela → st.dataframe()               │
│   Gráfico → st.plotly_chart()           │
└─────────────────────────────────────────┘
```

---

## Modelo de Dados — Catálogo Semântico (SQLite)

```sql
-- Datasets
CREATE TABLE datasets (
    dataset_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    uploaded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status       TEXT DEFAULT 'active'
);

-- Tabelas de cada dataset
CREATE TABLE tables (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id   TEXT REFERENCES datasets(dataset_id),
    table_name   TEXT NOT NULL,
    row_count    INTEGER,
    duckdb_path  TEXT
);

-- Colunas com descrições do dicionário
CREATE TABLE columns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id     INTEGER REFERENCES tables(id),
    column_name  TEXT NOT NULL,
    dtype        TEXT,
    description  TEXT,
    sample_json  TEXT   -- JSON array com 5 valores de exemplo
);
```
