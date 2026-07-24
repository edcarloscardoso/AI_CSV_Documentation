"""Modelos Pydantic para contratos de requisição e resposta da API."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    """Informações de esquema de uma coluna."""

    name: str = Field(..., description="Nome da coluna")
    dtype: str = Field(..., description="Tipo de dado no DuckDB")
    description: str | None = Field(default=None, description="Descrição semântica vinda do dicionário")
    sample_values: list[Any] = Field(default_factory=list, description="Amostra de valores da coluna")


class TableInfo(BaseModel):
    """Informações de uma tabela pertencente a um dataset."""

    name: str = Field(..., description="Nome da tabela")
    row_count: int = Field(..., description="Quantidade total de linhas na tabela")
    columns: list[ColumnInfo] = Field(default_factory=list, description="Lista de colunas da tabela")


class UploadResponse(BaseModel):
    """Resposta retornada pelo endpoint de upload POST /upload."""

    dataset_id: str = Field(..., description="Identificador único do dataset gerado")
    status: Literal["success", "error"] = Field(..., description="Status do processamento")
    message: str = Field(..., description="Mensagem descritiva de conclusão")
    tables: list[TableInfo] = Field(default_factory=list, description="Tabelas carregadas")


class DatasetMetadata(BaseModel):
    """Resumo de metadados de um dataset cadastrado."""

    dataset_id: str = Field(..., description="ID do dataset")
    name: str = Field(..., description="Nome amigável do dataset")
    uploaded_at: str = Field(..., description="Data/hora de upload no formato ISO")
    tables: list[str] = Field(default_factory=list, description="Nomes das tabelas contidas")
    row_count_total: int = Field(default=0, description="Total acumulado de linhas")


class DatasetListResponse(BaseModel):
    """Resposta para o endpoint GET /datasets."""

    datasets: list[DatasetMetadata] = Field(default_factory=list, description="Lista de datasets cadastrados")


class ErrorResponse(BaseModel):
    """Formato padronizado de respostas de erro da API."""

    error: str = Field(..., description="Nome da exceção gerada")
    detail: str = Field(..., description="Mensagem de erro detalhada")
    code: str = Field(..., description="Código único do erro para consumo de clientes")
