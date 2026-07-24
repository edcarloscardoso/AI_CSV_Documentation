"""Serviço de gerenciamento e consulta no DuckDB."""

from pathlib import Path
from typing import Any

import duckdb
from loguru import logger

from api.exceptions import SQLExecutionError, UnsafeQueryError

# Palavras-chave proibidas para garantir execução estritamente somente-leitura (SELECT)
FORBIDDEN_SQL_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "INSTALL",
    "LOAD",
    "COPY",
    "PRAGMA",
    "VACUUM",
    "CALL",
    "EXPORT",
    "IMPORT",
}


class DuckDBService:
    """Serviço para gerenciar conexão DuckDB e executar consultas com segurança."""

    def __init__(self, db_path: str | Path | None = None):
        """Inicializa a conexão DuckDB (arquivo ou em memória se db_path for None ou ':memory:')."""
        if db_path and str(db_path) != ":memory:":
            path = Path(db_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = duckdb.connect(str(path))
            self.is_memory = False
        else:
            self.conn = duckdb.connect(":memory:")
            self.is_memory = True
        logger.info(f"DuckDBService inicializado (in_memory={self.is_memory})")

    def execute_query(self, sql_query: str, max_rows: int = 500) -> list[dict[str, Any]]:
        """Executa uma instrução SQL SELECT e retorna lista de dicionários com os resultados.

        Lança UnsafeQueryError para tentativas de DDL/DML.
        Lança SQLExecutionError para erros de sintaxe ou execução.
        """
        cleaned_sql = sql_query.strip().strip(";").strip()
        tokens = [token.upper() for token in cleaned_sql.split()]

        # Validação básica de comando somente-leitura
        if not tokens or tokens[0] != "SELECT":
            raise UnsafeQueryError("Apenas consultas SELECT são permitidas.")

        for token in tokens:
            # Remove pontuações/caracteres do token para checagem de palavra-chave
            clean_token = "".join(c for c in token if c.isalnum() or c == "_")
            if clean_token in FORBIDDEN_SQL_KEYWORDS:
                raise UnsafeQueryError(
                    f"Comando SQL não permitido contendo palavra-chave reservada: {clean_token}"
                )

        # Adiciona LIMIT se não houver um LIMIT explícito na query
        if "LIMIT" not in tokens:
            cleaned_sql += f" LIMIT {max_rows}"

        try:
            rel = self.conn.sql(cleaned_sql)
            if rel is None:
                return []
            
            df = rel.df()
            # Trata tipos nulos/NaN para conversão limpa em dicionário Python
            df = df.where(df.notna(), None)
            return df.to_dict(orient="records")  # type: ignore[no-any-return]
        except duckdb.Error as e:
            logger.error(f"Erro na execução SQL no DuckDB: {e} | Query: {sql_query}")
            raise SQLExecutionError(f"Erro ao executar consulta SQL: {e!s}") from e
        except Exception as e:
            logger.error(f"Erro inesperado no DuckDB: {e}")
            raise SQLExecutionError(f"Erro na execução da consulta: {e!s}") from e

    def register_csv_view(self, table_name: str, csv_path: str | Path) -> None:
        """Cria ou substitui uma VIEW no DuckDB apontando diretamente para um arquivo CSV."""
        path = Path(csv_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {path}")

        sanitized_table = "".join(c for c in table_name if c.isalnum() or c == "_")
        if not sanitized_table:
            raise ValueError(f"Nome de tabela inválido: {table_name}")

        query = f"CREATE OR REPLACE VIEW {sanitized_table} AS SELECT * FROM read_csv_auto('{path.as_posix()}')"
        try:
            self.conn.execute(query)
            logger.info(f"View '{sanitized_table}' criada com sucesso a partir de {path.name}")
        except duckdb.Error as e:
            logger.error(f"Falha ao registrar VIEW do CSV '{path}': {e}")
            raise SQLExecutionError(f"Não foi possível carregar o CSV '{path.name}': {e!s}") from e

    def get_table_schema(self, table_name: str) -> list[dict[str, str]]:
        """Retorna os nomes de colunas e tipos de dados de uma tabela/view no DuckDB."""
        sanitized_table = "".join(c for c in table_name if c.isalnum() or c == "_")
        try:
            res = self.conn.execute(f"DESCRIBE {sanitized_table}").fetchall()
            return [{"column_name": row[0], "column_type": str(row[1])} for row in res]
        except duckdb.Error as e:
            raise SQLExecutionError(f"Erro ao obter esquema da tabela '{table_name}': {e!s}") from e

    def close(self) -> None:
        """Fecha a conexão DuckDB."""
        try:
            self.conn.close()
            logger.info("Conexão DuckDB encerrada.")
        except Exception as e:
            logger.warning(f"Erro ao fechar conexão DuckDB: {e}")
