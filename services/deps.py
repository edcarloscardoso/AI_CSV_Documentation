"""Gerenciamento de instâncias singleton e injeção de dependências dos serviços."""

import os
from pathlib import Path

from services.catalog_service import CatalogService
from services.duckdb_service import DuckDBService

_duckdb_service: DuckDBService | None = None
_catalog_service: CatalogService | None = None


def get_duckdb_service(db_path: str | Path | None = None) -> DuckDBService:
    """Retorna a instância singleton do DuckDBService."""
    global _duckdb_service
    if _duckdb_service is None or db_path is not None:
        target_path = db_path or os.getenv("DUCKDB_PATH", "data/db.duckdb")
        service = DuckDBService(target_path)
        if db_path is None:
            _duckdb_service = service
            return _duckdb_service
        return service
    return _duckdb_service


def get_catalog_service(db_path: str | Path | None = None) -> CatalogService:
    """Retorna a instância singleton do CatalogService."""
    global _catalog_service
    if _catalog_service is None or db_path is not None:
        target_path = db_path or os.getenv("CATALOG_PATH", "data/catalog.sqlite")
        service = CatalogService(target_path)
        if db_path is None:
            _catalog_service = service
            return _catalog_service
        return service
    return _catalog_service


def reset_services() -> None:
    """Reseta as instâncias globais (útil para suíte de testes)."""
    global _duckdb_service, _catalog_service
    if _duckdb_service is not None:
        _duckdb_service.close()
        _duckdb_service = None
    if _catalog_service is not None:
        _catalog_service.close()
        _catalog_service = None
