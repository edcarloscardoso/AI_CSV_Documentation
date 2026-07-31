@echo off
chcp 65001 > nul
title AI CSV Query System - Inicializador Automático

echo ========================================================
echo   🎈 AI CSV Query System - Passo a Passo Automático 🎈
echo ========================================================
echo.

:: 1. Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ [ERRO] O Python não foi encontrado no seu computador!
    echo Por favor, peça ajuda para instalar o Python em: https://www.python.org/downloads/
    echo ⚠️ IMPORTANTE: Marque a caixinha "Add Python to PATH" ao instalar!
    echo.
    pause
    exit /b
)

echo ✅ [Passo 1/4] Python encontrado!

:: 2. Criar ambiente virtual se não existir
if not exist ".venv" (
    echo ⚙️ [Passo 2/4] Criando a caixinha do sistema (.venv)...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

:: 3. Instalar dependências
echo 📦 Instalando os componentes necessários...
python -m pip install --quiet uv
uv pip install -r requirements.txt --quiet
echo ✅ [Passo 2/4] Tudo instalado com sucesso!

:: 4. Verificar arquivo .env
if not exist ".env" (
    echo.
    echo 🔑 [Passo 3/4] Precisamos da sua chave da API do Google Gemini!
    echo Se você ainda não tem uma, pegue grátis em: https://aistudio.google.com/app/apikey
    echo.
    set /p API_KEY="👉 Cole sua GOOGLE_API_KEY aqui e aperte ENTER: "
    echo GOOGLE_API_KEY=%API_KEY% > .env
    echo ✅ Chave salva no arquivo .env com sucesso!
    echo.
) else (
    echo ✅ [Passo 3/4] Arquivo de chave .env encontrado!
)

:: 5. Executar os testes
echo.
echo 🧪 [Passo 4/4] Testando se o robô está funcionando direitinho...
uv run pytest -q
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Ops! Alguns testes falharam. Verifique se sua chave do Gemini está certa no arquivo .env.
    echo Pressione qualquer tecla para tentar abrir o sistema mesmo assim...
    pause > nul
) else (
    echo.
    echo 🎉 EBAAA! Todos os testes passaram! O sistema está pronto!
)

echo.
echo 🚀 Ligando o sistema... Seu navegador vai abrir sozinho em alguns segundos!
echo.

:: 6. Abrir a API no fundo e o Streamlit no navegador
start /b uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
timeout /t 3 > nul
start http://localhost:8501
uv run streamlit run app_streamlit.py

pause
