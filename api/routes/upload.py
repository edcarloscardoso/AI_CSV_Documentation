"""Endpoint de upload de arquivos ZIP com CSVs e dicionário."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from loguru import logger

from agents.loader import LoaderAgent, LoadInput
from api.contracts import UploadResponse
from api.exceptions import FileTooLargeError, InvalidZipError
from services.deps import get_catalog_service, get_duckdb_service

router = APIRouter(tags=["Upload"])


@router.post("/upload", response_model=UploadResponse, status_code=200)
async def upload_dataset(file: UploadFile = File(...)) -> UploadResponse:
    """Recebe um arquivo ZIP contendo CSVs e Dicionário de dados para ingestão analítica."""
    filename = file.filename or ""
    if not filename.lower().endswith(".zip"):
        raise InvalidZipError("O arquivo enviado precisa possuir a extensão .zip.")

    upload_dir = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)

    temp_zip_path = upload_dir / f"upload_{uuid.uuid4().hex}_{filename}"

    try:
        # Grava os bytes do upload no arquivo de destino
        content = await file.read()
        
        # Validação antecipada de limite de tamanho em MB se configurado
        max_mb = int(os.getenv("MAX_ZIP_SIZE_MB", "200"))
        if len(content) > max_mb * 1024 * 1024:
            raise FileTooLargeError(f"O arquivo enviado excede o limite máximo permitido de {max_mb}MB.")

        with open(temp_zip_path, "wb") as f:
            f.write(content)

        logger.info(f"Arquivo recebido no /upload: {filename} ({len(content)} bytes)")

        # Executa a carga via Loader Agent
        loader = LoaderAgent(
            duckdb_service=get_duckdb_service(),
            catalog_service=get_catalog_service(),
        )

        load_input = LoadInput(
            zip_path=temp_zip_path,
            dataset_name=Path(filename).stem,
        )

        result = loader.load(load_input)
        return result.to_upload_response()

    finally:
        # Garante a remoção do arquivo ZIP após o término do processamento
        if temp_zip_path.exists():
            try:
                temp_zip_path.unlink()
            except Exception as e:
                logger.warning(f"Não foi possível apagar arquivo temporário de upload '{temp_zip_path}': {e}")
