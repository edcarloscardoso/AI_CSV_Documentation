# Test Plan — Plano de Testes

## Estratégia

Testes organizados em três níveis:
- **Unitários** — cada Tool isolada
- **Integração** — fluxo completo de upload e consulta via API
- **Manual / End-to-End** — usando os datasets reais do curso

---

## Testes Unitários (`tests/test_tools.py`)

### schema_tool
```python
def test_schema_tool_retorna_colunas_corretas():
    # Dado: dataset carregado com CSV de 3 colunas
    # Quando: schema_tool é chamada
    # Então: retorna os 3 nomes de colunas e tipos corretos

def test_schema_tool_dataset_inexistente():
    # Dado: dataset_id que não existe
    # Quando: schema_tool é chamada
    # Então: lança DatasetNotFoundError
```

### sql_tool
```python
def test_sql_tool_select_simples():
    # Dado: tabela com 10 linhas
    # Quando: SELECT * FROM tabela LIMIT 5
    # Então: retorna exatamente 5 linhas

def test_sql_tool_bloqueia_delete():
    # Quando: query contém DELETE
    # Então: lança SQLExecutionError com mensagem "apenas SELECT é permitido"

def test_sql_tool_bloqueia_drop():
    # Quando: query contém DROP TABLE
    # Então: lança SQLExecutionError

def test_sql_tool_retorna_vazio_sem_erro():
    # Quando: SELECT com WHERE que não bate nenhuma linha
    # Então: retorna lista vazia, sem exceção
```

### chart_tool
```python
def test_chart_tool_bar_para_comparacao():
    # Dado: dados com coluna categórica + numérica
    # Quando: pergunta = "quais os maiores fornecedores"
    # Então: chart_type == "bar"

def test_chart_tool_line_para_serie_temporal():
    # Dado: dados com coluna de data + valor
    # Quando: pergunta = "evolução por mês"
    # Então: chart_type == "line"

def test_chart_tool_retorna_plotly_spec_valido():
    # Então: plotly_spec contém "data" e "layout"
```

---

## Testes de Integração (`tests/test_upload.py`, `tests/test_query.py`)

### Upload
```python
def test_upload_zip_valido():
    # Dado: ZIP com 1 CSV + dicionário JSON
    # Quando: POST /upload
    # Então: status 200, dataset_id retornado, tabelas listadas

def test_upload_zip_sem_csv():
    # Quando: ZIP sem CSV
    # Então: status 422, code = "NO_CSV"

def test_upload_zip_invalido():
    # Quando: arquivo que não é ZIP
    # Então: status 400, code = "INVALID_ZIP"

def test_upload_zip_sem_dicionario():
    # Quando: ZIP com CSV mas sem dicionário
    # Então: status 422, code = "NO_DICTIONARY"

def test_upload_multiplos_csvs():
    # Dado: ZIP com 3 CSVs
    # Então: 3 tabelas criadas no DuckDB
```

### Consulta
```python
def test_ask_pergunta_simples():
    # Dado: dataset carregado
    # Quando: POST /ask com "quantas linhas tem a tabela?"
    # Então: answer_text contém o número correto

def test_ask_retorna_sql_usado():
    # Então: campo sql_used não é None

def test_ask_dataset_inexistente():
    # Quando: dataset_id inválido
    # Então: status 404

def test_ask_pergunta_sem_resultado():
    # Quando: pergunta que não tem dados correspondentes
    # Então: answer_text informa que não há dados (não inventa)
```

---

## Testes Manuais / End-to-End

Usar os datasets do curso:

### Dataset: `202401_NFs.zip`

| Pergunta | Resposta Esperada | Formato |
|----------|-------------------|---------|
| "Qual fornecedor recebeu o maior valor total?" | Nome do fornecedor + valor | Texto |
| "Quais os 5 maiores fornecedores?" | Lista com nome e valor | Tabela |
| "Qual foi o total gasto por mês?" | Valores por mês | Line chart |
| "Qual produto teve maior volume?" | Nome do produto | Texto |

### Dataset: `202505_NFe.zip`

| Pergunta | Resposta Esperada | Formato |
|----------|-------------------|---------|
| "Qual categoria teve maior crescimento?" | Categoria + variação | Texto + tabela |
| "Mostre a distribuição de valores" | Histograma | Histogram chart |

---

## Fixture Base (conftest.py)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
import duckdb

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_dataset_id(client, tmp_path):
    # Cria um ZIP de teste e faz upload, retorna dataset_id
    ...
```
