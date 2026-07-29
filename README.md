# AI CSV Query System — Interface Inteligente para Consulta de Dados CSV

> **I2A2 · Desafio 4 · Entrega Oficial**  
> *Plataforma de Self-Service Business Intelligence impulsionada por Agentes de IA com PydanticAI, DuckDB, FastAPI e Streamlit.*

---

## 💡 Visão de Negócio & Proposta de Valor

Em ambientes corporativos modernos, a extração de insights valiosos a partir de dados operacionais e planilhas CSV frequentemente esbarra em gargalos operacionais: dependência constante da equipe de BI/Analytics, necessidade de conhecimento técnico em SQL/Python e tempo elevado para obtenção de respostas.

O **AI CSV Query System** foi projetado para resolver este entrave através da **democratização total dos dados corporativos**:

- 🚀 **Autosserviço de BI (Self-Service BI / No-Code):** Gestores, auditores e analistas de negócio formulam perguntas analíticas complexas em linguagem natural diretamente aos seus conjuntos de dados (ex: *"Quais fornecedores receberam os maiores valores?"* ou *"Qual foi a evolução temporal dos gastos por mês?"*), eliminando a barreira técnica de bancos de dados.
- ⏱️ **Redução do Tempo até o Insight (Time-to-Insight):** Reduz o ciclo de obtenção de respostas de **dias ou semanas** (espera em filas de chamados tradicionais de BI) para **poucos segundos**, entregando respostas estruturadas em texto explicativo, tabelas resumo e gráficos interativos.
- 🛡️ **Governança e Segurança de Dados (Zero Data Exposure ao LLM):** Garantia de conformidade corporativa e proteção à privacidade. Os arquivos de dados CSV corporativos **nunca são enviados ou expostos ao LLM**; o modelo de IA recebe exclusivamente metadados e esquemas para síntese semântica de SQL. O processamento dos dados em si ocorre 100% no motor OLAP local e isolado (DuckDB), garantindo execução determinística sem riscos de vazamento.

---

## 📊 Motor de Geração de Gráficos & Visualização Interativa (Data Visualization)

O sistema possui um **motor de visualização inteligente e desacoplado** baseado na biblioteca **Plotly**, encarregado de identificar automaticamente o tipo de resposta gráfica mais adequado com base na intenção da pergunta e nos tipos de dados retornados:

| Tipo de Gráfico | Aplicação Principal / Caso de Uso | Gatilhos Semânticos & Decisão Automática |
| :--- | :--- | :--- |
| 📊 **Barras (`bar`)** | **Rankings de desempenho** (Top N maiores/menores), comparações categóricas e volume por entidade. | Perguntas de ranking (ex: *"Quais os 5 maiores fornecedores?"*, *"Volume por produto"*) ou agregações categóricas. |
| 📈 **Linhas (`line`)** | **Séries temporais**, análise de tendência histórica e evolução temporal contínua. | Pergunta contendo termos como *"evolução"*, *"histórico"*, *"tendência"*, *"mensal"*, *"anual"* ou colunas temporais/datas. |
| 🍕 **Pizza / Donut (`pie`)** | **Distribuição proporcional**, participação percentual no total e composição de despesas. | Perguntas que utilizam *"proporção"*, *"distribuição"*, *"porcentagem"*, *"fatia"* com poucas categorias representativas (≤ 6 itens). |

### Fluxo do Motor de Visualização (Engine Flow)

O diagrama abaixo ilustra o **desacoplamento arquitetural completo** entre a orquestração de IA, a execução analítica SQL, a inferência da ferramenta de gráficos e a renderização no frontend:

```
[ Pergunta do Usuário (Linguagem Natural) ]
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                 PydanticAI Orchestrator                     │
│  (Raciocínio Semântico, Validação de Schema & Sintaxe SQL)  │
└───────────────────────────┬─────────────────────────────────┘
                            │ (Consulta & Execução SQL Read-Only)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   DuckDB OLAP Engine                        │
│     (Execução SQL em memória local isolada - Zero LLM leak) │
└───────────────────────────┬─────────────────────────────────┘
                            │ (Dados Estruturados Retornados)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      chart_tool                             │
│  1. Analisa schema (datas, categorias, métricas numéricas)  │
│  2. Avalia gatilhos semânticos e intenção do usuário        │
│  3. Sintetiza Especificação Declarativa Plotly JSON         │
└───────────────────────────┬─────────────────────────────────┘
                            │ (Plotly JSON Spec)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Frontend Streamlit                         │
│  (Renderização Reativa Interativa: Hover, Zoom & PNG Export)│
└─────────────────────────────────────────────────────────────┘
```

---

## 🏛️ Arquitetura do Sistema & Stack Tecnológico

O sistema adota uma arquitetura em 4 camadas totalmente desacopladas, seguindo a diretriz: **"O LLM é o cérebro de raciocínio; as Tools são as mãos de execução."**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND — Streamlit Reativo                       │
│     • Upload de Pacote ZIP (CSVs + Dicionário)    • Chat Interativo     │
│     • Visualização de Tabelas                     • Renderizador Plotly │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP (REST API)
┌────────────────────────────────────▼────────────────────────────────────┐
│                       BACKEND — API FastAPI                             │
│     • POST /upload  • POST /ask  • GET /datasets  • GET /health         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                 ORQUESTRADOR DE AGENTES — PydanticAI                    │
│   ┌──────────────┐   ┌──────────────┐   ┌────────────┐   ┌────────────┐ │
│   │ Schema Tool  │   │  SQL Tool    │   │ Stats Tool │   │ Chart Tool │ │
│   │ (Catálogo)   │   │ (Valida SQL) │   │ (Métricas) │   │ (Plotly)   │ │
│   └──────────────┘   └──────────────┘   └────────────┘   └────────────┘ │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    MOTOR ANALÍTICO — DuckDB & SQLite                     │
│   • DuckDB: Processamento de dados em memória (Alta Performance OLAP)    │
│   • SQLite: Persistência de metadados e dicionário semântico            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Segurança e Tratamento de Dados

- **Proteção contra SQL Injection:** A ferramenta `sql_tool` executa pré-validação AST. Comandos de alteração ou destruição de dados (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`) são sumariamente bloqueados.
- **Prevenção contra Zip Slip:** A extração de pacotes `.zip` faz verificação estrita de *canonical path*, impedindo que arquivos maliciosos sejam gravados fora do ambiente temporário isolado.
- **Tratamento de Tipos e Formatos (BR Numbers):** Trata automaticamente variações numéricas (ex: `1.250,50` ➔ `1250.50`) com `TRY_CAST` SQL para garantir agregações precisas no DuckDB sem falhas de execução.

---

## 📁 Estrutura de Documentação do Projeto

| Diretório | Conteúdo e Propósito |
| :--- | :--- |
| [01-product/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/01-product) | **PRD** — Requisitos funcionais, não-funcionais e casos de uso de negócio. |
| [02-architecture/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/02-architecture) | **Arquitetura** — Especificação do orquestrador, ferramentas (tools) e agentes. |
| [03-api/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/03-api) | **API Specification** — Contratos Pydantic e documentação de endpoints FastAPI. |
| [04-engineering/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/04-engineering) | **Engenharia** — Padrões de código, estrutura do projeto e tratamento de exceções. |
| [05-prompts/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/05-prompts) | **System Prompts** — Prompts otimizados para o agente PydanticAI. |
| [06-testing/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/06-testing) | **Plano de Testes** — Estratégia de validação unitária, integração e E2E. |
| [07-roadmap/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/07-roadmap) | **Roadmap & Plano de Execução** — Acompanhamento detalhado das sprints. |
| [08-appendix/](file:///home/edcarlos/workspace/pessoal/AI_CSV_Documentation/08-appendix) | **Apêndice** — Diagramas complementares e fluxos de dados detalhados. |

---

## 🚀 Guia Rápido de Execução

### 1. Requisitos Prévios e Instalação do Gerenciador `uv`

Este projeto utiliza o gerenciador de ambiente Python ultra-rápido `uv`:

```bash
# Instalar uv (Linux / macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Crie e ative o ambiente virtual instalando as dependências:

```bash
# Criar ambiente virtual
uv venv

# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
uv pip install -r requirements.txt
```

### 2. Configuração das Variáveis de Ambiente

Crie o arquivo `.env` a partir do modelo disponibilizado:

```bash
cp .env.example .env
```

Edite o `.env` e insira sua chave da API do Google Gemini:
```env
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

### 3. Execução do Backend (API FastAPI)

Em um terminal ativo:
```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
> Documentação OpenAPI Swagger disponível em: `http://127.0.0.1:8000/docs`.

### 4. Execução do Frontend (Interface Streamlit)

Em outro terminal ativo:
```bash
uv run streamlit run app_streamlit.py
```
> Acesse a interface web em: `http://localhost:8501`.

---

## 🧪 Suíte de Testes Automatizados

Para executar a suíte completa de testes (cobertura de 34 testes automatizados em serviços, API, agentes, ferramentas de gráfico e testes E2E):

```bash
uv run pytest -v
```

---

## 📄 Geração do Relatório Técnico PDF & Pacote de Entrega

- **Gerar o Relatório Técnico PDF oficial (`Relatorio_Tecnico_AI_CSV_Query.pdf`):**
  ```bash
  uv run python gerar_relatorio_pdf.py
  ```

- **Gerar o Pacote ZIP limpo para Entrega (`entrega_desafio4_ai_csv_query.zip`):**
  ```bash
  uv run python empacotar_entrega.py
  ```

---

*Desenvolvido com excelência técnica e foco em inteligência de negócios para o Desafio 4 — I2A2.*