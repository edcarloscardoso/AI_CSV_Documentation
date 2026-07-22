# API Specification

**Base URL:** `http://localhost:8000`  
**Versão:** v1  
**Autenticação:** nenhuma (MVP local)

---

## POST /upload

Recebe um arquivo ZIP e inicia o processamento dos CSVs.

**Request:**
```
Content-Type: multipart/form-data
Campo: file (obrigatório) — arquivo .zip
```

**Response 200 — Sucesso:**
```json
{
  "dataset_id": "ds_20240115_abc123",
  "status": "success",
  "message": "3 tabelas carregadas com sucesso",
  "tables": [
    {
      "name": "notas_fiscais",
      "row_count": 15420,
      "columns": [
        {"name": "fornecedor",   "type": "VARCHAR", "description": "Nome do fornecedor"},
        {"name": "valor",        "type": "DOUBLE",  "description": "Valor da nota em R$"},
        {"name": "data_emissao", "type": "DATE",    "description": "Data de emissão"}
      ]
    }
  ]
}
```

**Response 400 — ZIP inválido:**
```json
{"error": "InvalidZipError", "detail": "O arquivo enviado não é um ZIP válido.", "code": "INVALID_ZIP"}
```

**Response 422 — Sem dicionário:**
```json
{"error": "NoDictionaryError", "detail": "Nenhum arquivo de dicionário encontrado no ZIP.", "code": "NO_DICTIONARY"}
```

---

## POST /ask

Recebe uma pergunta em linguagem natural e retorna a resposta do agente.

**Request:**
```json
{
  "dataset_id": "ds_20240115_abc123",
  "question": "Qual fornecedor recebeu o maior valor total?",
  "session_id": "sess_xyz789"
}
```

**Response 200 — Resposta em texto:**
```json
{
  "answer_text": "O fornecedor com maior valor total foi **Empresa A**, com R$ 450.000,00.",
  "answer_type": "text",
  "table_data": null,
  "chart_spec": null,
  "sql_used": "SELECT fornecedor, SUM(valor) as total FROM notas_fiscais ORDER BY total DESC LIMIT 1"
}
```

**Response 200 — Resposta com tabela:**
```json
{
  "answer_text": "Os 5 maiores fornecedores por valor total são:",
  "answer_type": "table",
  "table_data": [
    {"fornecedor": "Empresa A", "total": 450000.0},
    {"fornecedor": "Empresa B", "total": 320000.0}
  ],
  "chart_spec": null,
  "sql_used": "SELECT fornecedor, SUM(valor) as total FROM notas_fiscais GROUP BY fornecedor ORDER BY total DESC LIMIT 5"
}
```

**Response 200 — Resposta com gráfico:**
```json
{
  "answer_text": "Evolução do total gasto por mês:",
  "answer_type": "chart",
  "table_data": null,
  "chart_spec": {
    "chart_type": "line",
    "plotly_spec": {
      "data": [{"x": ["Jan", "Fev", "Mar"], "y": [50000, 75000, 62000], "type": "scatter", "mode": "lines+markers"}],
      "layout": {"title": "Total por Mês", "xaxis": {"title": "Mês"}, "yaxis": {"title": "R$"}}
    }
  },
  "sql_used": "SELECT strftime(data_emissao, '%Y-%m') as mes, SUM(valor) as total FROM notas_fiscais GROUP BY mes ORDER BY mes"
}
```

---

## GET /datasets

Lista todos os datasets disponíveis.

**Response 200:**
```json
{
  "datasets": [
    {
      "dataset_id": "ds_20240115_abc123",
      "name": "202401_NFs",
      "uploaded_at": "2024-01-15T10:30:00",
      "tables": ["notas_fiscais", "itens_nf"],
      "row_count_total": 18500
    }
  ]
}
```

---

## GET /datasets/{dataset_id}

Retorna detalhes de um dataset específico.

**Response 200:** Mesmo formato de `UploadResponse`.  
**Response 404:** `{"error": "DatasetNotFoundError", "detail": "Dataset não encontrado.", "code": "NOT_FOUND"}`

---

## DELETE /datasets/{dataset_id}

Remove um dataset do DuckDB e do catálogo.

**Response 200:**
```json
{"status": "success", "message": "Dataset removido com sucesso."}
```
