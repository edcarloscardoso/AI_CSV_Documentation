# Error Handling — Tratamento de Erros

## Princípio

Todos os erros devem:
1. Ser **capturados** antes de chegarem ao usuário
2. Retornar uma **mensagem legível** (não stack trace)
3. Ter um **código de máquina** para o frontend tratar
4. Ser **logados** com contexto suficiente para debug

---

## Hierarquia de Exceções

```python
# api/exceptions.py

class AppBaseError(Exception):
    """Exceção base da aplicação."""
    http_status: int = 500
    code: str = "INTERNAL_ERROR"

# Erros de Upload
class InvalidZipError(AppBaseError):
    http_status = 400
    code = "INVALID_ZIP"

class NoCSVFoundError(AppBaseError):
    http_status = 422
    code = "NO_CSV"

class NoDictionaryError(AppBaseError):
    http_status = 422
    code = "NO_DICTIONARY"

class InvalidCSVError(AppBaseError):
    http_status = 422
    code = "INVALID_CSV"

# Erros de Consulta
class DatasetNotFoundError(AppBaseError):
    http_status = 404
    code = "NOT_FOUND"

class SQLExecutionError(AppBaseError):
    http_status = 500
    code = "SQL_ERROR"

class LLMTimeoutError(AppBaseError):
    http_status = 504
    code = "LLM_TIMEOUT"
```

---

## Handler Global no FastAPI

```python
# app/main.py

from fastapi import Request
from fastapi.responses import JSONResponse
from api.exceptions import AppBaseError
from loguru import logger

@app.exception_handler(AppBaseError)
async def app_error_handler(request: Request, exc: AppBaseError):
    logger.error("[{code}] {msg}", code=exc.code, msg=str(exc))
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": type(exc).__name__, "detail": str(exc), "code": exc.code}
    )

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Erro não tratado: {e}", e=str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": "InternalError", "detail": "Erro interno. Tente novamente.", "code": "INTERNAL_ERROR"}
    )
```

---

## Tratamento nos Serviços

```python
# services/zip_service.py

def extract_zip(zip_path: str) -> ExtractResult:
    try:
        with zipfile.ZipFile(zip_path) as zf:
            ...
    except zipfile.BadZipFile:
        raise InvalidZipError("O arquivo enviado não é um ZIP válido.")

    csv_files = [f for f in zf.namelist() if f.endswith(".csv")]
    if not csv_files:
        raise NoCSVFoundError("Nenhum arquivo CSV encontrado no ZIP.")
```

---

## Retry no Agente (SQL inválido)

O Orchestrator tenta corrigir SQL inválido **1 vez** antes de lançar erro:

```python
for attempt in range(2):
    try:
        result = sql_tool(query, dataset_id)
        break
    except SQLExecutionError as e:
        if attempt == 0:
            logger.warning("SQL inválido na tentativa 1. Tentando correção...")
            query = await fix_sql(query, error=str(e), schema=schema)
        else:
            raise SQLExecutionError(f"SQL inválido após 2 tentativas: {str(e)}")
```

---

## Mensagens de Erro para o Usuário

| Situação | Mensagem exibida no frontend |
|----------|------------------------------|
| ZIP corrompido | "O arquivo enviado não é válido. Verifique se é um arquivo .zip." |
| Sem CSV no ZIP | "Nenhum arquivo CSV foi encontrado no arquivo enviado." |
| Sem dicionário | "Inclua um arquivo de dicionário de dados no ZIP (JSON, CSV ou XLSX)." |
| Pergunta sem resultado | "Não foram encontrados dados para essa consulta. Tente reformular a pergunta." |
| Erro de SQL | "Não consegui interpretar essa pergunta. Tente ser mais específico." |
| Timeout do LLM | "O serviço de IA demorou mais que o esperado. Tente novamente." |
