"""Script para gerar o Relatório Técnico PDF oficial do projeto AI CSV Query."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para importar módulos da raiz
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from gerar_relatorio_pdf import build_pdf_report

if __name__ == "__main__":
    pdf_path = build_pdf_report("Relatorio_Tecnico_AI_CSV_Query.pdf")
    print(f"✅ Relatório técnico gerado com sucesso: {pdf_path}")
