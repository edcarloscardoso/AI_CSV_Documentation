# Coding Standards — Padrões de Código

## Linguagem e Versão

- Python **3.11+**
- Type hints obrigatórios em todas as funções e métodos
- Nenhuma função sem docstring (mínimo: 1 linha descritiva)

---

## Estrutura dos Módulos

Cada módulo deve seguir o princípio da **responsabilidade única (SRP)**:

| Módulo | Faz | Não faz |
|--------|-----|---------|
| `tools/` | Executa operações (SQL, schema, stats, chart) | Não decide *quando* usar — isso é papel do agente |
| `agents/` | Orquestra lógica de negócio | Não acessa DuckDB diretamente |
| `services/` | Operações de infraestrutura (ZIP, DuckDB, catálogo) | Não contém lógica de IA |
| `api/` | Recebe requisições, valida input, retorna response | Não contém lógica de negócio |
| `frontend/` | Renderiza UI | Não contém lógica de dados |

---

## Convenções de Nomenclatura

```python
# Classes: PascalCase
class LoaderAgent:
class QuestionRequest:

# Funções e variáveis: snake_case
def schema_tool(dataset_id: str) -> SchemaResult:
row_count = 0

# Constantes: UPPER_SNAKE_CASE
MAX_ROWS = 500
DUCKDB_PATH = "data/db.duckdb"

# Arquivos: snake_case
# loader.py, sql_tool.py, zip_service.py
```

---

## Type Hints

```python
# Correto
def sql_tool(query: str, dataset_id: str) -> SQLResult:
    ...

def get_tables(dataset_id: str) -> list[TableInfo]:
    ...

# Errado — sem tipagem
def sql_tool(query, dataset_id):
    ...
```

---

## Logging

Usar **Loguru** em todos os módulos. Nenhum `print()` em código de produção.

```python
from loguru import logger

# Nível de log adequado para cada situação
logger.info("Dataset {id} carregado com {n} tabelas", id=dataset_id, n=len(tables))
logger.warning("SQL retornou 0 linhas para query: {q}", q=query)
logger.error("Falha ao processar ZIP: {e}", e=str(exc))
logger.debug("Schema retornado: {schema}", schema=schema_dict)
```

---

## Variáveis de Ambiente

**Nunca hardcodar** credenciais ou configurações no código.

```python
# Correto — via .env + python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DUCKDB_PATH    = os.getenv("DUCKDB_PATH", "data/db.duckdb")

# Errado
GOOGLE_API_KEY = "AIza..."
```

`.env.example` deve sempre estar atualizado com todas as variáveis necessárias (sem valores reais).

---

## Ferramentas de Qualidade

```
ruff       # linting e formatação (substitui flake8 + black)
mypy       # checagem de tipos estáticos
pytest     # testes unitários e de integração
```

Configuração mínima em `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
strict = true
python_version = "3.11"
```
