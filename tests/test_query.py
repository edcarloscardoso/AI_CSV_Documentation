"""Testes unitários e de integração para tools, orchestrator e endpoint POST /ask."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agents.orchestrator import OrchestratorAgent
from api.exceptions import UnsafeQueryError
from services.catalog_service import CatalogService
from services.duckdb_service import DuckDBService
from tools.schema_tool import schema_tool
from tools.sql_tool import sql_tool
from tools.stats_tool import stats_tool


def test_schema_and_sql_tools(
    duckdb_service: DuckDBService,
    catalog_service: CatalogService,
    tmp_path: Path,
) -> None:
    """Testa a execução básica do schema_tool, sql_tool e stats_tool com dados carregados."""
    # Cria CSV de teste
    csv_path = tmp_path / "vendas.csv"
    csv_path.write_text("id,produto,valor\n1,Notebook,4500.0\n2,Mouse,150.0\n3,Teclado,300.0\n")

    # Registra no DuckDB e Catálogo
    duckdb_service.register_csv_view("vendas", csv_path)
    ds_id = catalog_service.register_dataset("Vendas Teste", "vendas.zip")
    tbl_id = catalog_service.register_table(ds_id, "vendas", "vendas.csv", row_count=3)
    catalog_service.register_column(tbl_id, "valor", "DOUBLE", description="Preço do produto em R$")

    # 1. Teste schema_tool
    schema_res = schema_tool(ds_id, catalog_service, duckdb_service)
    assert schema_res["dataset_id"] == ds_id
    assert len(schema_res["tables"]) == 1
    assert schema_res["tables"][0]["name"] == "vendas"

    # 2. Teste sql_tool (SELECT permitido)
    sql_res = sql_tool("SELECT * FROM vendas WHERE valor > 200", ds_id, duckdb_service)
    assert sql_res["row_count"] == 2
    assert "valor" in sql_res["columns"]

    # 3. Teste sql_tool (bloqueio de comando perigoso)
    with pytest.raises(UnsafeQueryError):
        sql_tool("DROP TABLE vendas", ds_id, duckdb_service)

    # 4. Teste stats_tool
    stats_res = stats_tool("vendas", "valor", ds_id, duckdb_service)
    assert stats_res["count"] == 3
    assert stats_res["min"] == 150.0
    assert stats_res["max"] == 4500.0


def test_orchestrator_agent(
    duckdb_service: DuckDBService,
    catalog_service: CatalogService,
    tmp_path: Path,
) -> None:
    """Testa o OrchestratorAgent em dataset ativo."""
    csv_path = tmp_path / "produtos.csv"
    csv_path.write_text("id,nome,preco\n10,Cadeira,250.0\n20,Mesa,800.0\n")

    duckdb_service.register_csv_view("produtos", csv_path)
    ds_id = catalog_service.register_dataset("Produtos Teste", "prod.zip")
    tbl_id = catalog_service.register_table(ds_id, "produtos", "produtos.csv", row_count=2)
    catalog_service.register_column(tbl_id, "preco", "DOUBLE", description="Preço")

    orchestrator = OrchestratorAgent(catalog_service=catalog_service, duckdb_service=duckdb_service)
    response = orchestrator.run("Qual o valor médio dos produtos?", ds_id)

    assert response.answer_text is not None
    assert response.sql_used is not None
    assert response.answer_type in ["text", "table", "mixed", "chart"]


def test_ask_endpoint_integration(client: TestClient, sample_valid_zip: Path) -> None:
    """Testa a integração via HTTP POST /upload e subsequente POST /ask."""
    # 1. Faz upload do dataset
    with open(sample_valid_zip, "rb") as f:
        up_res = client.post("/upload", files={"file": ("dataset.zip", f, "application/zip")})
    assert up_res.status_code == 200
    dataset_id = up_res.json()["dataset_id"]

    # 2. Faz pergunta válida via POST /ask
    ask_payload = {
        "dataset_id": dataset_id,
        "question": "Qual o valor total das vendas?",
    }
    ask_res = client.post("/ask", json=ask_payload)
    assert ask_res.status_code == 200

    data = ask_res.json()
    assert "answer_text" in data
    assert "answer_type" in data
    assert data["sql_used"] is not None


def test_ask_endpoint_not_found(client: TestClient) -> None:
    """Testa POST /ask com um dataset_id inexistente (espera HTTP 404)."""
    ask_payload = {
        "dataset_id": "id-inexistente-123",
        "question": "Quantas linhas existem?",
    }
    ask_res = client.post("/ask", json=ask_payload)
    assert ask_res.status_code == 404
    assert ask_res.json()["code"] == "NOT_FOUND"
