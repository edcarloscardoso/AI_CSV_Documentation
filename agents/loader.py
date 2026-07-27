"""Agente de Carga (Loader Agent) responsável por orquestrar a validação e ingestão do ZIP."""

import os
import re
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent

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


class _DictionaryResult(BaseModel):
    """Modelo Pydantic para o resultado de geração de dicionário via LLM."""

    descriptions: dict[str, str]


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
        sanitized = re.sub(r"[^a-z0-9_]", "_", stem)
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")
        if not sanitized:
            sanitized = "tabela_dados"
        if sanitized[0].isdigit():
            sanitized = f"t_{sanitized}"
        return sanitized

    # ──────────────────────────────────────────────────────────────────────────
    # Geração automática de dicionário de dados
    # ──────────────────────────────────────────────────────────────────────────

    def _build_columns_info_for_dict(
        self, table_name: str, raw_schema: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Coleta schema + amostras de valores para subsidiar a geração do dicionário."""
        try:
            sample_rows = self.duckdb_service.execute_query(
                f"SELECT * FROM {table_name} LIMIT 5"
            )
        except Exception as e:
            logger.warning(f"Não foi possível obter amostras de '{table_name}': {e}")
            sample_rows = []

        result = []
        for col in raw_schema:
            col_name = col["column_name"]
            col_type = col["column_type"]
            samples = [
                row[col_name]
                for row in sample_rows
                if col_name in row and row[col_name] is not None
            ][:5]
            result.append({"name": col_name, "type": col_type, "samples": samples})
        return result

    def _generate_dictionary_with_llm(
        self,
        table_name: str,
        csv_filename: str,
        columns_info: list[dict[str, Any]],
    ) -> dict[str, str]:
        """Usa PydanticAI para gerar descrições semânticas das colunas via LLM."""
        model_name = os.getenv("GEMINI_MODEL") or os.getenv("LLM_MODEL", "google:gemini-2.0-flash")
        if not model_name.startswith(("google:", "google-gla:", "google-vertex:", "openai:", "anthropic:")):
            model_name = f"google:{model_name}"

        agent: Agent[None, _DictionaryResult] = Agent(
            model_name,
            output_type=_DictionaryResult,
            system_prompt=(
                "Você é um analista de dados especialista em documentação de dados. "
                "Dado o nome, tipo e exemplos de valores de cada coluna de um arquivo CSV, "
                "gere uma descrição semântica CONCISA (máx. 12 palavras) em português para cada coluna. "
                "Retorne APENAS o objeto 'descriptions' com {nome_exato_da_coluna: descricao_curta}."
            ),
        )

        columns_text = "\n".join(
            f"  - {c['name']} ({c['type']}): exemplos → {c['samples'][:3]}"
            for c in columns_info
        )
        prompt = (
            f"Arquivo CSV: {csv_filename}\n"
            f"Tabela: {table_name}\n\n"
            f"Colunas:\n{columns_text}\n\n"
            "Gere uma descrição semântica concisa para cada coluna acima."
        )

        import asyncio
        import concurrent.futures
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(agent.run_sync, prompt).result()
        else:
            result = agent.run_sync(prompt)

        return result.data.descriptions

    def _generate_basic_dictionary(
        self, columns_info: list[dict[str, Any]]
    ) -> dict[str, str]:
        """Fallback: gera descrições básicas humanizando os nomes das colunas."""
        dictionary: dict[str, str] = {}
        for col in columns_info:
            name: str = col["name"]
            col_type: str = col["type"]
            samples = [str(s) for s in col["samples"][:2]]
            sample_str = f" (ex: {', '.join(samples)})" if samples else ""
            human_name = name.replace("_", " ").title()
            dictionary[name] = f"{human_name} — {col_type}{sample_str}"
        return dictionary

    def auto_generate_dictionary(
        self,
        table_name: str,
        csv_filename: str,
        raw_schema: list[dict[str, Any]],
    ) -> dict[str, str]:
        """Gera automaticamente um dicionário de dados para a tabela indicada.

        Tenta usar o LLM para gerar descrições semânticas ricas. Se não houver
        chave de API configurada, usa humanização simples dos nomes das colunas.
        """
        columns_info = self._build_columns_info_for_dict(table_name, raw_schema)

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        if api_key:
            try:
                logger.info(
                    f"Gerando dicionário automático via LLM para tabela '{table_name}'..."
                )
                dictionary = self._generate_dictionary_with_llm(
                    table_name, csv_filename, columns_info
                )
                logger.info(
                    f"Dicionário auto-gerado com sucesso para '{table_name}' "
                    f"({len(dictionary)} colunas descritas pelo LLM)."
                )
                return dictionary
            except Exception as e:
                logger.warning(
                    f"LLM falhou ao gerar dicionário para '{table_name}' ({e}). "
                    "Usando fallback de humanização básica."
                )

        # Fallback sem LLM
        basic = self._generate_basic_dictionary(columns_info)
        logger.info(
            f"Dicionário básico gerado para '{table_name}' ({len(basic)} colunas)."
        )
        return basic

    # ──────────────────────────────────────────────────────────────────────────
    # Fluxo principal de carga
    # ──────────────────────────────────────────────────────────────────────────

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
            explicit_dict = extraction_result.dictionary_data  # {} se nenhum dicionário no ZIP

            if not explicit_dict:
                logger.info(
                    "Nenhum dicionário explícito encontrado no ZIP. "
                    "Dicionários serão auto-gerados por tabela após a carga no DuckDB."
                )

            # 2. Registra o Dataset no catálogo semântico
            self.catalog_service.register_dataset(
                name=dataset_name,
                zip_filename=zip_file_path.name,
                description=explicit_dict.get("raw_doc", f"Dataset {dataset_name}"),
                dataset_id=dataset_id,
            )

            processed_tables: list[TableInfo] = []

            # 3. Processa cada CSV localizado no pacote ZIP
            for csv_file in extraction_result.csv_files:
                table_name = self._sanitize_table_name(csv_file.name)

                # Cria VIEW no DuckDB
                try:
                    self.duckdb_service.register_csv_view(table_name, csv_file)
                except Exception as e:
                    raise InvalidCSVError(
                        f"Erro ao ler arquivo CSV '{csv_file.name}': {e}"
                    ) from e

                # Valida número de linhas
                count_res = self.duckdb_service.execute_query(
                    f"SELECT COUNT(*) as total FROM {table_name}"
                )
                row_count = int(count_res[0]["total"]) if count_res else 0
                if row_count == 0:
                    raise InvalidCSVError(
                        f"O arquivo CSV '{csv_file.name}' está vazio (0 linhas)."
                    )

                # Obtém esquema das colunas
                raw_schema = self.duckdb_service.get_table_schema(table_name)

                # Determina o dicionário de dados a usar para esta tabela:
                # - Se havia dicionário explícito no ZIP → usa-o
                # - Se não havia → gera automaticamente via LLM (ou fallback básico)
                if explicit_dict:
                    dict_data = explicit_dict
                else:
                    dict_data = self.auto_generate_dictionary(
                        table_name=table_name,
                        csv_filename=csv_file.name,
                        raw_schema=raw_schema,
                    )

                # Coleta amostra de valores (até 3 linhas)
                sample_rows = self.duckdb_service.execute_query(
                    f"SELECT * FROM {table_name} LIMIT 3"
                )

                # Registra tabela no catálogo semântico
                table_id = self.catalog_service.register_table(
                    dataset_id=dataset_id,
                    table_name=table_name,
                    csv_filename=csv_file.name,
                    row_count=row_count,
                )

                columns_info_list: list[ColumnInfo] = []

                for col in raw_schema:
                    col_name = col["column_name"]
                    col_type = col["column_type"]

                    # Busca descrição no dicionário gerado (insensível a maiúsculas/minúsculas)
                    col_desc = dict_data.get(col_name)
                    if not col_desc:
                        for k, v in dict_data.items():
                            if k.lower() == col_name.lower():
                                col_desc = str(v)
                                break

                    # Extrai amostra da coluna
                    sample_vals = [
                        row.get(col_name)
                        for row in sample_rows
                        if row.get(col_name) is not None
                    ]

                    # Registra coluna no catálogo semântico
                    self.catalog_service.register_column(
                        table_id=table_id,
                        column_name=col_name,
                        data_type=col_type,
                        description=col_desc,
                    )

                    columns_info_list.append(
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
                        columns=columns_info_list,
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
