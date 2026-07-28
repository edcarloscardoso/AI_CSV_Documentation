"""Testes End-to-End (E2E) para validação completa do fluxo do AI CSV Query."""

import json
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def nfs_dataset_zip(tmp_path: Path) -> Path:
    """Cria um pacote ZIP de teste simulando dados de NFs com múltiplas colunas e dicionário."""
    zip_path = tmp_path / "202401_NFs_test.zip"

    csv_nfs = (
        "nota_fiscal,data,fornecedor,produto,categoria,qtd,valor\n"
        "1001,2024-01-05,TechCorp,Notebook Pro,Eletrônicos,10,50000.00\n"
        "1002,2024-01-12,PaperCo,Papel A4,Escritório,100,2500.00\n"
        "1003,2024-01-18,TechCorp,Monitor 27,Eletrônicos,15,22500.00\n"
        "1004,2024-01-25,CleanInc,Detergente Ind,Limpeza,50,1500.00\n"
        "1005,2024-01-28,TechCorp,Teclado Mec,Eletrônicos,30,9000.00\n"
    )

    dict_content = json.dumps({
        "nota_fiscal": "Número identificador da nota fiscal emitativa",
        "data": "Data de emissão no formato YYYY-MM-DD",
        "fornecedor": "Nome da empresa fornecedora",
        "produto": "Descrição do item comprado",
        "categoria": "Segmento de mercado do produto",
        "qtd": "Quantidade comprada",
        "valor": "Valor total gasto na nota fiscal em Reais (BRL)",
    })

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("nfs_202401.csv", csv_nfs)
        zf.writestr("dicionario.json", dict_content)

    return zip_path


def test_e2e_full_pipeline_upload_schema_and_queries(client: TestClient, nfs_dataset_zip: Path) -> None:
    """Valida o fluxo end-to-end: Upload ➔ Checagem de Lista ➔ Consulta de Esquema ➔ Remoção."""
    # 1. POST /upload
    with open(nfs_dataset_zip, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("202401_NFs_test.zip", f, "application/zip")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    dataset_id = data["dataset_id"]
    assert dataset_id.startswith("ds_")
    assert len(data["tables"]) == 1
    assert data["tables"][0]["name"] == "nfs_202401"
    assert data["tables"][0]["row_count"] == 5

    # 2. GET /datasets
    response_list = client.get("/datasets")
    assert response_list.status_code == 200
    datasets = response_list.json()["datasets"]
    assert any(d["dataset_id"] == dataset_id for d in datasets)

    # 3. GET /datasets/{dataset_id}
    response_details = client.get(f"/datasets/{dataset_id}")
    assert response_details.status_code == 200
    details = response_details.json()
    assert details["dataset_id"] == dataset_id
    assert len(details["tables"]) == 1
    col_names = [c["name"] for c in details["tables"][0]["columns"]]
    assert "fornecedor" in col_names
    assert "valor" in col_names

    # 4. DELETE /datasets/{dataset_id}
    response_del = client.delete(f"/datasets/{dataset_id}")
    assert response_del.status_code == 200
    assert response_del.json()["status"] == "success"

    # Confirma remoção (deve retornar HTTP 404)
    response_details_after = client.get(f"/datasets/{dataset_id}")
    assert response_details_after.status_code == 404
    assert response_details_after.json()["code"] == "NOT_FOUND"


def test_e2e_invalid_upload_returns_friendly_error(client: TestClient, tmp_path: Path) -> None:
    """Valida que o envio de arquivo não-ZIP retorna erro 400 amigável."""
    invalid_file = tmp_path / "texto.txt"
    invalid_file.write_text("não é um arquivo zip")

    with open(invalid_file, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("texto.txt", f, "text/plain")},
        )

    assert response.status_code == 400
    assert "code" in response.json()
    assert response.json()["code"] == "INVALID_ZIP"
