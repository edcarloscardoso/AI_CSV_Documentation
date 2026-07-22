# Orchestrator — Fluxo de Decisão

## Papel

O Orchestrator é o cérebro da aplicação. Ele recebe a pergunta do usuário e coordena as Tools para produzir uma resposta factual baseada nos dados reais — sem inventar informações.

---

## Fluxo de Execução

```
Pergunta do Usuário
        │
        ▼
1. schema_tool(dataset_id)
   → obtém: tabelas, colunas, tipos, descrições do dicionário, amostras
        │
        ▼
2. LLM gera SQL
   → usa o contexto do schema para montar a query correta
        │
        ▼
3. sql_tool(query, dataset_id)
   → executa no DuckDB → retorna DataFrame como JSON
        │
        ▼
4. Validação do resultado
   → resultado vazio? → responde "Não foram encontrados dados"
   → erro de SQL?    → tenta corrigir (1 retry) → falha → erro explícito
        │
        ▼
5. Decisão de formato
   → texto / tabela / gráfico (ver regra em AGENTS.md)
        │
        ▼
6. [Se gráfico] chart_tool(data, question)
   → retorna spec Plotly JSON
        │
        ▼
7. Monta QuestionResponse
   → answer_text + table_data + chart_spec + sql_used
```

---

## Regras Invioláveis do Orchestrator

1. **`schema_tool` é sempre a primeira chamada.** Nunca gerar SQL sem conhecer o schema.
2. **Nunca inventar dados.** Se o SQL retornar vazio, informar o usuário.
3. **SQL deve ser executado via `sql_tool`.** O LLM não acessa DuckDB diretamente.
4. **1 retry em caso de SQL inválido.** Se falhar novamente, retornar erro com mensagem clara.
5. **`sql_used` sempre incluso na resposta** para fins de transparência e debug.
6. **Responder no idioma do usuário** (detectado automaticamente na pergunta).

---

## Prompt de Sistema

Ver `05-prompts/SYSTEM_PROMPTS.md` para o prompt completo.

---

## Contexto Passado ao LLM

```python
context = {
    "dataset_id": "abc123",
    "tables": [
        {
            "name": "notas_fiscais",
            "columns": [
                {"name": "fornecedor", "type": "VARCHAR", "description": "Nome do fornecedor"},
                {"name": "valor",      "type": "DOUBLE",  "description": "Valor da nota em R$"},
                {"name": "data_emissao","type": "DATE",   "description": "Data de emissão"},
            ],
            "sample": [["Empresa A", 1500.00, "2024-01-15"], ...]
        }
    ]
}
```
