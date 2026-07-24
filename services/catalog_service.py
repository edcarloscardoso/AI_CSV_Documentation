"""Serviço de Catálogo Semântico mantido em SQLite."""

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from api.exceptions import DatasetNotFoundError


class CatalogService:
    """Gerencia metadados de datasets, tabelas e colunas em banco SQLite."""

    def __init__(self, db_path: str | Path | None = None):
        """Inicializa banco do catálogo em arquivo ou memória."""
        if db_path and str(db_path) != ":memory:":
            path = Path(db_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = str(path)
            self._persistent_conn: sqlite3.Connection | None = None
        else:
            self.db_path = ":memory:"
            self._persistent_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row

        self._init_db()
        logger.info(f"CatalogService inicializado (db_path={self.db_path})")

    @contextmanager
    def _get_connection(self):
        """Retorna uma conexão atenta se o banco for em memória ou nova conexão para arquivo."""
        if self._persistent_conn is not None:
            yield self._persistent_conn
        else:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()


    def _init_db(self) -> None:
        """Cria as tabelas do catálogo semântico se não existirem."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS datasets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    zip_filename TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tables (
                    id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    csv_filename TEXT NOT NULL,
                    row_count INTEGER DEFAULT 0,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS columns (
                    id TEXT PRIMARY KEY,
                    table_id TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    description TEXT,
                    business_definition TEXT,
                    FOREIGN KEY (table_id) REFERENCES tables (id) ON DELETE CASCADE
                );
            """)

    def register_dataset(
        self,
        name: str,
        zip_filename: str,
        description: str | None = None,
        dataset_id: str | None = None,
    ) -> str:
        """Registra um novo dataset no catálogo."""
        ds_id = dataset_id or str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO datasets (id, name, description, zip_filename, created_at) VALUES (?, ?, ?, ?, ?)",
                (ds_id, name, description or "", zip_filename, created_at),
            )
            conn.commit()
        logger.info(f"Dataset '{name}' ({ds_id}) registrado no catálogo.")
        return ds_id

    def register_table(
        self,
        dataset_id: str,
        table_name: str,
        csv_filename: str,
        row_count: int = 0,
        table_id: str | None = None,
    ) -> str:
        """Registra uma tabela associada a um dataset."""
        tbl_id = table_id or str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO tables (id, dataset_id, table_name, csv_filename, row_count) VALUES (?, ?, ?, ?, ?)",
                (tbl_id, dataset_id, table_name, csv_filename, row_count),
            )
            conn.commit()
        return tbl_id

    def register_column(
        self,
        table_id: str,
        column_name: str,
        data_type: str,
        description: str | None = None,
        business_definition: str | None = None,
    ) -> str:
        """Registra a definição de uma coluna em uma tabela."""
        col_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO columns 
                   (id, table_id, column_name, data_type, description, business_definition) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (col_id, table_id, column_name, data_type, description or "", business_definition or ""),
            )
            conn.commit()
        return col_id

    def get_dataset(self, dataset_id: str) -> dict[str, Any]:
        """Obtém os dados de um dataset por ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
            if not row:
                raise DatasetNotFoundError(f"Dataset com ID '{dataset_id}' não encontrado.")
            return dict(row)

    def list_datasets(self) -> list[dict[str, Any]]:
        """Lista todos os datasets cadastrados."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM datasets ORDER BY created_at DESC").fetchall()
            return [dict(r) for r in rows]

    def get_dataset_full_schema(self, dataset_id: str) -> dict[str, Any]:
        """Retorna o dataset com todas as suas tabelas e colunas (catálogo semântico completo)."""
        dataset = self.get_dataset(dataset_id)
        
        with self._get_connection() as conn:
            tables_rows = conn.execute(
                "SELECT * FROM tables WHERE dataset_id = ?", (dataset_id,)
            ).fetchall()

            tables = []
            for t_row in tables_rows:
                t_dict = dict(t_row)
                cols_rows = conn.execute(
                    "SELECT * FROM columns WHERE table_id = ?", (t_dict["id"],)
                ).fetchall()
                t_dict["columns"] = [dict(c) for c in cols_rows]
                tables.append(t_dict)

            dataset["tables"] = tables
            return dataset

    def delete_dataset(self, dataset_id: str) -> None:
        """Remove um dataset e todas as tabelas e colunas vinculadas (ON DELETE CASCADE)."""
        dataset = self.get_dataset(dataset_id)
        with self._get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
            conn.commit()
        logger.info(f"Dataset '{dataset['name']}' ({dataset_id}) removido do catálogo.")

    def close(self) -> None:
        """Encerra a conexão persistente se houver."""
        if self._persistent_conn is not None:
            try:
                self._persistent_conn.close()
                self._persistent_conn = None
            except Exception as e:
                logger.warning(f"Erro ao fechar conexão SQLite: {e}")

