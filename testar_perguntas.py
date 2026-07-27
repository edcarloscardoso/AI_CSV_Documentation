#!/usr/bin/env python3
"""
Script de teste interativo do endpoint POST /ask.

Uso:
    .venv/bin/python testar_perguntas.py <dataset_id>

Exemplo:
    .venv/bin/python testar_perguntas.py ds_47c6d5e7e8c8
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

# Perguntas de demonstração do PRD
PERGUNTAS_DEMO = [
    "Qual fornecedor recebeu o maior valor no período?",
    "Qual produto apresentou o maior volume comprado?",
    "Qual foi o total gasto em cada mês?",
    "Quais foram os cinco maiores fornecedores?",
    "Qual categoria apresentou maior crescimento nas compras?",
]

SEPARADOR = "─" * 60


def cor(texto: str, codigo: str) -> str:
    cores = {"verde": "\033[32m", "vermelho": "\033[31m", "amarelo": "\033[33m",
             "ciano": "\033[36m", "negrito": "\033[1m", "reset": "\033[0m"}
    return f"{cores.get(codigo, '')}{texto}{cores['reset']}"


def chamar_ask(dataset_id: str, pergunta: str) -> dict:
    payload = json.dumps({"dataset_id": dataset_id, "question": pergunta}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def exibir_resposta(resposta: dict, numero: int, pergunta: str) -> None:
    print(f"\n{SEPARADOR}")
    print(cor(f"  Pergunta {numero}: {pergunta}", "negrito"))
    print(SEPARADOR)

    tipo = resposta.get("answer_type", "?")
    texto = resposta.get("answer_text", "")
    sql = resposta.get("sql_used", "")
    tabela = resposta.get("table_data") or []
    grafico = resposta.get("chart_spec")

    print(f"  Tipo de resposta : {cor(tipo.upper(), 'ciano')}")
    print(f"  Resposta         : {cor(texto, 'verde')}")

    if sql:
        print(f"\n  SQL executado:")
        print(f"  {cor(sql, 'amarelo')}")

    if tabela:
        print(f"\n  Dados ({len(tabela)} linha(s)):")
        if tabela:
            colunas = list(tabela[0].keys())
            # Cabeçalho
            header = "  | " + " | ".join(f"{c:<20}" for c in colunas[:4]) + " |"
            print(cor(header, "ciano"))
            print("  " + "-" * (len(header) - 2))
            # Linhas
            for linha in tabela[:5]:
                row = "  | " + " | ".join(
                    f"{str(linha.get(c, '')):<20}" for c in colunas[:4]
                ) + " |"
                print(row)
            if len(tabela) > 5:
                print(f"  ... e mais {len(tabela) - 5} linha(s)")

    if grafico:
        chart_t = grafico.get("chart_type", "?")
        print(f"\n  Gráfico: {cor(chart_t.upper(), 'verde')} (chart_spec disponível)")
        try:
            import plotly.graph_objects as go
            import webbrowser
            from pathlib import Path

            spec = grafico.get("plotly_spec")
            if spec:
                fig = go.Figure(spec)
                html_path = Path("grafico_preview.html").resolve()
                fig.write_html(str(html_path))
                print(cor(f"  📊 Gráfico interativo salvo em: {html_path}", "verde"))
                webbrowser.open(f"file://{html_path}")
        except Exception as e:
            print(f"  (Não foi possível abrir visualização interativa do gráfico: {e})")


def modo_interativo(dataset_id: str) -> None:
    print(cor("\n╔══════════════════════════════════════════════╗", "ciano"))
    print(cor("║   AI CSV Query — Teste Interativo de /ask   ║", "ciano"))
    print(cor("╚══════════════════════════════════════════════╝", "ciano"))
    print(f"\n  Dataset ID : {cor(dataset_id, 'negrito')}")
    print(f"  Endpoint   : {BASE_URL}/ask\n")

    print("  Opções:")
    print("    [1-5] Rodar pergunta de demonstração do PRD")
    print("    [t]   Rodar TODAS as perguntas de demo")
    print("    [p]   Digitar uma pergunta personalizada")
    print("    [q]   Sair\n")

    contador = 0
    while True:
        print(SEPARADOR)
        for i, q in enumerate(PERGUNTAS_DEMO, 1):
            print(f"  {i}. {q}")
        print()
        escolha = input("  Escolha [1-5 / t / p / q]: ").strip().lower()

        if escolha == "q":
            print(cor("\n  Encerrando. Até logo!\n", "verde"))
            break

        perguntas_para_testar = []

        if escolha == "t":
            perguntas_para_testar = list(enumerate(PERGUNTAS_DEMO, 1))
        elif escolha == "p":
            pergunta_custom = input("  Digite sua pergunta: ").strip()
            if pergunta_custom:
                perguntas_para_testar = [(0, pergunta_custom)]
        elif escolha.isdigit() and 1 <= int(escolha) <= len(PERGUNTAS_DEMO):
            idx = int(escolha)
            perguntas_para_testar = [(idx, PERGUNTAS_DEMO[idx - 1])]
        else:
            print(cor("  Opção inválida. Tente novamente.", "vermelho"))
            continue

        for num, pergunta in perguntas_para_testar:
            contador += 1
            print(f"\n  ⏳ Consultando... (pode demorar até 15s com LLM ativo)")
            try:
                resposta = chamar_ask(dataset_id, pergunta)
                exibir_resposta(resposta, contador, pergunta)
            except urllib.error.HTTPError as e:
                corpo = e.read().decode("utf-8")
                print(cor(f"\n  ERRO HTTP {e.code}: {corpo}", "vermelho"))
            except Exception as e:
                print(cor(f"\n  ERRO: {e}", "vermelho"))


def main() -> None:
    if len(sys.argv) < 2:
        print(f"\nUso: .venv/bin/python testar_perguntas.py <dataset_id>\n")
        print("Exemplo:")
        print("  .venv/bin/python testar_perguntas.py ds_47c6d5e7e8c8\n")
        sys.exit(1)

    dataset_id = sys.argv[1]

    # Verifica se a API está no ar
    try:
        urllib.request.urlopen(f"{BASE_URL}/health", timeout=5)
    except Exception:
        print(cor(f"\n  ERRO: API não está respondendo em {BASE_URL}", "vermelho"))
        print("  Certifique-se de que o servidor está rodando:\n")
        print("    .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload\n")
        sys.exit(1)

    modo_interativo(dataset_id)


if __name__ == "__main__":
    main()
