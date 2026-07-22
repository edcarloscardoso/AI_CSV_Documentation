# Contracts — Modelos Pydantic

Todos os contratos de entrada e saída da API são definidos como modelos Pydantic em `api/contracts.py`.

---

## Modelos de Upload

```python
from pydantic import BaseModel
from typing import Literal, Any
from datetime import datetime

class ColumnInfo(BaseModel):
    name: str
    dtype: str
    description: str | None = None      # vem do dicionário de dados
    sample_values: list[Any] = []

class TableInfo(BaseModel):
    name: str
    row_count: int
    columns: list[ColumnInfo]

class UploadResponse(BaseModel):
    dataset_id: str
    status: Literal["success", "error"]
    message: str
    tables: list[TableInfo]
```

---

## Modelos de Consulta

```python
class QuestionRequest(BaseModel):
    dataset_id: str
    question: str
    session_id: str | None = None       # mantém histórico de contexto por sessão

class ChartSpec(BaseModel):
    chart_type: Literal["bar", "line", "pie", "histogram", "scatter"]
    plotly_spec: dict                   # JSON Plotly pronto para renderizar

class QuestionResponse(BaseModel):
    answer_text: str
    answer_type: Literal["text", "table", "chart", "mixed"]
    table_data: list[dict] | None = None
    chart_spec: ChartSpec | None = None
    sql_used: str | None = None         # SQL executado (para transparência)
```

---

## Modelos de Dataset

```python
class DatasetMetadata(BaseModel):
    dataset_id: str
    name: str
    uploaded_at: datetime
    tables: list[str]
    row_count_total: int

class DatasetListResponse(BaseModel):
    datasets: list[DatasetMetadata]
```

---

## Modelos de Erro

```python
class ErrorResponse(BaseModel):
    error: str       # nome da exceção: "InvalidZipError"
    detail: str      # mensagem legível para o usuário
    code: str        # código de máquina: "INVALID_ZIP"
```

### Tabela de Códigos de Erro

| `code` | HTTP | Quando ocorre |
|--------|------|---------------|
| `INVALID_ZIP` | 400 | Arquivo enviado não é um ZIP válido |
| `NO_CSV` | 422 | ZIP não contém nenhum arquivo CSV |
| `NO_DICTIONARY` | 422 | ZIP não contém arquivo de dicionário |
| `INVALID_CSV` | 422 | CSV está malformado ou vazio |
| `SQL_ERROR` | 500 | SQL gerado pelo LLM é inválido |
| `NOT_FOUND` | 404 | `dataset_id` não existe |
| `LLM_TIMEOUT` | 504 | LLM não respondeu dentro do prazo |
