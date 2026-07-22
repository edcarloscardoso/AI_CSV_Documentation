# PRD — Product Requirements Document
## Interface Inteligente para Consulta de CSV

**Versão:** 1.0  
**Data:** 2026-07-22  
**Projeto:** I2A2 · Desafio 4  

---

## Objetivo

Desenvolver uma plataforma de consulta inteligente que permita a qualquer usuário — sem conhecimento técnico — interrogar arquivos CSV em linguagem natural e obter respostas em texto, tabela ou gráfico.

---

## Usuário-Alvo

Profissionais de negócio que precisam extrair informações de planilhas sem saber SQL ou ferramentas de análise de dados.

---

## Casos de Uso

| ID | Caso de Uso | Prioridade |
|----|-------------|------------|
| UC-01 | Usuário faz upload de um arquivo ZIP com CSVs + dicionário | Alta |
| UC-02 | Sistema processa e carrega dados no banco | Alta |
| UC-03 | Usuário realiza pergunta em linguagem natural | Alta |
| UC-04 | Sistema responde com texto explicativo | Alta |
| UC-05 | Sistema responde com tabela de dados | Alta |
| UC-06 | Sistema responde com gráfico interativo | Média |
| UC-07 | Usuário visualiza datasets carregados | Média |
| UC-08 | Usuário faz múltiplas perguntas em sequência (chat) | Média |

---

## Requisitos Funcionais

### RF-01 — Upload de Dados
- O sistema deve aceitar arquivos `.zip` contendo:
  - Um ou mais arquivos `.csv`
  - Um arquivo de dicionário de dados (JSON, CSV ou XLSX)
- O sistema deve validar o conteúdo do ZIP antes de processar
- O sistema deve informar ao usuário quais tabelas foram carregadas, com preview de 5 linhas

### RF-02 — Processamento de Dados
- Os CSVs devem ser carregados em tabelas DuckDB nomeadas pelo nome do arquivo
- O dicionário de dados deve ser lido e usado para enriquecer o contexto do agente
- Inferência automática de tipos de colunas

### RF-03 — Interface de Consulta
- Usuário digita pergunta em linguagem natural
- Agente interpreta a solicitação e consulta os dados via SQL
- Resposta apresentada em formato adequado (texto, tabela ou gráfico)

### RF-04 — Formatos de Resposta
- **Texto:** quando a resposta é um valor único ou frase explicativa
- **Tabela:** quando a resposta envolve múltiplas linhas de dados
- **Gráfico:** quando a resposta é uma série temporal, comparação ou distribuição
- O agente decide automaticamente o melhor formato

---

## Requisitos Não-Funcionais

| Requisito | Critério |
|-----------|----------|
| Desempenho | Resposta em menos de 15 segundos para datasets até 100MB |
| Segurança | Chaves de API nunca expostas no código; isolamento por sessão |
| Usabilidade | Interface intuitiva, sem necessidade de treinamento |
| Confiabilidade | SQL sempre validado antes de executar; erros tratados com mensagem clara |

---

## Perguntas de Exemplo (Dataset NFs)

- "Qual fornecedor recebeu o maior valor no período?"
- "Qual produto apresentou o maior volume comprado?"
- "Qual foi o total gasto em cada mês?"
- "Quais foram os cinco maiores fornecedores?"
- "Qual categoria apresentou maior crescimento nas compras?"

---

## Fora de Escopo (MVP)

- Autenticação de usuários
- Multi-tenant com isolamento de dados
- Deploy em nuvem (apenas local para o MVP)
- Suporte a formatos além de ZIP/CSV
