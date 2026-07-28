"""Script autônomo para gerar o pacote ZIP limpo do código-fonte para entrega do projeto."""

import os
import zipfile
from pathlib import Path

IGNORE_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".gemini",
    "data/uploads",
}

IGNORE_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".wal", ".html", ".duckdb", ".sqlite", ".sqlite3", ".zip"}
IGNORE_FILES = {"grafico_preview.html", "AI_CSV_Query_Entrega.zip", "entrega_desafio4_ai_csv_query.zip"}


def create_submission_zip(output_zip_name: str = "AI_CSV_Query_Entrega.zip") -> str:
    """Cria um arquivo .zip limpo com todo o código-fonte e documentação do projeto."""
    root_dir = Path(".").resolve()
    output_path = root_dir / output_zip_name

    count = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(root_dir):
            # Filtra diretórios ignorados
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(root_dir)

                # Verifica se o arquivo deve ser ignorado
                if (
                    file in IGNORE_FILES
                    or file_path.suffix in IGNORE_EXTENSIONS
                    or any(part in IGNORE_DIRS for part in rel_path.parts)
                ):
                    continue

                zf.write(file_path, arcname=str(rel_path))
                count += 1

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Pacote de entrega gerado com sucesso!")
    print(f"  • Arquivo : {output_path}")
    print(f"  • Tamanho : {file_size_mb:.2f} MB")
    print(f"  • Arquivos: {count} itens incluídos")

    return str(output_path)


if __name__ == "__main__":
    create_submission_zip()
