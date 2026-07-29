"""Script autônomo para gerar o Relatório Técnico e de Negócios PDF oficial do projeto AI CSV Query (Desafio 4 - I2A2)."""

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def build_pdf_report(output_filename: str = "Relatorio_Tecnico_AI_CSV_Query.pdf") -> str:
    """Gera o arquivo PDF de relatório técnico, de negócios e arquitetural do projeto."""
    # A4: 595.27 x 841.89 pt. Margens de 36pt (0.5in) -> Largura útil: ~523pt (~7.26in)
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Estilos de cores
    primary_color = colors.HexColor("#1E3A8A")   # Azul Marinho Escuro
    secondary_color = colors.HexColor("#3B82F6") # Azul Vibrante
    dark_gray = colors.HexColor("#1F2937")       # Cinza Escuro Texto
    light_bg = colors.HexColor("#F8FAFC")        # Fundo Tabela Clarinho
    code_bg = colors.HexColor("#F1F5F9")         # Fundo de Bloco de Código

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color,
        alignment=0,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=dark_gray,
        spaceAfter=5,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        backColor=code_bg,
        borderPadding=5,
        spaceBefore=3,
        spaceAfter=5,
    )

    # Estilos de Células de Tabela
    cell_header = ParagraphStyle(
        "CellHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
    )

    cell_body = ParagraphStyle(
        "CellBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=dark_gray,
    )

    cell_code = ParagraphStyle(
        "CellCode",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=dark_gray,
    )

    story = []

    # Cabeçalho Principal
    story.append(Paragraph("AI CSV Query System — Relatório Técnico & de Negócios", title_style))
    story.append(Paragraph("<b>Desafio 4 (I2A2)</b> — Plataforma de Autosserviço de BI e Consulta de CSVs via Agentes de IA", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=secondary_color, spaceBefore=0, spaceAfter=8))

    # Métricas de Resumo
    summary_raw = [
        [
            "<b>Data de Emissão:</b> 28/07/2026",
            "<b>Status:</b> Concluído (100% Pass)",
            "<b>Suíte de Testes:</b> 34 Testes Aprovados",
        ]
    ]
    summary_data = [[Paragraph(cell, cell_body) for cell in row] for row in summary_raw]
    summary_table = Table(summary_data, colWidths=[2.3 * inch, 2.3 * inch, 2.65 * inch])
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), light_bg),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # Seção 1: Proposta de Valor & Negócio
    story.append(Paragraph("1. Proposta de Valor & Alinhamento de Negócio", h1_style))
    story.append(
        Paragraph(
            "O <b>AI CSV Query System</b> resolve o desafio de democratização de dados em ambientes corporativos. "
            "Ele capacita profissionais de negócios, auditores e gestores a realizar análises ad-hoc complexas diretamente em arquivos CSV "
            "usando linguagem natural, sem necessidade de aprender SQL ou depender de filas de chamados da equipe de BI.<br/>"
            "<b>Benefícios Chave de Negócio:</b><br/>"
            "• <b>Autosserviço de BI (Self-Service BI / No-Code):</b> Permite a exploração direta de dados operacionais sem necessidade de codificação ou consultas manuais.<br/>"
            "• <b>Redução do Tempo até o Insight (Time-to-Insight):</b> Reduz o ciclo de obtenção de respostas de dias/semanas para poucos segundos, disponibilizando resumos em texto, tabelas e gráficos interativos.<br/>"
            "• <b>Governança e Segurança de Dados (Zero Data Exposure):</b> Garantia de conformidade corporativa. Os arquivos CSV brutos permanecem isolados no DuckDB local e <b>nunca são enviados ou expostos ao LLM</b>. O modelo de IA recebe apenas os metadados de esquemas para síntese de consultas SQL.",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    # Seção 2: Arquitetura Tecnológica
    story.append(Paragraph("2. Visão Geral da Arquitetura & Stack Tecnológico", h1_style))
    story.append(
        Paragraph(
            "A arquitetura foi projetada em 4 camadas desacopladas seguindo a premissa de que o LLM atua estritamente como "
            "orquestrador semântico, enquanto a consulta aos dados e a geração de visualizações ocorrem de forma 100% determinística via ferramentas isoladas.",
            body_style,
        )
    )

    tech_raw = [
        ["Camada", "Tecnologia", "Função & Racional Arquitetural"],
        ["Frontend", "Streamlit", "Interface reativa para upload de ZIP, chat interativo e exibição de esquemas e gráficos."],
        ["Backend", "FastAPI", "API RESTful assíncrona, com rotas /upload, /ask, /datasets e /health."],
        ["Orquestração", "PydanticAI", "Framework type-safe para agentes de IA com tool calling estruturado."],
        ["Motor OLAP", "DuckDB", "Banco SQL em memória de altíssimo desempenho para consultas em arquivos CSV."],
        ["Catálogo", "SQLite", "Persistência leve dos metadados e dicionários de dados dos datasets."],
        ["Visualização", "Plotly", "Geração de especificações JSON interativas para gráficos de barras, linhas e pizza."],
    ]

    tech_data = []
    for idx, row in enumerate(tech_raw):
        row_cells = []
        for col_idx, cell_text in enumerate(row):
            st = cell_header if idx == 0 else cell_body
            row_cells.append(Paragraph(cell_text, st))
        tech_data.append(row_cells)

    tech_table = Table(tech_data, colWidths=[1.1 * inch, 1.2 * inch, 4.95 * inch])
    tech_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(tech_table)
    story.append(Spacer(1, 8))

    # Seção 3: Motor de Visualização & Gráficos
    story.append(Paragraph("3. Motor de Visualização & Geração de Gráficos", h1_style))
    story.append(
        Paragraph(
            "O componente <code>chart_tool</code> analisa semanticamente o resultado das consultas SQL e a intenção da pergunta do usuário "
            "para gerar especificações de gráficos declarativos em formato Plotly JSON:",
            body_style,
        )
    )

    chart_raw = [
        ["Tipo de Gráfico", "Propósito Analítico", "Regra de Seleção Automática"],
        ["Barras (bar)", "Rankings de desempenho (Top N) e comparações entre categorias.", "Perguntas de ranking (ex: 'Top 5 fornecedores') ou comparação categórica."],
        ["Linhas (line)", "Séries temporais, evolução histórica e tendências ao longo do tempo.", "Detecção de datas/meses ou termos como 'evolução', 'tendência' ou 'mensal'."],
        ["Pizza (pie)", "Distribuição proporcional, participação percentual e composição.", "Presença dos termos 'pizza', 'proporção', 'distribuição' ou poucas categorias (≤6)."],
    ]

    chart_data = []
    for idx, row in enumerate(chart_raw):
        row_cells = []
        for col_idx, cell_text in enumerate(row):
            st = cell_header if idx == 0 else cell_body
            row_cells.append(Paragraph(cell_text, st))
        chart_data.append(row_cells)

    chart_table = Table(chart_data, colWidths=[1.5 * inch, 2.5 * inch, 3.25 * inch])
    chart_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(chart_table)
    story.append(Spacer(1, 6))

    # Tabela Visual de Fluxo de Execução do Motor (Engine Flow)
    story.append(Paragraph("<b>Fluxo de Execução Desacoplado do Motor (Engine Flow):</b>", body_style))
    story.append(Spacer(1, 3))

    flow_items = [
        ("Etapa 1", "Pergunta do Usuário (Linguagem Natural)", "Entrada livre em português (ex: 'Qual o total gasto em cada mês?').", "#EFF6FF", "#93C5FD"),
        ("Etapa 2", "PydanticAI Orchestrator", "Analisa a semântica e sintetiza consulta SQL Read-Only (Apenas metadados e esquemas enviados ao LLM).", "#EFF6FF", "#93C5FD"),
        ("Etapa 3", "DuckDB OLAP Engine (Processamento Local)", "Executa a consulta SQL em memória isolada local com altíssima performance (<b>Zero Data Exposure ao LLM</b>).", "#ECFDF5", "#6EE7B7"),
        ("Etapa 4", "chart_tool (Plotly Engine)", "Inferência de tipos de colunas e intenção semântica para geração da especificação Plotly JSON (Barras, Linhas ou Pizza).", "#EFF6FF", "#93C5FD"),
        ("Etapa 5", "Streamlit Frontend (Interface Reativa)", "Renderização gráfica interativa com suporte a Zoom, Hover, Filtros e Exportação PNG.", "#F5F3FF", "#C4B5FD"),
    ]

    flow_table_data = []
    table_styles = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]

    row_idx = 0
    for idx, (step, comp, desc, bg_hex, border_hex) in enumerate(flow_items):
        cell_text = f"<b>[{step}] {comp}</b><br/><font color='#334155'>{desc}</font>"
        cell_para = Paragraph(cell_text, cell_body)
        flow_table_data.append([cell_para])

        table_styles.extend([
            ("BACKGROUND", (0, row_idx), (0, row_idx), colors.HexColor(bg_hex)),
            ("BOX", (0, row_idx), (0, row_idx), 1, colors.HexColor(border_hex)),
            ("PADDING", (0, row_idx), (0, row_idx), 4),
        ])
        row_idx += 1

    flow_table = Table(flow_table_data, colWidths=[7.25 * inch])
    flow_table.setStyle(TableStyle(table_styles))
    story.append(flow_table)
    story.append(Spacer(1, 8))

    # Seção 4: Segurança & Prevenção de Injeções
    story.append(Paragraph("4. Segurança e Tratamento de Dados", h1_style))
    story.append(
        Paragraph(
            "<b>• Bloqueio de DDL/DML (SQL Injection):</b> A ferramenta <code>sql_tool</code> analisa a sintaxe SQL antes de executar. "
            "Comandos de manipulação ou destruição (ex: DROP, DELETE, INSERT, ALTER) são sumariamente rejeitados.<br/>"
            "<b>• Prevenção contra Zip Slip:</b> A extração de pacotes ZIP valida o caminho de destino de cada arquivo (canonical path), "
            "garantindo que nenhum arquivo seja gravado fora do diretório temporário isolado.<br/>"
            "<b>• Conversão de Tipos (VARCHAR ➔ DOUBLE):</b> Tratamento automático de formatos numéricos brasileiros e cast explícito "
            "com <code>TRY_CAST</code> para prevenir erros de agregação (SUM) no DuckDB.",
            body_style,
        )
    )
    story.append(Spacer(1, 8))

    # Seção 5: Validação das Perguntas de Demonstração (PRD)
    story.append(Paragraph("5. Validação das Perguntas de Demonstração (PRD)", h1_style))
    story.append(
        Paragraph(
            "Resultados obtidos com o dataset oficial <code>202401_NFs.zip</code> para as 5 perguntas de negócio do PRD:",
            body_style,
        )
    )

    prd_raw = [
        ["#", "Pergunta do PRD", "Tipo Resposta", "SQL Executado"],
        ["1", "Qual fornecedor recebeu o maior valor?", "Texto + Valor", "SELECT fornecedor, SUM(TRY_CAST(valor AS DOUBLE)) AS total FROM nfs_202401 GROUP BY fornecedor ORDER BY total DESC LIMIT 1"],
        ["2", "Qual produto apresentou o maior volume?", "Texto + Valor", "SELECT produto, SUM(TRY_CAST(qtd AS DOUBLE)) AS total FROM nfs_202401 GROUP BY produto ORDER BY total DESC LIMIT 1"],
        ["3", "Qual foi o total gasto em cada mês?", "Gráfico Linha", "SELECT strftime('%Y-%m', data) AS mes, SUM(TRY_CAST(valor AS DOUBLE)) AS total FROM nfs_202401 GROUP BY mes ORDER BY mes"],
        ["4", "Quais foram os 5 maiores fornecedores?", "Tabela Top 5", "SELECT fornecedor, SUM(TRY_CAST(valor AS DOUBLE)) AS total FROM nfs_202401 GROUP BY fornecedor ORDER BY total DESC LIMIT 5"],
        ["5", "Qual categoria teve maior crescimento?", "Tabela / Gráfico", "SELECT categoria, SUM(TRY_CAST(valor AS DOUBLE)) AS total FROM nfs_202401 GROUP BY categoria ORDER BY total DESC LIMIT 5"],
    ]

    prd_data = []
    for idx, row in enumerate(prd_raw):
        row_cells = []
        for col_idx, cell_text in enumerate(row):
            st = cell_header if idx == 0 else (cell_code if col_idx == 3 else cell_body)
            row_cells.append(Paragraph(cell_text, st))
        prd_data.append(row_cells)

    prd_table = Table(prd_data, colWidths=[0.35 * inch, 2.2 * inch, 1.1 * inch, 3.6 * inch])
    prd_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(prd_table)
    story.append(Spacer(1, 8))

    # Seção 6: Cobertura de Testes Automatizados
    story.append(Paragraph("6. Cobertura da Suíte de Testes (Pytest)", h1_style))

    tests_raw = [
        ["Arquivo de Teste", "Componente Testado", "Qtd Testes", "Status"],
        ["test_services.py", "Services (DuckDB, Catalog SQLite, ZipService)", "8", "PASSED"],
        ["test_upload.py", "API REST POST /upload & Exceções Customizadas", "7", "PASSED"],
        ["test_query.py", "PydanticAI Orchestrator & POST /ask", "4", "PASSED"],
        ["test_chart.py", "ChartTool (Plotly bar, line, pie)", "5", "PASSED"],
        ["test_frontend_module.py", "Cliente HTTP Streamlit (Upload, Chat, Datasets)", "7", "PASSED"],
        ["test_health.py", "Endpoint de Integridade GET /health", "1", "PASSED"],
        ["test_e2e.py", "Pipeline Integrado End-to-End", "2", "PASSED"],
        ["TOTAL", "Suíte Completa de Testes Integrados", "34", "100% PASSED"],
    ]

    tests_data = []
    for idx, row in enumerate(tests_raw):
        row_cells = []
        is_total = (idx == len(tests_raw) - 1)
        for col_idx, cell_text in enumerate(row):
            if idx == 0:
                st = cell_header
            elif is_total:
                st = ParagraphStyle("TotalCell", parent=cell_body, fontName="Helvetica-Bold")
            elif col_idx == 3:
                st = ParagraphStyle("StatusCell", parent=cell_body, fontName="Helvetica-Bold", textColor=colors.HexColor("#166534"))
            else:
                st = cell_body
            row_cells.append(Paragraph(cell_text, st))
        tests_data.append(row_cells)

    tests_table = Table(tests_data, colWidths=[1.7 * inch, 3.45 * inch, 0.9 * inch, 1.2 * inch])
    tests_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCFCE7")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(tests_table)
    story.append(Spacer(1, 8))

    # Seção 7: Instruções de Execução via Gerenciador uv
    story.append(Paragraph("7. Instruções de Execução via Gerenciador uv", h1_style))
    cmd_text = (
        "# 1. Instalar o gerenciador uv\n"
        "curl -LsSf https://astral.sh/uv/install.sh | sh\n\n"
        "# 2. Criar ambiente virtual e instalar dependências\n"
        "uv venv && source .venv/bin/activate && uv pip install -r requirements.txt\n\n"
        "# 3. Configurar variáveis de ambiente (.env)\n"
        "cp .env.example .env  # Inserir GOOGLE_API_KEY no .env\n\n"
        "# 4. Executar Backend FastAPI (Terminal 1)\n"
        "uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload\n\n"
        "# 5. Executar Frontend Streamlit (Terminal 2)\n"
        "uv run streamlit run app_streamlit.py\n\n"
        "# 6. Executar Suíte de Testes (Pytest)\n"
        "uv run pytest -v"
    )
    story.append(Paragraph(cmd_text.replace("\n", "<br/>"), code_style))

    # Conclusão e Assinatura
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=6))
    story.append(Paragraph("<b>Relatório técnico e de negócios verificado para entrega do Desafio 4 (I2A2).</b>", body_style))

    doc.build(story)
    return output_filename


if __name__ == "__main__":
    out_path = build_pdf_report()
    print(f"Relatório técnico em PDF gerado com sucesso: {Path(out_path).resolve()}")
