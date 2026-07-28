# AI CSV Query — Interface Inteligente para Consulta de CSV

> I2A2 · Desafio 4 · Prazo: 16/08/2026

Plataforma de consulta inteligente de dados CSV via linguagem natural, usando agentes de IA com **PydanticAI**, **FastAPI**, **Streamlit** e **DuckDB**.

## Documentação

| Pasta | Conteúdo |
|-------|----------|
| `01-product/` | PRD — Requisitos e casos de uso |
| `02-architecture/` | Arquitetura do sistema, agentes, orchestrator e tools |
| `03-api/` | Especificação da API e contratos Pydantic |
| `04-engineering/` | Padrões de código, estrutura do projeto, tratamento de erros |
| `05-prompts/` | System prompts dos agentes |
| `06-testing/` | Plano de testes |
| `07-roadmap/` | Roadmap de implementação em sprints |
| `08-appendix/` | Fluxo de dados e diagramas complementares |

## Fluxo Resumido

```
ZIP Upload → CSVs → DuckDB → Orchestrator Agent → SQL → Resposta (texto/tabela/gráfico)
```

## Início Rápido

### 1. Instalação do `uv` e Dependências

Caso ainda não possua o `uv` instalado no seu sistema:

```bash
# Instalar uv (Linux / macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Em seguida, crie o ambiente virtual e instale as dependências do projeto:

```bash
# Criar ambiente virtual com uv
uv venv

# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências com uv
uv pip install -r requirements.txt
```

### 2. Configuração de Variáveis de Ambiente

Crie o arquivo `.env` a partir do modelo:
```bash
cp .env.example .env
# Adicione sua GOOGLE_API_KEY no .env
```

### 3. Execução do Backend (FastAPI)

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

A documentação interativa Swagger (OpenAPI) estará disponível em: `http://127.0.0.1:8000/docs`.

### 4. Execução do Frontend (Streamlit)

Em um segundo terminal, inicie a interface gráfica:
```bash
uv run streamlit run app_streamlit.py
```

Acesse a interface gráfica no navegador em: `http://localhost:8501`.

### 5. Execução da Suíte de Testes

```bash
uv run pytest -v
```

Consulte `07-roadmap/IMPLEMENTATION_PLAN.md` para o plano de execução detalhado em sprints.