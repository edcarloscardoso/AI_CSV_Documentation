"""Tool sql_tool: executa consultas SQL no DuckDB com restrições de segurança."""

from typing import Any

from loguru import logger

from services.deps import get_duckdb_service
from services.duckdb_service import DuckDBService


def sql_tool(
    query: str,
    dataset_id: str,
    duckdb_service: DuckDBService | None = None,
) -> dict[str, Any]:
    """Executa uma query SQL no DuckDB.

    O SQL deve referenciar apenas tabelas existentes no dataset informado.
    Apenas SELECT é permitido. Retorna até 500 linhas.
    """
    duckdb_s = duckdb_service or get_duckdb_service()

    logger.info(f"sql_tool executando SQL para dataset_id='{dataset_id}': {query}")
    rows = duckdb_s.execute_query(query, max_rows=500)

    columns = list(rows[0].keys()) if rows else []

    return {
        "rows": rows,
        "row_count": len(rows),
        "columns": columns,
        "sql_executed": query,
    }
