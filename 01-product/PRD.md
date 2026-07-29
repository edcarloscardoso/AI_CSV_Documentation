# PRD — Product Requirements Document
## AI CSV Query System — Interface Inteligente para Consulta de CSV

**Versão:** 1.1  
**Data:** 2026-07-28  
**Projeto:** I2A2 · Desafio 4  

---

## 🎯 Objetivo & Proposta de Valor de Negócio

Desenvolver uma plataforma de **Autosserviço de Business Intelligence (Self-Service BI / No-Code)** que permita a qualquer profissional de negócio — sem conhecimento técnico em SQL, Python ou fórmulas avançadas de Excel — interrogar arquivos CSV corporativos em linguagem natural e obter instantaneamente respostas estruturadas em formato de **texto explicativo**, **tabelas de dados** ou **gráficos interativos**.

### Principais Benefícios de Negócio:
- 🚀 **Autosserviço BI sem Código (No-Code BI):** Democratização do acesso a dados operacionais e financeiros. Usuários fazem perguntas como *"Qual foi o total gasto em cada mês?"* e recebem análises prontas sem passar por intermediários.
- ⏱️ **Redução do Tempo até o Insight (Time-to-Insight):** Transforma semanas/dias de espera por demandas na fila de TI/BI em respostas analíticas geradas em **poucos segundos**.
- 🛡️ **Governança e Segurança de Dados (Zero Data Exposure ao LLM):** Leitura determinística de dados operacionais sem expor arquivos ou planilhas corporativas ao modelo de IA. Apenas metadados de esquemas e sintaxe SQL transitam pela IA; todo o volume de dados brutos permanece isolado no motor OLAP local (DuckDB).

---

## 👤 Usuário-Alvo

Profissionais de negócio (financeiro, suprimentos, vendas, auditoria) que gerenciam planilhas CSV e precisam extrair indicadores e padrões sem digitar comandos de banco de dados.

---

## 📋 Casos de Uso

| ID | Caso de Uso | Descrição de Negócio | Prioridade |
|----|-------------|----------------------|------------|
| UC-01 | Upload de Pacote ZIP | Usuário envia arquivo ZIP contendo CSVs e dicionário de dados | Alta |
| UC-02 | Ingestão e Processamento | Sistema cataloga os dados e disponibiliza tabelas em memória | Alta |
| UC-03 | Pergunta em Linguagem Natural | Usuário faz pergunta analítica em português (ex: "Total gasto no mês") | Alta |
| UC-04 | Resposta em Texto | Apresentação de valores pontuais ou resumos executivos | Alta |
| UC-05 | Resposta em Tabela | Apresentação de detalhamentos estruturados (ex: Top 5 fornecedores) | Alta |
| UC-06 | Resposta em Gráfico Interativo | Renderização automática de gráficos de Barras, Linhas ou Pizza | Média |
| UC-07 | Inspeção de Datasets | Visualização dos schemas, tipos de colunas e preview de 5 linhas | Média |
| UC-08 | Chat Continuo | Conversação contínua mantendo o contexto do conjunto de dados | Média |

---

## ⚙️ Requisitos Funcionais

### RF-01 — Upload e Validação de Dados
- Aceitar arquivos `.zip` contendo um ou mais `.csv` e um dicionário de dados (JSON, CSV ou XLSX).
- Validar a estrutura do ZIP contra Zip Slip e extrair em diretório isolado por sessão.
- Apresentar catálogo com nomes de tabelas, colunas, tipos inferidos e preview de 5 linhas.

### RF-02 — Processamento OLAP em Memória
- Carregar CSVs em tabelas DuckDB nomeadas automaticamente.
- Utilizar o dicionário de dados para enriquecer os prompts do orquestrador de IA.
- Fazer conversão de tipos (ex: datas, valores monetários em formato brasileiro `TRY_CAST`).

### RF-03 — Interface de Consulta Natural
- Interpretar perguntas em português via PydanticAI + Gemini 2.0.
- Sintetizar consultas SQL válidas e executá-las de forma determinística no DuckDB.

### RF-04 — Motor de Formatos de Resposta & Visualização Gráfica (Plotly Engine)
- **Texto Explicativo:** Para valores únicos, agregados pontuais ou esclarecimentos conceituais.
- **Tabela Estruturada:** Para agrupamentos com múltiplos registros e detalhamentos numéricos.
- **Gráficos Interativos (Plotly Engine):**
  - 📊 **Barras (`bar`):** Rankings de desempenho (Top N maiores/menores) e comparações entre categorias.
  - 📈 **Linhas (`line`):** Análise de séries temporais, tendências históricas e evolução de despesas ao longo do tempo.
  - 🍕 **Pizza / Donut (`pie`):** Distribuição proporcional, participação percentual no total e composição de fatias representativas (≤ 6 itens).

#### Fluxo Arquitetural do Motor de Gráficos (Engine Flow)
```
[ Pergunta em Linguagem Natural ] 
            │
            ▼
[ PydanticAI Orchestrator ] ──(Consulta Schema)──► [ DuckDB OLAP Engine ]
            │                                              │
            ▼                                              ▼
[ Dados Estruturados ] ◄───────────────────────── [ Execução SQL Read-Only ]
            │
            ▼
[ chart_tool ]
  ├── 1. Inferência de Tipos (Temporais, Categóricos, Métricas)
  ├── 2. Mapeamento de Gatilhos Semânticos (Ranking, Tendência, Proporção)
  └── 3. Síntese da Especificação Declarativa Plotly JSON
            │
            ▼
[ Streamlit UI ] ──► Renderização Reativa & Interatividade (Hover/Zoom/Export)
```

---

## 🛡️ Requisitos Não-Funcionais

| Requisito | Critério de Aceite |
|-----------|--------------------|
| Desempenho | Resposta em menos de 15 segundos para datasets até 100MB |
| Segurança | SQL Injection bloqueado (comportamento estritamente Read-Only); Zip Slip bloqueado |
| Usabilidade | Interface intutiva em Streamlit sem necessidade de treinamento técnico |
| Confiabilidade | SQL validado com `EXPLAIN` antes de executar; tratamento elegante de erros |

---

## 📊 Perguntas de Exemplo de Negócio (Dataset NFs)

1. *"Qual fornecedor recebeu o maior valor no período?"* ➔ Resposta: Texto com Valor e Fornecedor
2. *"Qual produto apresentou o maior volume comprado?"* ➔ Resposta: Texto com Produto e Quantidade
3. *"Qual foi o total gasto em cada mês?"* ➔ Resposta: Gráfico de Linha (Série Temporal)
4. *"Quais foram os cinco maiores fornecedores?"* ➔ Resposta: Tabela Top 5 ou Gráfico de Barras
5. *"Qual categoria apresentou maior crescimento nas compras?"* ➔ Resposta: Tabela / Gráfico Comparativo

---

## 🚫 Fora de Escopo (MVP)

- Autenticação e gestão de usuários multi-tenant.
- Deploy em ambiente de nuvem distribuído.
- Modificação de dados brutos (operação 100% somente-leitura).
