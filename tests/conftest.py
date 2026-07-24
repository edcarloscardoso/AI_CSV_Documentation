"""Fixtures compartilhadas para suíte de testes com Pytest."""

import json
import zipfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from services import deps
from services.catalog_service import CatalogService
from services.duckdb_service import DuckDBService


@pytest.fixture
def client() -> TestClient:
    """Retorna cliente de testes da API FastAPI."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_services(tmp_path: Path) -> Generator[None, None, None]:
    """Configura bancos de dados isolados em memória para cada execução de teste."""
    deps._duckdb_service = DuckDBService(":memory:")
    deps._catalog_service = CatalogService(":memory:")
    yield
    deps.reset_services()


@pytest.fixture
def duckdb_service() -> DuckDBService:
    """Retorna a instância do DuckDBService ativa no teste."""
    return deps.get_duckdb_service()


@pytest.fixture
def catalog_service() -> CatalogService:
    """Retorna a instância do CatalogService ativa no teste."""
    return deps.get_catalog_service()


@pytest.fixture
def sample_valid_zip(tmp_path: Path) -> Path:
    """Cria um arquivo ZIP válido contendo um CSV e um dicionário de dados."""
    zip_file = tmp_path / "valid_dataset.zip"
    csv_content = "id,produto,valor\n1,Notebook,4500.00\n2,Mouse,150.50\n3,Teclado,300.00\n"
    dict_content = json.dumps({
        "id": "Identificador único da venda",
        "produto": "Nome do item vendido",
        "valor": "Preço em Reais (BRL)"
    })

    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("vendas.csv", csv_content)
        zf.writestr("dicionario.json", dict_content)

    return zip_file


@pytest.fixture
def sample_zip_no_csv(tmp_path: Path) -> Path:
    """Cria um arquivo ZIP sem nenhum CSV."""
    zip_file = tmp_path / "no_csv.zip"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("readme.txt", "Apenas um texto de ajuda")
    return zip_file


@pytest.fixture
def sample_zip_no_dict(tmp_path: Path) -> Path:
    """Cria um arquivo ZIP com CSV mas sem arquivo de dicionário."""
    zip_file = tmp_path / "no_dict.zip"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("dados.csv", "id,nome\n1,Teste")
    return zip_file
