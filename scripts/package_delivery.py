"""Script para gerar o pacote ZIP de entrega final do projeto."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para importar módulos da raiz
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from empacotar_entrega import create_submission_zip

if __name__ == "__main__":
    zip_path = create_submission_zip("entrega_desafio4_ai_csv_query.zip")
    print(f"✅ Pacote de entrega gerado com sucesso: {zip_path}")
