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

Consulte `07-roadmap/IMPLEMENTATION_PLAN.md` para o plano de execução em sprints.