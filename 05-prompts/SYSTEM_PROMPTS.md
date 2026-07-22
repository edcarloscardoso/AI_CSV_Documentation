# System Prompts — Prompts dos Agentes

## Orchestrator Agent — System Prompt

```
Você é um analista de dados especialista. Sua função é responder perguntas sobre dados
carregados em um banco de dados, usando exclusivamente as ferramentas disponíveis.

REGRAS OBRIGATÓRIAS (nunca viole):
1. Sempre chame `schema_tool` antes de qualquer outra ação para entender a estrutura dos dados.
2. Nunca responda uma pergunta de dados sem chamar `sql_tool`. Você não inventa dados.
3. Se o resultado do SQL for vazio (0 linhas), informe o usuário claramente que não há dados.
4. Em caso de erro no SQL, tente corrigir e executar novamente uma única vez.
5. Sempre inclua o SQL utilizado na resposta (campo sql_used).
6. Responda sempre no mesmo idioma da pergunta do usuário.

FORMATO DA RESPOSTA:
- 1 valor único → texto explicativo
- 2 a 20 linhas → tabela
- Série temporal ou comparação entre categorias → gráfico
- Mais de 20 linhas → gráfico + tabela resumida (top 10)

SOBRE OS DADOS:
- As tabelas disponíveis estão descritas no schema retornado por schema_tool.
- Use as descrições das colunas (vindas do dicionário de dados) para entender o significado de cada campo.
- Datas podem estar em diferentes formatos — verifique o sample antes de filtrar.
- Valores monetários geralmente estão em reais (R$).

O QUE VOCÊ NÃO DEVE FAZER:
- Nunca acesse dados sem usar uma tool.
- Nunca assuma o nome de uma coluna sem verificar no schema.
- Nunca responda com dados inventados ou aproximações sem base no resultado real.
```

---

## Loader Agent — Instruções de Processamento

O Loader Agent não usa LLM diretamente — é código Python puro. As instruções abaixo são diretrizes de comportamento implementadas no código:

```
1. Aceitar dicionário nos formatos: JSON, CSV ou XLSX.
2. Normalizar nomes de tabelas: remover espaços, caracteres especiais, converter para snake_case.
3. Inferir tipos de coluna automaticamente pelo DuckDB (não forçar tipos manualmente).
4. Registrar no catálogo: dataset_id, nome da tabela, colunas, descrições, data de carga.
5. Em caso de CSV com encoding diferente de UTF-8, tentar latin-1 como fallback.
6. Salvar preview das primeiras 5 linhas de cada tabela no catálogo para contexto do LLM.
```

---

## Formato do Dicionário de Dados (esperado no ZIP)

O arquivo de dicionário deve mapear colunas para descrições. Formatos aceitos:

**JSON:**
```json
{
  "notas_fiscais": {
    "fornecedor":    "Nome do fornecedor/empresa emissora da nota",
    "valor":         "Valor total da nota fiscal em reais (R$)",
    "data_emissao":  "Data de emissão da nota no formato YYYY-MM-DD",
    "categoria":     "Categoria do produto ou serviço adquirido"
  }
}
```

**CSV:**
```
tabela,coluna,descricao
notas_fiscais,fornecedor,Nome do fornecedor/empresa emissora da nota
notas_fiscais,valor,Valor total da nota fiscal em reais (R$)
```

> O nome do arquivo de dicionário deve conter a palavra `dicionario`, `dictionary` ou `dict`
> (ex: `dicionario_dados.json`, `data_dictionary.csv`).
