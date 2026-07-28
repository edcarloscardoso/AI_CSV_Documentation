"""Agente Orchestrator de Consulta em linguagem natural utilizando PydanticAI."""

import os
from typing import Any

from loguru import logger
from pydantic_ai import Agent

from api.contracts import ChartSpec, QuestionResponse
from api.exceptions import DatasetNotFoundError, SQLExecutionError
from services.catalog_service import CatalogService
from services.deps import get_catalog_service, get_duckdb_service
from services.duckdb_service import DuckDBService
from tools.chart_tool import chart_tool
from tools.schema_tool import schema_tool
from tools.sql_tool import sql_tool
from tools.stats_tool import stats_tool

SYSTEM_PROMPT = """
Você é um analista de dados especialista. Sua função é responder perguntas sobre dados
carregados em um banco de dados, usando exclusivamente as ferramentas disponíveis.

REGRAS OBRIGATÓRIAS (nunca viole):
1. Sempre chame `schema_tool` antes de qualquer outra ação para entender a estrutura dos dados.
2. Nunca responda uma pergunta de dados sem chamar `sql_tool`. Você não inventa dados.
3. Se o resultado do SQL for vazio (0 linhas), informe o usuário claramente que não há dados.
4. Em caso de erro no SQL (ex: tipo de dado incompatível), tente corrigir e executar novamente uma única vez.
5. Sempre inclua o SQL utilizado na resposta (campo sql_used).
6. Responda sempre no mesmo idioma da pergunta do usuário.
7. CONVERSÃO DE TIPOS EM COLUNAS VARCHAR (IMPORTANTE):
   - Se uma coluna contendo valores numéricos ou monetários estiver como `VARCHAR` ou `TEXT` no DuckDB (ex: '1234.56' ou '1.234,56'), você NUNCA deve aplicar `SUM(coluna)` diretamente.
   - Use SEMPRE conversão de tipo explícita com tratamento de formatação brasileira: `TRY_CAST(REPLACE(REPLACE(CAST(coluna AS VARCHAR), '.', ''), ',', '.') AS DOUBLE)` ou `TRY_CAST(coluna AS DOUBLE)` antes de funções de agregação como `SUM()`, `AVG()`, `MIN()`, `MAX()`.

FORMATO DA RESPOSTA:
- 1 valor único -> texto explicativo (answer_type="text")
- 2 a 20 linhas -> tabela (answer_type="table")
- Série temporal ou comparação entre categorias -> gráfico (answer_type="chart")
- Mais de 20 linhas -> gráfico + tabela resumida (top 10) (answer_type="mixed")
"""


class OrchestratorAgent:
    """Gerencia a execução da consulta via PydanticAI Agent e ferramentas."""

    def __init__(
        self,
        catalog_service: CatalogService | None = None,
        duckdb_service: DuckDBService | None = None,
        model_name: str | None = None,
    ):
        self.catalog_service = catalog_service or get_catalog_service()
        self.duckdb_service = duckdb_service or get_duckdb_service()
        self.model_name = (
            model_name
            or os.getenv("GEMINI_MODEL")
            or os.getenv("LLM_MODEL", "google:gemini-2.0-flash")
        )
        if self.model_name and not self.model_name.startswith(
            ("google:", "google-gla:", "google-vertex:", "openai:", "anthropic:")
        ):
            self.model_name = f"google:{self.model_name}"

    async def run_async(self, question: str, dataset_id: str) -> QuestionResponse:
        """Processa a pergunta do usuário de forma assíncrona (compatível com FastAPI)."""
        try:
            dataset_meta = self.catalog_service.get_dataset(dataset_id)
        except Exception:
            raise DatasetNotFoundError(f"Dataset com ID '{dataset_id}' não encontrado.")

        if not dataset_meta:
            raise DatasetNotFoundError(f"Dataset com ID '{dataset_id}' não encontrado.")

        schema_info = schema_tool(
            dataset_id=dataset_id,
            catalog_service=self.catalog_service,
            duckdb_service=self.duckdb_service,
        )

        tables = schema_info.get("tables", [])
        if not tables:
            return QuestionResponse(
                answer_text="O dataset não possui tabelas válidas para consulta.",
                answer_type="text",
                table_data=[],
                chart_spec=None,
                sql_used=None,
            )

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        if api_key:
            try:
                response = await self._run_pydantic_ai_async(question, dataset_id, schema_info)
                # Se a resposta LLM contiver dados de tabela e não tiver gráfico, gera automaticamente o chart_spec
                if response.table_data and len(response.table_data) >= 2 and not response.chart_spec:
                    chart_res = chart_tool(response.table_data, question)
                    if chart_res:
                        response.chart_spec = ChartSpec(
                            chart_type=chart_res["chart_type"],
                            plotly_spec=chart_res["plotly_spec"],
                        )
                        if response.answer_type == "table":
                            response.answer_type = "chart"
                return response
            except Exception as e:
                logger.warning(f"Execução PydanticAI falhou ({e}), executando fluxo de fallback.")

        return self._run_fallback_query(question, dataset_id, tables)

    async def _run_pydantic_ai_async(
        self, question: str, dataset_id: str, schema_info: dict[str, Any]
    ) -> QuestionResponse:
        agent = Agent(
            self.model_name,
            output_type=QuestionResponse,
            system_prompt=SYSTEM_PROMPT,
        )

        @agent.tool_plain
        def schema_tool_caller() -> dict[str, Any]:
            return schema_info

        @agent.tool_plain
        def run_sql(query: str) -> dict[str, Any]:
            try:
                return sql_tool(query, dataset_id, self.duckdb_service)
            except Exception as e:
                return {"error": f"Falha na execução do SQL: {e!s}. Tente aplicar TRY_CAST(REPLACE(coluna, ',', '.') AS DOUBLE) para colunas de texto."}

        @agent.tool_plain
        def get_stats(table: str, column: str) -> dict[str, Any]:
            return stats_tool(table, column, dataset_id, self.duckdb_service)

        user_prompt = f"Dataset ID: {dataset_id}\nPergunta: {question}"
        result = await agent.run(user_prompt)
        return result.data

    def run(self, question: str, dataset_id: str) -> QuestionResponse:
        """Processa a pergunta do usuário de forma síncrona (para scripts CLI/testes)."""
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            schema_info = schema_tool(
                dataset_id=dataset_id,
                catalog_service=self.catalog_service,
                duckdb_service=self.duckdb_service,
            )
            tables = schema_info.get("tables", [])
            return self._run_fallback_query(question, dataset_id, tables)

        return asyncio.run(self.run_async(question, dataset_id))

    def _run_fallback_query(
        self, question: str, dataset_id: str, tables: list[dict[str, Any]]
    ) -> QuestionResponse:
        """Fluxo determinístico seguro de consulta SQL baseada em intenção quando o LLM não está disponível."""
        q_lower = question.lower()

        def find_col(keywords: list[str], prefer_types: list[str] | None = None) -> tuple[str, str] | None:
            best_match = None
            for tbl in tables:
                tbl_name = tbl["name"]
                for col in tbl.get("columns", []):
                    c_name = col["name"]
                    c_type = (col.get("type") or "").upper()
                    c_desc = (col.get("description") or "").lower()
                    c_comb = f"{c_name} {c_desc}".lower()
                    if any(kw in c_comb for kw in keywords):
                        match = (tbl_name, c_name)
                        if prefer_types and any(pt in c_type for pt in prefer_types):
                            return match
                        if not prefer_types and c_type in ["VARCHAR", "TEXT", "STRING"]:
                            return match
                        if best_match is None:
                            best_match = match
            return best_match

        supplier_match = find_col(["fornecedor", "emitente", "razao", "razão", "nome_emitente"])
        product_match = find_col(["descrição", "descricao", "produto", "item"])
        category_match = find_col(["categoria", "ncm", "tipo_produto", "natureza"])
        date_match = find_col(
            ["data", "emissao", "emissão", "dt_", "mes", "mês"],
            prefer_types=["TIMESTAMP", "DATE", "DATETIME", "VARCHAR", "TEXT"],
        )
        val_match = find_col(
            ["valor", "total", "gasto", "preco", "preço"],
            prefer_types=["DOUBLE", "FLOAT", "BIGINT", "INTEGER", "DECIMAL", "NUMERIC", "VARCHAR", "TEXT"],
        )
        qty_match = find_col(
            ["quantidade", "volume", "qtd"],
            prefer_types=["DOUBLE", "FLOAT", "BIGINT", "INTEGER", "DECIMAL", "NUMERIC", "VARCHAR", "TEXT"],
        )

        query = None
        answer_text = ""
        answer_type = "text"
        chart_spec_obj = None

        # Função auxiliar para gerar expressão de soma segura com cast
        def safe_sum(col: str) -> str:
            return f"ROUND(SUM(COALESCE(TRY_CAST(\"{col}\" AS DOUBLE), TRY_CAST(REPLACE(REPLACE(CAST(\"{col}\" AS VARCHAR), '.', ''), ',', '.') AS DOUBLE), 0)), 2)"

        # Intenção 1: Fornecedores (maior valor ou top 5)
        if ("fornecedor" in q_lower or "emitente" in q_lower) and supplier_match and val_match:
            tbl_s, col_s = supplier_match
            _, col_v = val_match
            sum_expr = safe_sum(col_v)
            if any(w in q_lower for w in ["cinco", "5", "maiores", "principais"]):
                query = f'SELECT "{col_s}" AS fornecedor, {sum_expr} AS total_valor FROM {tbl_s} GROUP BY "{col_s}" ORDER BY total_valor DESC LIMIT 5'
                answer_type = "table"
            else:
                query = f'SELECT "{col_s}" AS fornecedor, {sum_expr} AS total_valor FROM {tbl_s} GROUP BY "{col_s}" ORDER BY total_valor DESC LIMIT 1'
                answer_type = "text"

        # Intenção 2: Produtos (maior volume / maior quantidade)
        elif ("produto" in q_lower or "item" in q_lower) and product_match and (qty_match or val_match):
            tbl_p, col_p = product_match
            col_q = qty_match[1] if qty_match else val_match[1]
            sum_expr = safe_sum(col_q)
            query = f'SELECT "{col_p}" AS produto, {sum_expr} AS total_volume FROM {tbl_p} GROUP BY "{col_p}" ORDER BY total_volume DESC LIMIT 1'
            answer_type = "text"

        # Intenção 3: Total gasto por mês
        elif ("mês" in q_lower or "mes" in q_lower or "mensal" in q_lower) and date_match and val_match:
            tbl_d, col_d = date_match
            _, col_v = val_match
            sum_expr = safe_sum(col_v)
            query = f'SELECT strftime(\'%Y-%m\', TRY_CAST("{col_d}" AS TIMESTAMP)) AS mes, {sum_expr} AS total_gasto FROM {tbl_d} WHERE "{col_d}" IS NOT NULL GROUP BY mes ORDER BY mes'
            answer_type = "chart"

        # Intenção 4: Categoria (maior crescimento / maior volume de compras)
        elif ("categoria" in q_lower or "tipo" in q_lower or "ncm" in q_lower) and (
            category_match or product_match
        ) and val_match:
            cat_target = category_match or product_match
            tbl_c, col_c = cat_target
            _, col_v = val_match
            sum_expr = safe_sum(col_v)
            query = f'SELECT "{col_c}" AS categoria, {sum_expr} AS total FROM {tbl_c} GROUP BY "{col_c}" ORDER BY total DESC LIMIT 5'
            answer_type = "table"

        # Fallback genérico se nenhuma intenção específica for identificada
        if not query:
            main_table = tables[0]["name"]
            query = f"SELECT * FROM {main_table} LIMIT 10"

        sql_result = sql_tool(query, dataset_id, self.duckdb_service)
        rows = sql_result["rows"]
        row_count = sql_result["row_count"]

        if row_count == 0:
            return QuestionResponse(
                answer_text="Não foram encontrados dados para essa consulta.",
                answer_type="text",
                table_data=[],
                chart_spec=None,
                sql_used=query,
            )

        # Gera gráfico Plotly se houver dados estruturados suficientes e for apropriado
        if row_count >= 1 and (answer_type in ["chart", "mixed", "table"] or "gráfico" in q_lower or "grafico" in q_lower):
            chart_res = chart_tool(rows, question)
            if chart_res:
                chart_spec_obj = ChartSpec(
                    chart_type=chart_res["chart_type"],
                    plotly_spec=chart_res["plotly_spec"],
                )
                if answer_type != "text" and row_count >= 2:
                    answer_type = "chart"

        if row_count == 1 and answer_type == "text":
            row = rows[0]
            col_keys = list(row.keys())
            if len(col_keys) == 2:
                answer_text = (
                    f"O resultado para '{question}' é {col_keys[0]}: '{row[col_keys[0]]}' com {col_keys[1]}: {row[col_keys[1]]}."
                )
            else:
                answer_text = f"Resultado da consulta: {row}"
        else:
            answer_text = f"Consulta realizada com sucesso. Foram encontrados {row_count} registros."

        return QuestionResponse(
            answer_text=answer_text,
            answer_type=answer_type,
            table_data=rows,
            chart_spec=chart_spec_obj,
            sql_used=query,
        )
