"""Interface Web Streamlit para a aplicação AI CSV Query."""

import json
import os
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Configuração da página Streamlit
st.set_page_config(
    page_title="AI CSV Query — Agente Analítico de CSVs",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização visual customizada (Dark/Modern Elegance)
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #9CA3AF;
        margin-bottom: 1.5rem;
    }
    .status-online {
        color: #10B981;
        font-weight: 600;
    }
    .status-offline {
        color: #EF4444;
        font-weight: 600;
    }
    /* Estilização para os botões de rádio horizontais de navegação */
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        gap: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Configuração do URL base da API FastAPI
DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# --- Funções do Cliente HTTP Backend ---

def check_backend_health(api_url: str) -> bool:
    """Verifica se o backend FastAPI está respondendo no endpoint /health."""
    try:
        resp = requests.get(f"{api_url}/health", timeout=3)
        return resp.status_code == 200 and resp.json().get("status") == "ok"
    except Exception:
        return False


def get_datasets_list(api_url: str) -> list[dict]:
    """Obtém a lista de datasets cadastrados no backend."""
    try:
        resp = requests.get(f"{api_url}/datasets", timeout=5)
        if resp.status_code == 200:
            return resp.json().get("datasets", [])
        return []
    except Exception:
        return []


def get_dataset_details(api_url: str, dataset_id: str) -> dict | None:
    """Obtém os detalhes e esquema de um dataset específico."""
    try:
        resp = requests.get(f"{api_url}/datasets/{dataset_id}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def upload_zip_file(api_url: str, file_bytes: bytes, filename: str) -> tuple[bool, dict | str]:
    """Envia um arquivo ZIP para a rota POST /upload da API."""
    try:
        files = {"file": (filename, file_bytes, "application/zip")}
        resp = requests.post(f"{api_url}/upload", files=files, timeout=60)
        if resp.status_code in (200, 201):
            return True, resp.json()
        error_detail = resp.json().get("detail", "Erro desconhecido durante upload.")
        return False, f"Erro HTTP {resp.status_code}: {error_detail}"
    except Exception as e:
        return False, f"Erro na conexão com a API: {e!s}"


def ask_question(api_url: str, dataset_id: str, question: str) -> tuple[bool, dict | str]:
    """Envia uma pergunta em linguagem natural para o endpoint POST /ask."""
    try:
        payload = {"dataset_id": dataset_id, "question": question}
        resp = requests.post(f"{api_url}/ask", json=payload, timeout=60)
        if resp.status_code == 200:
            return True, resp.json()
        error_detail = resp.json().get("detail", "Falha ao obter resposta do agente.")
        return False, f"Erro HTTP {resp.status_code}: {error_detail}"
    except Exception as e:
        return False, f"Erro na requisição: {e!s}"


def delete_dataset(api_url: str, dataset_id: str) -> bool:
    """Solicita a remoção de um dataset no backend."""
    try:
        resp = requests.delete(f"{api_url}/datasets/{dataset_id}", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


# --- Inicialização do Session State ---

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_dataset_id" not in st.session_state:
    st.session_state.selected_dataset_id = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

TAB_CHAT = "💬 Chat & Consultas"
TAB_UPLOAD = "📤 Upload de Dataset"
TAB_SCHEMA = "📋 Esquemas & Tabelas"

if "active_tab" not in st.session_state:
    st.session_state.active_tab = TAB_CHAT


# --- Barra Lateral (Sidebar) ---

st.sidebar.title("⚙️ Configurações & Datasets")

# Configuração da URL da API
api_url = st.sidebar.text_input("Endereço da API Backend", value=DEFAULT_API_URL).rstrip("/")

# Health Check da API
is_online = check_backend_health(api_url)
if is_online:
    st.sidebar.markdown("Status do Backend: <span class='status-online'>🟢 Online</span>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("Status do Backend: <span class='status-offline'>🔴 Offline (verifique o servidor)</span>", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Listagem e Seleção de Datasets
st.sidebar.subheader("📦 Dataset Ativo")

datasets = get_datasets_list(api_url) if is_online else []

if datasets:
    dataset_options = {f"{ds['name']} ({ds['dataset_id']})": ds['dataset_id'] for ds in datasets}

    # Atualiza seleção padrão se houver
    current_idx = 0
    if st.session_state.selected_dataset_id:
        for idx, (label, ds_id) in enumerate(dataset_options.items()):
            if ds_id == st.session_state.selected_dataset_id:
                current_idx = idx
                break

    selected_label = st.sidebar.selectbox(
        "Selecione o dataset para consultas:",
        options=list(dataset_options.keys()),
        index=current_idx,
    )
    selected_ds_id = dataset_options[selected_label]
    st.session_state.selected_dataset_id = selected_ds_id

    # Exibe resumo do dataset selecionado
    selected_ds_meta = next((d for d in datasets if d["dataset_id"] == selected_ds_id), None)
    if selected_ds_meta:
        with st.sidebar.expander("ℹ️ Detalhes do Dataset", expanded=True):
            st.markdown(f"**ID:** `{selected_ds_meta['dataset_id']}`")
            st.markdown(f"**Tabelas ({len(selected_ds_meta['tables'])}):** {', '.join(selected_ds_meta['tables'])}")
            st.markdown(f"**Linhas Totais:** {selected_ds_meta['row_count_total']:,}")
            st.markdown(f"**Upload em:** {selected_ds_meta['uploaded_at'][:19].replace('T', ' ')}")

            if st.button("🗑️ Excluir este dataset", use_container_width=True, type="secondary"):
                if delete_dataset(api_url, selected_ds_id):
                    st.toast("Dataset removido com sucesso!", icon="✅")
                    st.session_state.selected_dataset_id = None
                    st.rerun()
                else:
                    st.error("Falha ao remover o dataset.")
else:
    st.sidebar.info("Nenhum dataset carregado. Faça upload na aba Upload.")
    st.session_state.selected_dataset_id = None

st.sidebar.markdown("---")

# Perguntas de Demonstração (PRD)
st.sidebar.subheader("💡 Perguntas Rápidas (PRD)")
perguntas_demo = [
    "Qual fornecedor recebeu o maior valor no período?",
    "Qual produto apresentou o maior volume comprado?",
    "Qual foi o total gasto em cada mês?",
    "Quais foram os cinco maiores fornecedores?",
    "Qual categoria apresentou maior crescimento nas compras?",
]

for p in perguntas_demo:
    if st.sidebar.button(p, use_container_width=True):
        st.session_state.pending_question = p
        st.session_state.active_tab = TAB_CHAT
        st.rerun()


# --- Cabeçalho Principal ---

st.markdown("<h1 class='main-header'>AI CSV Query System</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Consulta inteligente em linguagem natural sobre conjuntos de dados CSV via Agentes PydanticAI & DuckDB</p>", unsafe_allow_html=True)


# --- Controle de Navegação de Telas ---

selected_nav = st.radio(
    "Navegação Principal",
    options=[TAB_CHAT, TAB_UPLOAD, TAB_SCHEMA],
    index=[TAB_CHAT, TAB_UPLOAD, TAB_SCHEMA].index(st.session_state.active_tab),
    horizontal=True,
    label_visibility="collapsed",
)
st.session_state.active_tab = selected_nav

st.markdown("---")


# --- ABA 1: Chat & Consultas ---

if st.session_state.active_tab == TAB_CHAT:
    if not is_online:
        st.warning("⚠️ O backend da API não está acessível. Certifique-se de executar `uvicorn app.main:app --reload` no terminal.")

    if not st.session_state.selected_dataset_id:
        st.info("👈 Por favor, selecione um dataset na barra lateral ou faça upload de um novo arquivo na aba **Upload de Dataset** para começar a consultar.")
    else:
        st.markdown(f"**Consultando dataset:** `{st.session_state.selected_dataset_id}`")

        # Exibe histórico de mensagens do Chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                # Renderiza componentes adicionais caso existam na mensagem do assistente
                if msg["role"] == "assistant":
                    if msg.get("sql"):
                        with st.expander("🔍 Query SQL executada pelo agente"):
                            st.code(msg["sql"], language="sql")

                    if msg.get("table_data"):
                        st.markdown("**📊 Tabela de Resultados:**")
                        df_res = pd.DataFrame(msg["table_data"])
                        st.dataframe(df_res, use_container_width=True)

                    if msg.get("chart_spec"):
                        st.markdown("**📈 Visualização Gráfica:**")
                        chart_spec = msg["chart_spec"]
                        plotly_spec = chart_spec.get("plotly_spec")
                        if plotly_spec:
                            fig = go.Figure(plotly_spec)
                            st.plotly_chart(fig, use_container_width=True)

        # Trata pergunta disparada pelas perguntas rápidas
        prompt_input = st.chat_input("Digite sua pergunta sobre os dados (ex: 'Qual fornecedor teve o maior valor total?')...")

        if st.session_state.pending_question:
            prompt_input = st.session_state.pending_question
            st.session_state.pending_question = None

        if prompt_input:
            # Registra mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt_input})
            with st.chat_message("user"):
                st.markdown(prompt_input)

            # Executa consulta no backend com o Agente de IA
            with st.chat_message("assistant"):
                with st.spinner("🤖 O Agente de IA está analisando o esquema e executando a consulta SQL no DuckDB..."):
                    success, result = ask_question(api_url, st.session_state.selected_dataset_id, prompt_input)

                if success and isinstance(result, dict):
                    answer_text = result.get("answer_text", "Consulta concluída.")
                    sql_used = result.get("sql_used")
                    table_data = result.get("table_data")
                    chart_spec = result.get("chart_spec")

                    st.markdown(answer_text)

                    if sql_used:
                        with st.expander("🔍 Query SQL executada pelo agente"):
                            st.code(sql_used, language="sql")

                    if table_data:
                        st.markdown("**📊 Tabela de Resultados:**")
                        df_res = pd.DataFrame(table_data)
                        st.dataframe(df_res, use_container_width=True)

                    if chart_spec and chart_spec.get("plotly_spec"):
                        st.markdown("**📈 Visualização Gráfica:**")
                        fig = go.Figure(chart_spec["plotly_spec"])
                        st.plotly_chart(fig, use_container_width=True)

                    # Salva resposta do assistente no session_state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer_text,
                        "sql": sql_used,
                        "table_data": table_data,
                        "chart_spec": chart_spec,
                    })

                else:
                    error_msg = str(result)
                    st.error(f"❌ Não foi possível responder à pergunta: {error_msg}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ Erro ao processar consulta: {error_msg}",
                    })


# --- ABA 2: Upload de Dataset ---

elif st.session_state.active_tab == TAB_UPLOAD:
    st.subheader("📤 Ingestão de Novo Dataset ZIP")
    st.markdown(
        """
        Faça upload de um arquivo contendo:
        - Arquivo(s) `.csv` com dados brutos.
        - Arquivo de dicionário de dados (`dicionario.json` ou `dicionario.txt`) descrevendo o significado de cada coluna.
        """
    )

    uploaded_file = st.file_uploader("Selecione um arquivo .zip:", type=["zip"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        st.write(f"Arquivo selecionado: `{uploaded_file.name}` ({file_size_mb:.2f} MB)")

        if st.button("🚀 Processar e Cargar no DuckDB", type="primary", use_container_width=True):
            with st.spinner("⏳ Extraindo ZIP, validando dicionários e inserindo no banco DuckDB..."):
                success, resp_data = upload_zip_file(api_url, file_bytes, uploaded_file.name)

            if success and isinstance(resp_data, dict):
                st.success(f"✅ Dataset processado com sucesso! ID: `{resp_data['dataset_id']}`")
                st.session_state.selected_dataset_id = resp_data['dataset_id']

                st.markdown("### 📑 Tabelas Criadas")
                tables = resp_data.get("tables", [])
                for t in tables:
                    with st.expander(f"Tabela `{t['name']}` ({t['row_count']:,} linhas)", expanded=True):
                        cols = t.get("columns", [])
                        df_cols = pd.DataFrame([
                            {
                                "Coluna": c["name"],
                                "Tipo DuckDB": c["dtype"],
                                "Descrição Semântica": c.get("description") or "—"
                            } for c in cols
                        ])
                        st.dataframe(df_cols, use_container_width=True)

                st.toast("Upload concluído! Redirecionando para o Chat...", icon="🎉")
            else:
                st.error(f"❌ Falha no upload: {resp_data}")


# --- ABA 3: Esquemas & Tabelas ---

elif st.session_state.active_tab == TAB_SCHEMA:
    st.subheader("📋 Estrutura do Dataset Selecionado")

    if not st.session_state.selected_dataset_id:
        st.info("Nenhum dataset selecionado. Selecione um dataset na barra lateral.")
    elif not is_online:
        st.error("Conexão com a API offline.")
    else:
        ds_id = st.session_state.selected_dataset_id
        details = get_dataset_details(api_url, ds_id)

        if details:
            st.markdown(f"**ID do Dataset:** `{details['dataset_id']}`")
            st.markdown(f"**Status:** `{details.get('message', 'Carregado')}`")

            for tbl in details.get("tables", []):
                st.markdown(f"### Tabela: `{tbl['name']}`")
                st.markdown(f"**Quantidade de Registros:** {tbl['row_count']:,} linhas")

                cols_data = []
                for col in tbl.get("columns", []):
                    cols_data.append({
                        "Coluna": col["name"],
                        "Tipo de Dado": col["dtype"],
                        "Descrição no Dicionário": col.get("description") or "Sem descrição fornecida",
                    })

                df_schema = pd.DataFrame(cols_data)
                st.dataframe(df_schema, use_container_width=True)
                st.markdown("---")
        else:
            st.warning("Não foi possível carregar os detalhes do dataset.")
