"""Testes unitários para as funções utilitárias e cliente HTTP do app_streamlit.py."""

from unittest.mock import MagicMock, patch
import pytest

from app_streamlit import (
    ask_question,
    check_backend_health,
    delete_dataset,
    get_dataset_details,
    get_datasets_list,
    upload_zip_file,
)


def test_check_backend_health_success():
    """Testa check_backend_health quando o backend responde HTTP 200 OK."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "ok"}

        assert check_backend_health("http://127.0.0.1:8000") is True


def test_check_backend_health_failure():
    """Testa check_backend_health quando o backend falha ou está offline."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Conexão recusada")

        assert check_backend_health("http://127.0.0.1:8000") is False


def test_get_datasets_list_success():
    """Testa a obtenção da lista de datasets."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "datasets": [
                {
                    "dataset_id": "ds_123",
                    "name": "202401_NFs.zip",
                    "uploaded_at": "2026-07-27T12:00:00Z",
                    "tables": ["notas"],
                    "row_count_total": 100,
                }
            ]
        }

        res = get_datasets_list("http://127.0.0.1:8000")
        assert len(res) == 1
        assert res[0]["dataset_id"] == "ds_123"


def test_get_dataset_details_success():
    """Testa a busca de detalhes de um dataset específico."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "dataset_id": "ds_123",
            "status": "success",
            "message": "Dataset localizado",
            "tables": [],
        }

        res = get_dataset_details("http://127.0.0.1:8000", "ds_123")
        assert res is not None
        assert res["dataset_id"] == "ds_123"


def test_upload_zip_file_success():
    """Testa o envio de arquivo ZIP via upload_zip_file."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "dataset_id": "ds_456",
            "status": "success",
            "message": "Upload concluído",
            "tables": [],
        }

        success, data = upload_zip_file("http://127.0.0.1:8000", b"fake zip content", "test.zip")
        assert success is True
        assert isinstance(data, dict)
        assert data["dataset_id"] == "ds_456"


def test_ask_question_success():
    """Testa a execução de consulta via ask_question."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "answer_text": "O fornecedor com maior valor foi a Empresa X.",
            "answer_type": "text",
            "sql_used": "SELECT * FROM nfs ORDER BY valor DESC LIMIT 1;",
        }

        success, data = ask_question("http://127.0.0.1:8000", "ds_123", "Qual maior fornecedor?")
        assert success is True
        assert isinstance(data, dict)
        assert data["answer_text"].startswith("O fornecedor")


def test_delete_dataset_success():
    """Testa a remoção de um dataset."""
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value.status_code = 200

        assert delete_dataset("http://127.0.0.1:8000", "ds_123") is True
