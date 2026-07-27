"""Tool chart_tool: gera especificações de gráfico Plotly a partir de dados estruturados."""

import decimal
import re
from typing import Any

from loguru import logger


def chart_tool(
    data: list[dict[str, Any]],
    question: str = "",
    force_type: str | None = None,
) -> dict[str, Any] | None:
    """Analisar os dados e gerar uma especificação de gráfico Plotly."""
    if not data or len(data) < 1:
        logger.debug("Dados insuficientes para gerar gráfico (mínimo de 1 linha necessária).")
        return None

    columns = list(data[0].keys())
    if len(columns) < 2:
        logger.debug("Número insuficiente de colunas para gráfico (mínimo de 2 colunas necessárias).")
        return None

    q_lower = question.lower()

    # Identifica colunas por tipo
    first_row = data[0]
    cat_col = None
    date_col = None
    num_col = None

    for col in columns:
        val = first_row.get(col)
        col_lower = str(col).lower()

        # Verifica datas/mês/período
        if any(kw in col_lower for kw in ["mes", "mês", "data", "dt_", "ano", "periodo", "período"]):
            date_col = date_col or col

        # Verifica se o valor é numérico (int, float, Decimal)
        elif isinstance(val, (int, float, decimal.Decimal)) and not isinstance(val, bool):
            num_col = num_col or col

        # Verifica se é texto/categoria
        elif isinstance(val, str):
            cat_col = cat_col or col

    # Fallback se não detectou explicitamente
    if not num_col:
        for col in columns:
            v = first_row.get(col)
            if isinstance(v, (int, float, decimal.Decimal)) and not isinstance(v, bool):
                num_col = col
                break

    if not cat_col and not date_col:
        for col in columns:
            if col != num_col:
                cat_col = col
                break

    if not num_col or (not cat_col and not date_col):
        return None

    x_col = date_col or cat_col
    y_col = num_col

    # Determina o tipo de gráfico
    chart_type = force_type

    if not chart_type:
        if "pizza" in q_lower or "pie" in q_lower or "proporção" in q_lower or "distribuição" in q_lower:
            chart_type = "pie"
        elif date_col or "evolução" in q_lower or "linha" in q_lower or "tendência" in q_lower or "histórico" in q_lower:
            chart_type = "line"
        elif len(data) <= 6 and not date_col and "pizza" in q_lower:
            chart_type = "pie"
        else:
            chart_type = "bar"

    x_vals = [str(row.get(x_col, "")) for row in data]
    y_vals = [float(row.get(y_col, 0)) if isinstance(row.get(y_col), (int, float, decimal.Decimal)) else 0.0 for row in data]

    # Constrói o plotly_spec
    if chart_type == "pie":
        plotly_spec = {
            "data": [
                {
                    "labels": x_vals,
                    "values": y_vals,
                    "type": "pie",
                    "hoverinfo": "label+percent+value",
                    "textinfo": "percent+label",
                }
            ],
            "layout": {
                "title": f"Distribuição de {y_col} por {x_col}",
                "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
            },
        }
    elif chart_type == "line":
        plotly_spec = {
            "data": [
                {
                    "x": x_vals,
                    "y": y_vals,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": y_col,
                    "marker": {"size": 8},
                    "line": {"width": 3},
                }
            ],
            "layout": {
                "title": f"Evolução de {y_col} por {x_col}",
                "xaxis": {"title": str(x_col)},
                "yaxis": {"title": str(y_col)},
                "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
            },
        }
    else:  # bar (default)
        chart_type = "bar"
        plotly_spec = {
            "data": [
                {
                    "x": x_vals,
                    "y": y_vals,
                    "type": "bar",
                    "name": y_col,
                }
            ],
            "layout": {
                "title": f"{y_col} por {x_col}",
                "xaxis": {"title": str(x_col)},
                "yaxis": {"title": str(y_col)},
                "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
            },
        }

    logger.info(f"chart_tool gerou gráfico do tipo '{chart_type}' para {len(data)} linhas.")

    return {
        "chart_type": chart_type,
        "plotly_spec": plotly_spec,
    }
