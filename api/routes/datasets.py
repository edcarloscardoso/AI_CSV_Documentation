"""Endpoints de listagem, detalhamento e remoção de datasets."""

from typing import Any

from fastapi import APIRouter

from api.contracts import (
    ColumnInfo,
    DatasetListResponse,
    DatasetMetadata,
    TableInfo,
    UploadResponse,
)
from services.deps import get_catalog_service

router = APIRouter(tags=["Datasets"])


@router.get("/datasets", response_model=DatasetListResponse, status_code=200)
async def list_datasets() -> DatasetListResponse:
    """Lista todos os datasets analíticos atualmente cadastrados no catálogo semântico."""
    catalog = get_catalog_service()
    raw_datasets = catalog.list_datasets()

    dataset_metadatas: list[DatasetMetadata] = []

    for ds in raw_datasets:
        ds_id = ds["id"]
        full_info = catalog.get_dataset_full_schema(ds_id)
        
        tables = full_info.get("tables", [])
        table_names = [t["table_name"] for t in tables]
        total_rows = sum(int(t.get("row_count", 0)) for t in tables)

        dataset_metadatas.append(
            DatasetMetadata(
                dataset_id=ds_id,
                name=ds["name"],
                uploaded_at=ds["created_at"],
                tables=table_names,
                row_count_total=total_rows,
            )
        )

    return DatasetListResponse(datasets=dataset_metadatas)


@router.get("/datasets/{dataset_id}", response_model=UploadResponse, status_code=200)
async def get_dataset_details(dataset_id: str) -> UploadResponse:
    """Obtém o esquema detalhado (tabelas e colunas com descrições) de um dataset específico por ID."""
    catalog = get_catalog_service()
    full_info = catalog.get_dataset_full_schema(dataset_id)

    tables_info: list[TableInfo] = []

    for tbl in full_info.get("tables", []):
        cols_info: list[ColumnInfo] = []
        for col in tbl.get("columns", []):
            cols_info.append(
                ColumnInfo(
                    name=col["column_name"],
                    dtype=col["data_type"],
                    description=col.get("description"),
                    sample_values=[],
                )
            )

        tables_info.append(
            TableInfo(
                name=tbl["table_name"],
                row_count=tbl.get("row_count", 0),
                columns=cols_info,
            )
        )

    return UploadResponse(
        dataset_id=dataset_id,
        status="success",
        message=f"Dataset '{full_info['name']}' localizado.",
        tables=tables_info,
    )


@router.delete("/datasets/{dataset_id}", status_code=200)
async def delete_dataset(dataset_id: str) -> dict[str, Any]:
    """Remove um dataset e todas as suas tabelas e colunas vinculadas do catálogo."""
    catalog = get_catalog_service()
    catalog.delete_dataset(dataset_id)
    return {"status": "success", "message": "Dataset removido com sucesso."}
