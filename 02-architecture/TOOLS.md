# Tools — Especificação

Todas as Tools são funções registradas no PydanticAI Agent. O LLM decide quando e como chamá-las; a execução é sempre em Python, nunca diretamente pelo LLM.

---

## schema_tool

**Arquivo:** `tools/schema_tool.py`

**Propósito:** Retornar o schema completo de um dataset para dar contexto ao LLM antes de gerar SQL.

```python
def schema_tool(dataset_id: str) -> SchemaResult:
    """
    Retorna o schema de todas as tabelas de um dataset,
    incluindo tipos de colunas, descrições do dicionário e amostras de valores.
    """
```

**Retorno:**
```json
{
  "tables": [
    {
      "name": "notas_fiscais",
      "row_count": 15420,
      "columns": [
        {"name": "fornecedor", "type": "VARCHAR", "description": "Nome do fornecedor", "sample": ["Empresa A", "Empresa B"]},
        {"name": "valor",      "type": "DOUBLE",  "description": "Valor em R$",        "sample": [1500.0, 3200.5]}
      ]
    }
  ]
}
```

---

## sql_tool

**Arquivo:** `tools/sql_tool.py`

**Propósito:** Executar uma query SQL no DuckDB e retornar o resultado como lista de dicionários.

```python
def sql_tool(query: str, dataset_id: str) -> SQLResult:
    """
    Executa SQL no DuckDB. O SQL deve referenciar apenas tabelas
    existentes no dataset informado. Retorna até 500 linhas.
    """
```

**Retorno:**
```json
{
  "rows": [{"fornecedor": "Empresa A", "total": 45000.0}, ...],
  "row_count": 10,
  "columns": ["fornecedor", "total"],
  "sql_executed": "SELECT fornecedor, SUM(valor) as total FROM notas_fiscais GROUP BY fornecedor ORDER BY total DESC LIMIT 10"
}
```

**Restrições de segurança:**
- Apenas `SELECT` é permitido — `INSERT`, `UPDATE`, `DELETE`, `DROP` são bloqueados
- Limite de 500 linhas por query
- Timeout de 30 segundos

---

## stats_tool

**Arquivo:** `tools/stats_tool.py`

**Propósito:** Calcular estatísticas descritivas de uma coluna sem precisar de SQL manual.

```python
def stats_tool(table: str, column: str, dataset_id: str) -> StatsResult:
    """
    Retorna: count, min, max, mean, median, std, null_count.
    """
```

**Retorno:**
```json
{
  "column": "valor",
  "count": 15420,
  "min": 50.0,
  "max": 980000.0,
  "mean": 8543.2,
  "median": 3200.0,
  "std": 15200.4,
  "null_count": 0
}
```

---

## chart_tool

**Arquivo:** `tools/chart_tool.py`

**Propósito:** Receber os dados do resultado SQL e produzir uma especificação Plotly JSON pronta para renderizar no frontend.

```python
def chart_tool(data: list[dict], question: str, chart_type: str | None = None) -> ChartResult:
    """
    Se chart_type não for informado, decide automaticamente com base
    nos dados e na pergunta.
    Tipos suportados: bar, line, pie, histogram, scatter.
    """
```

**Retorno:**
```json
{
  "chart_type": "bar",
  "plotly_spec": {
    "data": [{"x": ["Empresa A", "Empresa B"], "y": [45000, 32000], "type": "bar"}],
    "layout": {"title": "Total por Fornecedor", "xaxis": {"title": "Fornecedor"}, "yaxis": {"title": "R$"}}
  }
}
```
