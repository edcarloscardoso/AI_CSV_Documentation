"""Testes unitários dos serviços fundamentais (DuckDB, Catalog, ZIP)."""

from pathlib import Path

import pytest

from api.exceptions import (
    DatasetNotFoundError,
    InvalidZipError,
    NoCSVFoundError,
    NoDictionaryError,
    UnsafeQueryError,
)
from services.catalog_service import CatalogService
from services.duckdb_service import DuckDBService
from services.zip_service import ZipService


class TestDuckDBService:
    def test_register_csv_view_and_select(self, duckdb_service: DuckDBService, tmp_path: Path) -> None:
        csv_file = tmp_path / "teste.csv"
        csv_file.write_text("id,nome,preco\n1,Produto A,10.5\n2,Produto B,20.0\n", encoding="utf-8")

        duckdb_service.register_csv_view("produtos", csv_file)
        results = duckdb_service.execute_query("SELECT * FROM produtos")

        assert len(results) == 2
        assert results[0]["nome"] == "Produto A"
        assert results[1]["preco"] == 20.0

    def test_block_unsafe_sql(self, duckdb_service: DuckDBService) -> None:
        with pytest.raises(UnsafeQueryError):
            duckdb_service.execute_query("DROP TABLE produtos")

        with pytest.raises(UnsafeQueryError):
            duckdb_service.execute_query("DELETE FROM produtos WHERE id = 1")

        with pytest.raises(UnsafeQueryError):
            duckdb_service.execute_query("INSERT INTO produtos VALUES (3, 'C', 30)")

    def test_get_table_schema(self, duckdb_service: DuckDBService, tmp_path: Path) -> None:
        csv_file = tmp_path / "teste.csv"
        csv_file.write_text("id,categoria\n100,Eletronicos\n", encoding="utf-8")
        duckdb_service.register_csv_view("itens", csv_file)

        schema = duckdb_service.get_table_schema("itens")
        cols = [col["column_name"] for col in schema]
        assert "id" in cols
        assert "categoria" in cols


class TestCatalogService:
    def test_catalog_dataset_lifecycle(self, catalog_service: CatalogService) -> None:
        ds_id = catalog_service.register_dataset(
            name="Vendas 2024",
            zip_filename="202401_NFs.zip",
            description="Dataset de teste"
        )
        tbl_id = catalog_service.register_table(
            dataset_id=ds_id,
            table_name="vendas",
            csv_filename="vendas.csv",
            row_count=100
        )
        catalog_service.register_column(
            table_id=tbl_id,
            column_name="valor",
            data_type="DECIMAL",
            description="Valor total",
            business_definition="Valor bruto com impostos"
        )

        full_schema = catalog_service.get_dataset_full_schema(ds_id)
        assert full_schema["name"] == "Vendas 2024"
        assert len(full_schema["tables"]) == 1
        assert full_schema["tables"][0]["table_name"] == "vendas"
        assert len(full_schema["tables"][0]["columns"]) == 1

        catalog_service.delete_dataset(ds_id)
        with pytest.raises(DatasetNotFoundError):
            catalog_service.get_dataset(ds_id)


class TestZipService:
    def test_extract_valid_zip(self, sample_valid_zip: Path, tmp_path: Path) -> None:
        zip_service = ZipService()
        dest = tmp_path / "extracted"
        result = zip_service.validate_and_extract(sample_valid_zip, dest)

        assert len(result.csv_files) == 1
        assert result.csv_files[0].name == "vendas.csv"
        assert result.dictionary_file is not None
        assert "id" in result.dictionary_data

    def test_extract_zip_no_csv(self, sample_zip_no_csv: Path, tmp_path: Path) -> None:
        zip_service = ZipService()
        dest = tmp_path / "extracted_no_csv"
        with pytest.raises(NoCSVFoundError):
            zip_service.validate_and_extract(sample_zip_no_csv, dest)

    def test_extract_zip_no_dict(self, sample_zip_no_dict: Path, tmp_path: Path) -> None:
        zip_service = ZipService()
        dest = tmp_path / "extracted_no_dict"
        with pytest.raises(NoDictionaryError):
            zip_service.validate_and_extract(sample_zip_no_dict, dest)

    def test_extract_corrupted_zip(self, tmp_path: Path) -> None:
        bad_zip = tmp_path / "bad.zip"
        bad_zip.write_bytes(b"conteudo_invalido_nao_zip")

        zip_service = ZipService()
        dest = tmp_path / "extracted_bad"
        with pytest.raises(InvalidZipError):
            zip_service.validate_and_extract(bad_zip, dest)
