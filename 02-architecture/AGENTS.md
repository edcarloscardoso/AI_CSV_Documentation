# Agents — Definição e Responsabilidades

## Visão Geral

O sistema possui **dois agentes** com responsabilidades distintas e separadas.

```
Upload  ──►  Loader Agent
Pergunta ──►  Orchestrator Agent ──► Tools ──► DuckDB
```

---

## Loader Agent

**Arquivo:** `agents/loader.py`  
**Trigger:** chamado internamente pelo endpoint `POST /upload`

### Responsabilidades
1. Receber o caminho do ZIP extraído
2. Identificar e validar os arquivos CSV
3. Identificar o arquivo de dicionário de dados (`.json`, `.csv` ou `.xlsx`)
4. Carregar cada CSV no DuckDB como tabela isolada por `dataset_id`
5. Registrar os metadados no catálogo semântico

### Input / Output

```python
# Input
@dataclass
class LoadInput:
    zip_path: str
    dataset_id: str

# Output
@dataclass
class LoadResult:
    dataset_id: str
    tables: list[TableInfo]
    status: Literal["success", "error"]
    message: str
```

### Regras de Validação
- ZIP deve conter ao menos 1 arquivo `.csv`
- CSV não pode estar vazio (0 linhas)
- Dicionário de dados é obrigatório para enriquecer o contexto do agente
- Nomes de tabelas são normalizados: `meu arquivo.csv` → `meu_arquivo`

---

## Orchestrator Agent

**Arquivo:** `agents/orchestrator.py`  
**Trigger:** chamado pelo endpoint `POST /ask`  
**Framework:** PydanticAI

### Responsabilidades
1. Receber pergunta em linguagem natural + `dataset_id`
2. Consultar o catálogo semântico via `schema_tool`
3. Gerar SQL adequado com base no contexto
4. Executar o SQL via `sql_tool`
5. Decidir o formato de resposta (texto / tabela / gráfico)
6. Retornar resposta estruturada (`QuestionResponse`)

### Tools Disponíveis (obrigatórias)

| Tool | Quando usar |
|------|-------------|
| `schema_tool` | **Sempre** — primeira chamada obrigatória |
| `sql_tool` | Para toda consulta de dados |
| `stats_tool` | Perguntas de médias, máximos, mínimos, contagens |
| `chart_tool` | Quando a resposta for uma série temporal ou comparação |

### Regra de Decisão de Formato

```
resultado.row_count == 1 e resultado.col_count == 1  →  texto
resultado.row_count <= 20                            →  tabela
pergunta contém "mês", "evolução", "crescimento"     →  line chart
pergunta contém "maior", "ranking", "top"            →  bar chart
resultado.row_count > 20                             →  gráfico + tabela resumida
```
