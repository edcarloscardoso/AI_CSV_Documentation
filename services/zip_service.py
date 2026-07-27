"""Serviço para extração e validação de arquivos ZIP com proteções de segurança."""

import json
import os
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from api.exceptions import FileTooLargeError, InvalidZipError, NoCSVFoundError

DEFAULT_MAX_ZIP_SIZE_MB = 500


@dataclass
class ZipExtractionResult:
    """Resultado do processamento de um arquivo ZIP."""

    extract_dir: Path
    csv_files: list[Path] = field(default_factory=list)
    dictionary_file: Path | None = None
    dictionary_data: dict[str, str] = field(default_factory=dict)


class ZipService:
    """Gerencia a descompressão, validação e extração segura de arquivos ZIP."""

    def __init__(self, max_size_mb: int = DEFAULT_MAX_ZIP_SIZE_MB):
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def validate_and_extract(self, zip_path: str | Path, dest_dir: str | Path) -> ZipExtractionResult:
        """Valida o tamanho, verifica a integridade do ZIP, previne Path Traversal e extrai os arquivos.

        O dicionário de dados é OPCIONAL. Quando ausente, o sistema gera metadados
        automaticamente a partir dos nomes das colunas dos CSVs extraídos.

        Lança:
            InvalidZipError: Se o arquivo não puder ser lido como ZIP.
            FileTooLargeError: Se o ZIP exceder o limite de tamanho configurado.
            NoCSVFoundError: Se nenhum arquivo .csv for localizado.
        """
        zip_file_path = Path(zip_path).resolve()
        destination = Path(dest_dir).resolve()
        destination.mkdir(parents=True, exist_ok=True)

        if not zip_file_path.exists():
            raise InvalidZipError("Arquivo ZIP não encontrado.")

        # Validação de Tamanho do Arquivo
        file_size = zip_file_path.stat().st_size
        if file_size > self.max_size_bytes:
            raise FileTooLargeError(
                f"O arquivo enviado possui {file_size / (1024*1024):.1f}MB, excedendo o limite de {self.max_size_bytes / (1024*1024):.0f}MB."
            )

        if not zipfile.is_zipfile(zip_file_path):
            raise InvalidZipError("O arquivo fornecido não é um arquivo .zip válido.")

        try:
            with zipfile.ZipFile(zip_file_path, "r") as zf:
                # Prevenção contra Zip Slip (Path Traversal)
                for member in zf.infolist():
                    # Resolve o caminho de destino planejado
                    target_path = (destination / member.filename).resolve()
                    # Verifica se o arquivo extraído sairia do diretório de destino
                    if not str(target_path).startswith(str(destination) + os.sep) and target_path != destination:
                        logger.error(f"Tentativa de Zip Slip detectada no arquivo: {member.filename}")
                        raise InvalidZipError(f"Arquivo zip inválido contendo caminho não permitido: {member.filename}")

                # Extrai arquivos de forma segura
                zf.extractall(destination)
                logger.info(f"ZIP extraído com sucesso para: {destination}")

        except zipfile.BadZipFile as e:
            raise InvalidZipError(f"Arquivo zip corrompido: {e!s}") from e

        # Varredura dos arquivos extraídos
        all_extracted_files = [p for p in destination.rglob("*") if p.is_file()]

        # Localiza arquivos CSV
        csv_files = [f for f in all_extracted_files if f.suffix.lower() == ".csv"]
        if not csv_files:
            raise NoCSVFoundError("Nenhum arquivo .csv foi encontrado no pacote ZIP fornecido.")

        # Localiza dicionário de dados (opcional)
        dictionary_file = self._find_dictionary_file(all_extracted_files)
        if dictionary_file:
            dictionary_data = self._parse_dictionary_file(dictionary_file)
            logger.info(f"Dicionário de dados localizado: '{dictionary_file.name}'")
        else:
            logger.info(
                "Nenhum dicionário explícito no ZIP. "
                "Metadados serão inferidos automaticamente dos cabeçalhos dos CSVs."
            )
            dictionary_data = {}

        return ZipExtractionResult(
            extract_dir=destination,
            csv_files=csv_files,
            dictionary_file=dictionary_file,
            dictionary_data=dictionary_data,
        )

    def _find_dictionary_file(self, file_list: list[Path]) -> Path | None:
        """Procura por um arquivo candidato a dicionário de dados."""
        # 1ª prioridade: arquivos que contenham palavras-chave de dicionário
        keywords = ["dicionario", "dicionário", "dict", "schema", "leia-me", "readme"]
        for file_path in file_list:
            fname = file_path.name.lower()
            if any(kw in fname for kw in keywords) and file_path.suffix.lower() in [".txt", ".json", ".csv", ".md"]:
                return file_path

        # 2ª prioridade: qualquer arquivo .txt ou .json que não seja um dos CSVs de dados
        for file_path in file_list:
            if file_path.suffix.lower() in [".txt", ".json", ".md"]:
                return file_path

        return None

    def _parse_dictionary_file(self, dict_path: Path) -> dict[str, str]:
        """Tenta realizar a leitura do dicionário de dados (JSON ou TXT)."""
        try:
            content = dict_path.read_text(encoding="utf-8", errors="ignore")
            if dict_path.suffix.lower() == ".json":
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return {str(k): str(v) for k, v in parsed.items()}
            
            # Se for TXT ou MD, armazena conteúdo bruto em chave genérica 'raw_doc'
            return {"raw_doc": content}
        except Exception as e:
            logger.warning(f"Não foi possível parsear conteúdo estruturado do dicionário '{dict_path.name}': {e}")
            return {}
