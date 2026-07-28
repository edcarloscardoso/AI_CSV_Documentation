# Implementation Plan — Roadmap de Execução

**Prazo:** 16/08/2026  
**Início estimado:** 22/07/2026  
**Dias disponíveis:** ~25 dias  

---

## Sprint 1 — Infraestrutura Base
**Dias 1–3**

- [x] Criar estrutura de pastas do projeto
- [x] Configurar `pyproject.toml` (ruff, mypy, pytest)
- [x] Criar `.env.example` com todas as variáveis
- [x] Implementar `services/duckdb_service.py` + testes unitários
- [x] Implementar `services/catalog_service.py` (SQLite para metadados)
- [x] Implementar `services/zip_service.py` (extração + validação)
- [x] FastAPI skeleton com health check (`GET /health`)

**Critério de conclusão:** `pytest tests/` passa; ZIP é extraído e validado corretamente.

---

## Sprint 2 — Upload e Carga de Dados
**Dias 4–7**

- [x] Implementar `agents/loader.py`
- [x] Implementar `api/routes/upload.py` → `POST /upload`
- [x] Implementar `api/routes/datasets.py` → `GET /datasets`, `GET /datasets/{id}`
- [x] Tratamento de erros: `InvalidZipError`, `NoCSVFoundError`, `NoDictionaryError`
- [x] Testes: ZIP válido, sem CSV, sem dicionário, múltiplos CSVs

**Critério de conclusão:** upload de `202401_NFs.zip` funciona; tabelas aparecem no `GET /datasets`.

---

## Sprint 3 — Tools e Agente de Consulta
**Dias 8–13**

- [x] Implementar `tools/schema_tool.py`
- [x] Implementar `tools/sql_tool.py` (com bloqueio de DDL/DML)
- [x] Implementar `tools/stats_tool.py`
- [x] Implementar `agents/orchestrator.py` com PydanticAI
- [x] Implementar `api/routes/query.py` → `POST /ask`
- [x] Retry automático em SQL inválido (1 tentativa)
- [x] Testes: perguntas simples, perguntas inválidas, dataset inexistente

**Critério de conclusão:** perguntas em linguagem natural retornam dados corretos via API.

---

## Sprint 4 — Visualizações
**Dias 14–16**

- [x] Implementar `tools/chart_tool.py` (bar, line, pie, histogram)
- [x] Integrar `chart_tool` no Orchestrator
- [x] Lógica de decisão de formato (texto / tabela / gráfico)
- [x] Testes: verificar tipo de gráfico para cada categoria de pergunta

**Critério de conclusão:** perguntas de série temporal retornam `chart_spec` Plotly válido.

---

## Sprint 5 — Frontend Streamlit
**Dias 17–20**

- [x] Interface A — Upload: drag & drop de ZIP, preview das tabelas
- [x] Interface B — Chat: input de pergunta, histórico de conversa
- [x] Renderização de respostas em texto
- [x] Renderização de tabelas (st.dataframe)
- [x] Renderização de gráficos Plotly (st.plotly_chart)
- [x] Seleção de dataset ativo

**Critério de conclusão:** usuário consegue fazer upload e realizar perguntas pelo navegador.

---

## Sprint 6 — Polimento e Entrega
**Dias 21–25**

- [x] Testes end-to-end com `202401_NFs.zip` e `202505_NFe.zip`
- [x] Validar as 4+ perguntas de demonstração
- [x] Tratamento de erros no frontend (mensagens amigáveis)
- [x] Logging completo com Loguru
- [x] README com instruções de instalação e execução
- [x] Relatório técnico em PDF
- [x] ZIP do código-fonte para entrega
- [x] (Opcional) publicar repositório no GitHub

---

## Dependências Entre Sprints

```
Sprint 1 (infra)
    └── Sprint 2 (upload) ──────────────────────┐
            └── Sprint 3 (tools + agente)        │
                    ├── Sprint 4 (visualização)   │
                    └── Sprint 5 (frontend) ◄─────┘
                            └── Sprint 6 (entrega)
```

---

## Checklist Final de Entrega

- [x] Sistema executa com `uvicorn` + `streamlit` sem erros
- [x] Upload de ZIP funciona
- [x] Agente responde perguntas com dados reais (não inventados)
- [x] Respostas em texto, tabela e gráfico demonstradas
- [x] Pelo menos 4 perguntas documentadas com respostas no relatório
- [x] Framework PydanticAI utilizado e documentado
- [x] `GOOGLE_API_KEY` em `.env` (nunca no código)
- [x] Relatório técnico em PDF entregue (`Relatorio_Tecnico_AI_CSV_Query.pdf`)
- [x] Código-fonte em ZIP entregue (`entrega_desafio4_ai_csv_query.zip`)
