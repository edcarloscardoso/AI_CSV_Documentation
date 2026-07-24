"""Agente de Carga (Loader Agent) responsável por orquestrar a validação e ingestão do ZIP."""

import re
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from loguru import logger

from api.contracts import ColumnInfo, TableInfo, UploadResponse
from api.exceptions import InvalidCSVError
from services.catalog_service import CatalogService
from services.deps import get_catalog_service, get_duckdb_service
from services.duckdb_service import DuckDBService
from services.zip_service import ZipService


@dataclass
class LoadInput:
    """Dados de entrada para execução do Loader Agent."""

    zip_path: str | Path
    dataset_name: str | None = None
    dataset_id: str | None = None


@dataclass
class LoadResult:
    """Resultado da execução do Loader Agent."""

    dataset_id: str
    status: Literal["success", "error"]
    message: str
    tables: list[TableInfo] = field(default_factory=list)

    def to_upload_response(self) -> UploadResponse:
        """Converte o resultado no contrato oficial UploadResponse."""
        return UploadResponse(
            dataset_id=self.dataset_id,
            status=self.status,
            message=self.message,
            tables=self.tables,
        )


class LoaderAgent:
    """Agente responsável pelo processamento, validação e carga dos dados contidos no pacote ZIP."""

    def __init__(
        self,
        duckdb_service: DuckDBService | None = None,
        catalog_service: CatalogService | None = None,
        zip_service: ZipService | None = None,
    ):
        self.duckdb_service = duckdb_service or get_duckdb_service()
        self.catalog_service = catalog_service or get_catalog_service()
        self.zip_service = zip_service or ZipService()

    def _sanitize_table_name(self, filename: str) -> str:
        """Sanitiza e normaliza o nome do arquivo para um identificador de tabela SQL seguro."""
        stem = Path(filename).stem.lower()
        # Subsitui espaços, traços e caracteres especiais por '_'
        sanitized = re.sub(r"[^a-z0-9_]", "_", stem)
        # Remove underlines duplicados e reduz bordas
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")
        if not sanitized:
            sanitized = "tabela_dados"
        return sanitized

    def load(self, load_input: LoadInput) -> LoadResult:
        """Processa o pacote ZIP e efetua a carga no DuckDB e Catálogo Semântico."""
        zip_file_path = Path(load_input.zip_path)
        dataset_name = load_input.dataset_name or zip_file_path.stem
        dataset_id = load_input.dataset_id or f"ds_{uuid.uuid4().hex[:12]}"

        # Diretório temporário para extração segura
        temp_dir = Path(tempfile.mkdtemp(prefix="zip_extract_"))

        try:
            logger.info(f"Iniciando Loader Agent para dataset '{dataset_name}' ({dataset_id})")
            
            # 1. Extrai e valida ZIP
            extraction_result = self.zip_service.validate_and_extract(zip_file_path, temp_dir)
            dict_data = extraction_result.dictionary_data

            # 2. Registra o Dataset no catálogo semântico
            self.catalog_service.register_dataset(
                name=dataset_name,
                zip_filename=zip_file_path.name,
                description=dict_data.get("raw_doc", f"Dataset {dataset_name}"),
                dataset_id=dataset_id,
            )

            processed_tables: list[TableInfo] = []

            # 3. Processa cada CSV localizado no pacote ZIP
            for csv_file in extraction_result.csv_files:
                table_name = self. _sanitize_table_name(csv_file.name)

                # Cria VIEW no DuckDB
                try:
                    self.duckdb_service.register_csv_view(table_name, csv_file)
                except Exception as e:
                    raise InvalidCSVError(f"Erro ao ler arquivo CSV '{csv_file.name}': {e}") from e

                # Valida número de linhas
                count_res = self.duckdb_service.execute_query(f"SELECT COUNT(*) as total FROM {table_name}")
                row_count = int(count_res[0]["total"]) if count_res else 0
                if row_count == 0:
                    raise InvalidCSVError(f"O arquivo CSV '{csv_file.name}' está vazio (0 linhas).")

                # Obtém esquema das colunas
                raw_schema = self.duckdb_service.get_table_schema(table_name)
                
                # Coleta amostra de valores (até 3 linhas)
                sample_rows = self.duckdb_service.execute_query(f"SELECT * FROM {table_name} LIMIT 3")

                # Registra tabela no catálogo semântico
                table_id = self.catalog_service.register_table(
                    dataset_id=dataset_id,
                    table_name=table_name,
                    csv_filename=csv_file.name,
                    row_count=row_count,
                )

                columns_info: list[ColumnInfo] = []

                for col in raw_schema:
                    col_name = col["column_name"]
                    col_type = col["column_type"]

                    # Busca descrição no dicionário (busca insensível a maiúsculas/minúsculas)
                    col_desc = dict_data.get(col_name)
                    if not col_desc:
                        for k, v in dict_data.items():
                            if k.lower() == col_name.lower():
                                col_desc = str(v)
                                break

                    # Extrai amostra da coluna
                    sample_vals = [row.get(col_name) for row in sample_rows if row.get(col_name) is not None]

                    # Registra coluna no catálogo semântico
                    self.catalog_service.register_column(
                        table_id=table_id,
                        column_name=col_name,
                        data_type=col_type,
                        description=col_desc,
                    )

                    columns_info.append(
                        ColumnInfo(
                            name=col_name,
                            dtype=col_type,
                            description=col_desc,
                            sample_values=sample_vals,
                        )
                    )

                processed_tables.append(
                    TableInfo(
                        name=table_name,
                        row_count=row_count,
                        columns=columns_info,
                    )
                )

            msg = f"{len(processed_tables)} tabela(s) carregada(s) com sucesso."
            logger.info(f"Loader Agent concluído com sucesso: {msg}")

            return LoadResult(
                dataset_id=dataset_id,
                status="success",
                message=msg,
                tables=processed_tables,
            )

        finally:
            # Limpeza do diretório temporário
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Erro ao remover diretório temporário '{temp_dir}': {e}")
