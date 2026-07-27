"""Testes unitários e de integração para a ferramenta chart_tool e visualizações Plotly."""

import pytest
from tools.chart_tool import chart_tool
from agents.orchestrator import OrchestratorAgent
from services.duckdb_service import DuckDBService
from services.catalog_service import CatalogService


def test_chart_tool_bar_chart() -> None:
    """Testa geração de gráfico de barras a partir de dados por categoria."""
    data = [
        {"fornecedor": "Empresa A", "total_valor": 15000.0},
        {"fornecedor": "Empresa B", "total_valor": 8500.0},
        {"fornecedor": "Empresa C", "total_valor": 3200.0},
    ]

    res = chart_tool(data, question="Quais os maiores fornecedores?")
    assert res is not None
    assert res["chart_type"] == "bar"
    assert "plotly_spec" in res
    assert len(res["plotly_spec"]["data"]) == 1
    assert res["plotly_spec"]["data"][0]["type"] == "bar"
    assert res["plotly_spec"]["data"][0]["x"] == ["Empresa A", "Empresa B", "Empresa C"]


def test_chart_tool_line_chart() -> None:
    """Testa geração de gráfico de linhas a partir de série temporal."""
    data = [
        {"mes": "2024-01", "total_gasto": 120000.0},
        {"mes": "2024-02", "total_gasto": 145000.0},
        {"mes": "2024-03", "total_gasto": 98000.0},
    ]

    res = chart_tool(data, question="Qual o total gasto por mês?")
    assert res is not None
    assert res["chart_type"] == "line"
    assert res["plotly_spec"]["data"][0]["type"] == "scatter"
    assert res["plotly_spec"]["data"][0]["mode"] == "lines+markers"


def test_chart_tool_pie_chart() -> None:
    """Testa geração de gráfico de pizza quando solicitado explicitamente."""
    data = [
        {"categoria": "Alimentos", "total": 5000.0},
        {"categoria": "Transporte", "total": 3000.0},
    ]

    res = chart_tool(data, question="Mostre um gráfico de pizza das categorias")
    assert res is not None
    assert res["chart_type"] == "pie"
    assert res["plotly_spec"]["data"][0]["type"] == "pie"


def test_chart_tool_insufficient_data() -> None:
    """Testa comportamento seguro quando há dados insuficientes (menos de 2 linhas ou 2 colunas)."""
    assert chart_tool([]) is None
    assert chart_tool([{"col1": "val1"}]) is None


def test_orchestrator_chart_integration(
    duckdb_service: DuckDBService,
    catalog_service: CatalogService,
    tmp_path: pytest.TempPathFactory,
) -> None:
    """Testa se o OrchestratorAgent retorna chart_spec para perguntas temporais."""
    from pathlib import Path
    csv_file = Path(tmp_path) / "vendas_mensais.csv"
    csv_file.write_text("data,total\n2024-01-10 10:00:00,1000.0\n2024-02-15 11:00:00,2500.0\n")

    duckdb_service.register_csv_view("vendas_mensais", csv_file)
    ds_id = catalog_service.register_dataset("Vendas Mensais", "vendas.zip")
    tbl_id = catalog_service.register_table(ds_id, "vendas_mensais", "vendas_mensais.csv", row_count=2)
    catalog_service.register_column(tbl_id, "data", "TIMESTAMP", description="Data da venda")
    catalog_service.register_column(tbl_id, "total", "DOUBLE", description="Valor total em R$")

    orchestrator = OrchestratorAgent(catalog_service=catalog_service, duckdb_service=duckdb_service)
    res = orchestrator.run("Qual foi o total gasto em cada mês?", ds_id)

    assert res.chart_spec is not None
    assert res.chart_spec.chart_type in ["line", "bar"]
    assert "plotly_spec" in res.chart_spec.model_dump()
