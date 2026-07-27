"""Tool stats_tool: calcula estatísticas descritivas de uma coluna de uma tabela."""

from typing import Any

from loguru import logger

from services.deps import get_duckdb_service
from services.duckdb_service import DuckDBService


def stats_tool(
    table: str,
    column: str,
    dataset_id: str,
    duckdb_service: DuckDBService | None = None,
) -> dict[str, Any]:
    """Calcula estatísticas descritivas de uma coluna em uma tabela DuckDB."""
    duckdb_s = duckdb_service or get_duckdb_service()

    # Sanitização básica de nomes de tabela e coluna
    sanitized_table = "".join(c for c in table if c.isalnum() or c == "_")
    sanitized_col = "".join(c for c in column if c.isalnum() or c == "_")

    query = f"""
    SELECT 
        COUNT(*) as count,
        COUNT("{sanitized_col}") as non_null_count,
        COUNT(*) - COUNT("{sanitized_col}") as null_count,
        MIN("{sanitized_col}") as min_val,
        MAX("{sanitized_col}") as max_val,
        AVG(TRY_CAST("{sanitized_col}" AS DOUBLE)) as mean,
        MEDIAN(TRY_CAST("{sanitized_col}" AS DOUBLE)) as median,
        STDDEV(TRY_CAST("{sanitized_col}" AS DOUBLE)) as std
    FROM {sanitized_table}
    """

    logger.info(f"stats_tool executando para {sanitized_table}.{sanitized_col}")
    rows = duckdb_s.execute_query(query)
    
    res = rows[0] if rows else {}

    return {
        "table": sanitized_table,
        "column": sanitized_col,
        "count": res.get("count", 0),
        "null_count": res.get("null_count", 0),
        "min": res.get("min_val"),
        "max": res.get("max_val"),
        "mean": res.get("mean"),
        "median": res.get("median"),
        "std": res.get("std"),
    }
