#!/bin/bash
# ========================================================
# 🤖 AI CSV Query System - Inicializador Automático (Linux/macOS)
# ========================================================

echo "========================================================"
echo "  🎈 AI CSV Query System - Passo a Passo Automático 🎈"
echo "========================================================"
echo ""

# 1. Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ [ERRO] O Python3 não foi encontrado!"
    echo "Por favor, instale o Python em https://www.python.org/downloads/"
    exit 1
fi

echo "✅ [Passo 1/4] Python encontrado!"

# 2. Criar ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo "⚙️ [Passo 2/4] Criando a caixinha do sistema (.venv)..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 3. Instalar dependências
echo "📦 Instalando os componentes necessários..."
pip install -q uv
uv pip install -r requirements.txt -q
echo "✅ [Passo 2/4] Tudo instalado com sucesso!"

# 4. Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo ""
    echo "🔑 [Passo 3/4] Precisamos da sua chave da API do Google Gemini!"
    echo "Se você ainda não tem uma, pegue grátis em: https://aistudio.google.com/app/apikey"
    echo ""
    read -p "👉 Cole sua GOOGLE_API_KEY aqui e aperte ENTER: " API_KEY
    echo "GOOGLE_API_KEY=$API_KEY" > .env
    echo "✅ Chave salva no arquivo .env!"
else
    echo "✅ [Passo 3/4] Arquivo de chave .env encontrado!"
fi

# 5. Rodar os testes
echo ""
echo "🧪 [Passo 4/4] Testando se o robô está funcionando direitinho..."
uv run pytest -q

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 EBAAA! Todos os testes passaram! O sistema está pronto!"
else
    echo ""
    echo "⚠️ Ops! Alguns testes falharam. Verifique se sua chave do Gemini está certa no arquivo .env."
fi

echo ""
echo "🚀 Ligando o sistema... Seu navegador vai abrir sozinho em alguns segundos!"
echo "Pressione CTRL + C quando quiser desligar o programa."
echo ""

# Iniciar backend em segundo plano e frontend no navegador
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 3
xdg-open http://localhost:8501 2>/dev/null || open http://localhost:8501 2>/dev/null

uv run streamlit run app_streamlit.py

# Quando o streamlit fechar, encerra o backend
kill $BACKEND_PID 2>/dev/null
