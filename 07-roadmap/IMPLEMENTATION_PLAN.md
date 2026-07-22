# Implementation Plan — Roadmap de Execução

**Prazo:** 16/08/2026  
**Início estimado:** 22/07/2026  
**Dias disponíveis:** ~25 dias  

---

## Sprint 1 — Infraestrutura Base
**Dias 1–3**

- [ ] Criar estrutura de pastas do projeto
- [ ] Configurar `pyproject.toml` (ruff, mypy, pytest)
- [ ] Criar `.env.example` com todas as variáveis
- [ ] Implementar `services/duckdb_service.py` + testes unitários
- [ ] Implementar `services/catalog_service.py` (SQLite para metadados)
- [ ] Implementar `services/zip_service.py` (extração + validação)
- [ ] FastAPI skeleton com health check (`GET /health`)

**Critério de conclusão:** `pytest tests/` passa; ZIP é extraído e validado corretamente.

---

## Sprint 2 — Upload e Carga de Dados
**Dias 4–7**

- [ ] Implementar `agents/loader.py`
- [ ] Implementar `api/routes/upload.py` → `POST /upload`
- [ ] Implementar `api/routes/datasets.py` → `GET /datasets`, `GET /datasets/{id}`
- [ ] Tratamento de erros: `InvalidZipError`, `NoCSVFoundError`, `NoDictionaryError`
- [ ] Testes: ZIP válido, sem CSV, sem dicionário, múltiplos CSVs

**Critério de conclusão:** upload de `202401_NFs.zip` funciona; tabelas aparecem no `GET /datasets`.

---

## Sprint 3 — Tools e Agente de Consulta
**Dias 8–13**

- [ ] Implementar `tools/schema_tool.py`
- [ ] Implementar `tools/sql_tool.py` (com bloqueio de DDL/DML)
- [ ] Implementar `tools/stats_tool.py`
- [ ] Implementar `agents/orchestrator.py` com PydanticAI
- [ ] Implementar `api/routes/query.py` → `POST /ask`
- [ ] Retry automático em SQL inválido (1 tentativa)
- [ ] Testes: perguntas simples, perguntas inválidas, dataset inexistente

**Critério de conclusão:** perguntas em linguagem natural retornam dados corretos via API.

---

## Sprint 4 — Visualizações
**Dias 14–16**

- [ ] Implementar `tools/chart_tool.py` (bar, line, pie, histogram)
- [ ] Integrar `chart_tool` no Orchestrator
- [ ] Lógica de decisão de formato (texto / tabela / gráfico)
- [ ] Testes: verificar tipo de gráfico para cada categoria de pergunta

**Critério de conclusão:** perguntas de série temporal retornam `chart_spec` Plotly válido.

---

## Sprint 5 — Frontend Streamlit
**Dias 17–20**

- [ ] Interface A — Upload: drag & drop de ZIP, preview das tabelas
- [ ] Interface B — Chat: input de pergunta, histórico de conversa
- [ ] Renderização de respostas em texto
- [ ] Renderização de tabelas (st.dataframe)
- [ ] Renderização de gráficos Plotly (st.plotly_chart)
- [ ] Seleção de dataset ativo

**Critério de conclusão:** usuário consegue fazer upload e realizar perguntas pelo navegador.

---

## Sprint 6 — Polimento e Entrega
**Dias 21–25**

- [ ] Testes end-to-end com `202401_NFs.zip` e `202505_NFe.zip`
- [ ] Validar as 4+ perguntas de demonstração
- [ ] Tratamento de erros no frontend (mensagens amigáveis)
- [ ] Logging completo com Loguru
- [ ] README com instruções de instalação e execução
- [ ] Relatório técnico em PDF
- [ ] ZIP do código-fonte para entrega
- [ ] (Opcional) publicar repositório no GitHub

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

- [ ] Sistema executa com `uvicorn` + `streamlit` sem erros
- [ ] Upload de ZIP funciona
- [ ] Agente responde perguntas com dados reais (não inventados)
- [ ] Respostas em texto, tabela e gráfico demonstradas
- [ ] Pelo menos 4 perguntas documentadas com respostas no relatório
- [ ] Framework PydanticAI utilizado e documentado
- [ ] `GOOGLE_API_KEY` em `.env` (nunca no código)
- [ ] Relatório técnico em PDF entregue
- [ ] Código-fonte em ZIP entregue
