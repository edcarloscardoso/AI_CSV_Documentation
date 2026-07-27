"""Tool schema_tool: fornece a estrutura semântica das tabelas do dataset."""

from typing import Any

from loguru import logger

from services.catalog_service import CatalogService
from services.deps import get_catalog_service, get_duckdb_service
from services.duckdb_service import DuckDBService


def schema_tool(
    dataset_id: str,
    catalog_service: CatalogService | None = None,
    duckdb_service: DuckDBService | None = None,
) -> dict[str, Any]:
    """Retorna o esquema completo de todas as tabelas de um dataset.
    
    Inclui tipos de colunas, descrições vinda do dicionário de dados e amostras de valores.
    """
    catalog = catalog_service or get_catalog_service()
    duckdb_s = duckdb_service or get_duckdb_service()

    # Busca o schema completo do catálogo semântico
    dataset_schema = catalog.get_dataset_full_schema(dataset_id)
    tables_result = []

    for tbl in dataset_schema.get("tables", []):
        tbl_name = tbl["table_name"]
        row_count = tbl.get("row_count", 0)

        # Busca amostra de linhas do DuckDB para contextualizar o LLM
        sample_rows: list[dict[str, Any]] = []
        try:
            sample_rows = duckdb_s.execute_query(f"SELECT * FROM {tbl_name} LIMIT 3", max_rows=3)
        except Exception as e:
            logger.warning(f"Não foi possível extrair amostras da tabela '{tbl_name}': {e}")

        cols_info = []
        for col in tbl.get("columns", []):
            c_name = col["column_name"]
            c_type = col["data_type"]
            c_desc = col.get("description") or col.get("business_definition") or ""

            # Extrai amostra específica desta coluna
            samples = [
                row[c_name]
                for row in sample_rows
                if c_name in row and row[c_name] is not None
            ]

            cols_info.append({
                "name": c_name,
                "type": c_type,
                "description": c_desc,
                "sample": samples,
            })

        tables_result.append({
            "name": tbl_name,
            "row_count": row_count,
            "columns": cols_info,
        })

    logger.info(
        f"schema_tool executado com sucesso para dataset_id='{dataset_id}' "
        f"({len(tables_result)} tabelas)"
    )

    return {
        "dataset_id": dataset_id,
        "dataset_name": dataset_schema.get("name", ""),
        "tables": tables_result,
    }
