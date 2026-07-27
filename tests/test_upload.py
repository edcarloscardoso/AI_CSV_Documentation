"""Testes de integração para fluxo de upload de dados e gerenciamento de datasets."""

import json
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient


def test_upload_valid_zip(client: TestClient, sample_valid_zip: Path) -> None:
    """Testa upload de um arquivo ZIP válido com CSV e Dicionário de dados."""
    with open(sample_valid_zip, "rb") as f:
        response = client.post("/upload", files={"file": ("valid_dataset.zip", f, "application/zip")})

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "dataset_id" in data
    assert len(data["tables"]) == 1

    table = data["tables"][0]
    assert table["name"] == "vendas"
    assert table["row_count"] == 3
    assert len(table["columns"]) == 3

    cols = {c["name"]: c for c in table["columns"]}
    assert "produto" in cols
    assert cols["produto"]["description"] == "Nome do item vendido"


def test_upload_zip_no_csv(client: TestClient, sample_zip_no_csv: Path) -> None:
    """Testa upload de ZIP sem arquivos CSV (espera HTTP 422 / NO_CSV)."""
    with open(sample_zip_no_csv, "rb") as f:
        response = client.post("/upload", files={"file": ("no_csv.zip", f, "application/zip")})

    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "NO_CSV"


def test_upload_zip_no_dict(client: TestClient, sample_zip_no_dict: Path) -> None:
    """Testa upload de ZIP sem dicionário explícito (aceita com metadados auto-gerados — HTTP 200)."""
    with open(sample_zip_no_dict, "rb") as f:
        response = client.post("/upload", files={"file": ("no_dict.zip", f, "application/zip")})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "dataset_id" in data





def test_upload_invalid_extension(client: TestClient) -> None:
    """Testa upload de arquivo que não possui extensão .zip (espera HTTP 400 / INVALID_ZIP)."""
    files = {"file": ("documento.txt", b"conteudo qualquer", "text/plain")}
    response = client.post("/upload", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_ZIP"


def test_upload_corrupted_zip(client: TestClient) -> None:
    """Testa upload de arquivo corrompido com extensão .zip (espera HTTP 400 / INVALID_ZIP)."""
    files = {"file": ("corrupto.zip", b"nao_sou_um_zip_real", "application/zip")}
    response = client.post("/upload", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_ZIP"


def test_upload_multiple_csvs(client: TestClient, tmp_path: Path) -> None:
    """Testa upload de pacote ZIP contendo múltiplos arquivos CSV."""
    zip_file = tmp_path / "multi_dataset.zip"
    csv1 = "id,cliente\n1,Ana\n2,Bruno\n"
    csv2 = "id,valor\n100,500.0\n"
    dict_json = json.dumps({"cliente": "Nome do cliente", "valor": "Valor da fatura"})

    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("clientes.csv", csv1)
        zf.writestr("faturas.csv", csv2)
        zf.writestr("dicionario.json", dict_json)

    with open(zip_file, "rb") as f:
        response = client.post("/upload", files={"file": ("multi_dataset.zip", f, "application/zip")})

    assert response.status_code == 200
    data = response.json()
    assert len(data["tables"]) == 2
    table_names = [t["name"] for t in data["tables"]]
    assert "clientes" in table_names
    assert "faturas" in table_names


def test_get_datasets_lifecycle(client: TestClient, sample_valid_zip: Path) -> None:
    """Testa listagem (GET /datasets), detalhamento (GET /datasets/{id}) e deleção (DELETE /datasets/{id})."""
    # 1. Faz upload
    with open(sample_valid_zip, "rb") as f:
        up_res = client.post("/upload", files={"file": ("valid_dataset.zip", f, "application/zip")})
    assert up_res.status_code == 200
    dataset_id = up_res.json()["dataset_id"]

    # 2. Lista datasets
    list_res = client.get("/datasets")
    assert list_res.status_code == 200
    datasets = list_res.json()["datasets"]
    assert len(datasets) >= 1
    ds_ids = [d["dataset_id"] for d in datasets]
    assert dataset_id in ds_ids

    # 3. Consulta detalhes
    detail_res = client.get(f"/datasets/{dataset_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["dataset_id"] == dataset_id
    assert len(detail_data["tables"]) == 1

    # 4. Deleta dataset
    del_res = client.delete(f"/datasets/{dataset_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # 5. Consulta novamente detalhes (espera 404)
    detail_404 = client.get(f"/datasets/{dataset_id}")
    assert detail_404.status_code == 404
    assert detail_404.json()["code"] == "NOT_FOUND"
