from __future__ import annotations

from dataclasses import dataclass
from typing import List

import streamlit as st


MAX_SOURCES = 3
DEFAULT_SYSTEM_PROMPT = """Voce e o Euclides, um assistente de estudo academico.
Use apenas as fontes em PDF carregadas pelo usuario.
Explique com clareza, cite o documento quando possivel e avise quando algo nao estiver nas fontes.
Modo de ensino: [[TEACHING_MODE]]
Fontes carregadas: [[SOURCES]]
"""


@dataclass(frozen=True)
class SourceFile:
    name: str
    size: int
    content: bytes


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def init_state() -> None:
    st.session_state.setdefault("sources", [])
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("model_provider", "Placeholder")
    st.session_state.setdefault("model_name", "Modelo ainda nao conectado")
    st.session_state.setdefault("temperature", 0.2)
    st.session_state.setdefault("max_tokens", 1200)
    st.session_state.setdefault("retrieval_k", 5)
    st.session_state.setdefault("teaching_mode", "Tutor socratico")
    st.session_state.setdefault("show_reasoning", False)
    st.session_state.setdefault("active_tools", ["Resumo", "Mapa mental", "Tabela de dados"])
    st.session_state.setdefault("base_system_prompt", DEFAULT_SYSTEM_PROMPT)
    st.session_state.setdefault("simulated_pipeline", "Chat academico")


def add_sources(uploaded_files: List[object]) -> None:
    current_names = {source.name for source in st.session_state.sources}
    remaining_slots = MAX_SOURCES - len(st.session_state.sources)
    added_count = 0

    if remaining_slots <= 0:
        st.warning("Limite atingido: remova um documento para adicionar outro PDF.")
        return

    for uploaded_file in uploaded_files:
        if uploaded_file.name in current_names:
            continue
        if added_count >= remaining_slots:
            break

        st.session_state.sources.append(
            SourceFile(
                name=uploaded_file.name,
                size=uploaded_file.size,
                content=uploaded_file.getvalue(),
            )
        )
        current_names.add(uploaded_file.name)
        added_count += 1

    unique_selected = {uploaded_file.name for uploaded_file in uploaded_files}
    if len(unique_selected) > remaining_slots:
        st.warning(f"Foram adicionados apenas {added_count} arquivo(s). O limite maximo e {MAX_SOURCES} PDFs.")


def remove_source(source_name: str) -> None:
    st.session_state.sources = [
        source for source in st.session_state.sources if source.name != source_name
    ]


def source_names() -> str:
    if not st.session_state.sources:
        return "Nenhum PDF carregado ainda."
    return ", ".join(source.name for source in st.session_state.sources)


def final_system_prompt() -> str:
    return (
        st.session_state.base_system_prompt
        .replace("[[TEACHING_MODE]]", st.session_state.teaching_mode)
        .replace("[[SOURCES]]", source_names())
    )


def render_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --euclides-bg: #f7f5ef;
            --euclides-panel: #ffffff;
            --euclides-border: #ddd7ca;
            --euclides-text: #26231f;
            --euclides-muted: #706a60;
            --euclides-accent: #3f6f64;
        }

        .stApp {
            background: var(--euclides-bg);
            color: var(--euclides-text);
        }

        [data-testid="stSidebar"] {
            background: #eee9de;
            border-right: 1px solid var(--euclides-border);
        }

        .euclides-header {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 10px 0 18px;
            border-bottom: 1px solid var(--euclides-border);
            margin-bottom: 18px;
        }

        .euclides-logo {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, #315c53, #78a08f);
            display: grid;
            place-items: center;
            color: white;
            font-weight: 800;
            font-size: 24px;
            letter-spacing: 0;
            box-shadow: 0 8px 22px rgba(49, 92, 83, 0.18);
        }

        .euclides-title {
            margin: 0;
            font-size: 30px;
            line-height: 1.1;
            font-weight: 750;
        }

        .euclides-subtitle {
            margin: 4px 0 0;
            color: var(--euclides-muted);
            font-size: 15px;
        }

        .source-card {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid var(--euclides-border);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 8px;
        }

        .source-name {
            font-weight: 650;
            overflow-wrap: anywhere;
        }

        .source-meta {
            color: var(--euclides-muted);
            font-size: 13px;
            margin-top: 2px;
        }

        .tool-panel {
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid var(--euclides-border);
            border-radius: 8px;
            padding: 16px;
            margin-top: 8px;
        }

        .placeholder-output {
            border: 1px dashed #b8b0a2;
            border-radius: 8px;
            padding: 14px;
            color: var(--euclides-muted);
            background: rgba(255, 255, 255, 0.45);
        }

        .config-pill {
            display: inline-block;
            padding: 5px 9px;
            border: 1px solid var(--euclides-border);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.72);
            color: var(--euclides-muted);
            font-size: 12px;
            margin: 0 5px 5px 0;
        }

        .pipeline-step {
            border-left: 3px solid var(--euclides-accent);
            background: rgba(255, 255, 255, 0.6);
            padding: 8px 10px;
            margin-bottom: 8px;
            border-radius: 0 8px 8px 0;
        }

        .pipeline-title {
            font-weight: 700;
            margin-bottom: 2px;
        }

        .pipeline-note {
            color: var(--euclides-muted);
            font-size: 13px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="euclides-header">
            <div class="euclides-logo">E</div>
            <div>
                <h1 class="euclides-title">Euclides</h1>
                <p class="euclides-subtitle">Notebook de estudo para conversar com artigos em PDF.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources() -> None:
    with st.sidebar:
        st.header("Fontes")
        st.caption(f"Adicione ate {MAX_SOURCES} documentos em PDF.")

        uploaded_files = st.file_uploader(
            "Adicionar fontes",
            type=["pdf"],
            accept_multiple_files=True,
            help="Selecione PDFs do seu computador. O limite atual e de 3 arquivos.",
        )

        if uploaded_files:
            add_sources(uploaded_files)

        st.divider()
        st.subheader("Arquivos carregados")

        if not st.session_state.sources:
            st.info("Nenhum PDF carregado.")
            return

        for source in st.session_state.sources:
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-name">{source.name}</div>
                    <div class="source-meta">PDF - {format_size(source.size)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Remover", key=f"remove-{source.name}", use_container_width=True):
                remove_source(source.name)
                st.rerun()

        st.caption(f"{len(st.session_state.sources)} de {MAX_SOURCES} fontes adicionadas.")


def render_configuration_sidebar() -> None:
    with st.sidebar:
        st.divider()
        st.header("Configuracao futura")
        st.caption("Somente visual por enquanto. Nenhum modelo ou agente esta conectado.")

        with st.expander("Model settings", expanded=False):
            st.selectbox(
                "Provedor",
                ["Placeholder", "OpenAI", "Anthropic", "Google", "Ollama", "Azure OpenAI"],
                key="model_provider",
            )
            st.text_input("Modelo", key="model_name")
            st.slider("Temperatura", 0.0, 1.5, key="temperature", step=0.1)
            st.number_input("Max tokens", min_value=256, max_value=16000, step=256, key="max_tokens")

        with st.expander("Model config", expanded=False):
            st.number_input("Trechos recuperados por pergunta", min_value=1, max_value=20, key="retrieval_k")
            st.checkbox("Mostrar raciocinio/etapas quando disponivel", key="show_reasoning")
            st.selectbox(
                "Formato de citacao",
                ["Nome do arquivo", "Arquivo + pagina", "ABNT simplificado"],
                key="citation_style",
            )
            st.selectbox(
                "Estrategia de resposta",
                ["Responder somente com as fontes", "Permitir conhecimento geral marcado", "Perguntar quando faltar contexto"],
                key="answer_strategy",
            )

        with st.expander("Teaching mode", expanded=False):
            st.radio(
                "Modo",
                ["Tutor socratico", "Explicacao direta", "Preparacao para prova", "Revisao critica", "Passo a passo"],
                key="teaching_mode",
            )
            st.caption("Esse valor entra no prompt final e podera guiar o comportamento da LLM.")

        with st.expander("Active tools", expanded=False):
            st.multiselect(
                "Ferramentas disponiveis na interface",
                ["Chat", "Resumo", "Mapa mental", "Tabela de dados", "Citas", "Flashcards", "Quiz"],
                key="active_tools",
            )
            if st.session_state.active_tools:
                pills = "".join(
                    f'<span class="config-pill">{tool}</span>'
                    for tool in st.session_state.active_tools
                )
                st.markdown(pills, unsafe_allow_html=True)

        with st.expander("Final system prompt preview", expanded=False):
            st.text_area(
                "Prompt base",
                key="base_system_prompt",
                height=180,
                help="Use placeholders como [[TEACHING_MODE]] e [[SOURCES]].",
            )
            st.code(final_system_prompt(), language="text")


def render_ai_readiness_panel() -> None:
    st.subheader("Arquitetura futura de IA")
    st.caption("Visualizacao simulada do fluxo que sera conectado a modelos, RAG e ferramentas.")

    steps = [
        ("1. Fontes PDF", "Recebe ate 3 artigos e mantem a lista de documentos ativos."),
        ("2. Extracao de texto", "Etapa futura para ler paginas, limpar texto e preservar metadados."),
        ("3. Indexacao RAG", "Etapa futura para criar embeddings e buscar trechos relevantes."),
        ("4. Orquestracao", "Escolhe entre chat, resumo, mapa mental ou tabela conforme a acao do usuario."),
        ("5. Modelo de linguagem", "Gera resposta usando o prompt final, o modo de ensino e as fontes recuperadas."),
        ("6. Resposta com evidencias", "Apresenta resposta, citacoes e artefatos de estudo na interface."),
    ]

    with st.expander("Pipeline planejado", expanded=True):
        for title, note in steps:
            st.markdown(
                f"""
                <div class="pipeline-step">
                    <div class="pipeline-title">{title}</div>
                    <div class="pipeline-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander("Simulador de execucao", expanded=False):
        st.selectbox(
            "Fluxo que deseja simular",
            ["Chat academico", "Resumo por topico", "Mapa mental", "Tabela de dados"],
            key="simulated_pipeline",
        )
        st.write("**Entrada simulada:** documentos carregados + pergunta/topico do usuario")
        st.write(f"**Ferramenta selecionada:** {st.session_state.simulated_pipeline}")
        st.write(f"**Modo de ensino:** {st.session_state.teaching_mode}")
        st.write(f"**Modelo configurado:** {st.session_state.model_provider} / {st.session_state.model_name}")
        st.info(
            "Simulacao: nesta versao, o Euclides apenas mostra o fluxo previsto. "
            "Na proxima etapa, esse painel pode registrar chamadas reais de RAG, LLM e ferramentas."
        )


def render_chat() -> None:
    st.subheader("Chat com os artigos")
    st.caption(f"Fontes em uso: {source_names()}")

    with st.expander("Contexto ativo", expanded=False):
        config_left, config_right = st.columns(2)
        with config_left:
            st.write(f"**Modelo:** {st.session_state.model_provider} / {st.session_state.model_name}")
            st.write(f"**Modo de ensino:** {st.session_state.teaching_mode}")
        with config_right:
            st.write(f"**Temperatura:** {st.session_state.temperature}")
            st.write(f"**Ferramentas ativas:** {', '.join(st.session_state.active_tools) or 'Nenhuma'}")

    chat_box = st.container(height=360, border=True)
    with chat_box:
        if not st.session_state.messages:
            st.markdown(
                '<div class="placeholder-output">Faca perguntas sobre os PDFs carregados. A conexao com a LLM sera adicionada depois.</div>',
                unsafe_allow_html=True,
            )

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    prompt = st.chat_input("Pergunte algo sobre os documentos...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "Chat preparado. Quando uma LLM for conectada, vou responder usando "
                    "os PDFs carregados como fontes."
                ),
            }
        )
        st.rerun()


def render_tools() -> None:
    st.subheader("Funcoes de estudo")

    tab_summary, tab_map, tab_table = st.tabs(["Resumo", "Mapa mental", "Tabela de dados"])

    with tab_summary:
        st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
        topic = st.text_input("Topico para resumir", placeholder="Ex.: metodologia, resultados, conclusao")
        if st.button("Gerar resumo", use_container_width=True):
            if not st.session_state.sources:
                st.warning("Carregue pelo menos um PDF antes de gerar um resumo.")
            elif not topic.strip():
                st.warning("Informe um topico para orientar o resumo.")
            else:
                st.markdown(
                    f"""
                    <div class="placeholder-output">
                        Resumo pendente para o topico <strong>{topic}</strong>.
                        A interface esta pronta para enviar este pedido a uma LLM usando as fontes: {source_names()}.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_map:
        st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
        map_topic = st.text_input("Tema do mapa mental", placeholder="Ex.: conceitos principais do artigo")
        if st.button("Gerar mapa mental", use_container_width=True):
            if not st.session_state.sources:
                st.warning("Carregue pelo menos um PDF antes de gerar um mapa mental.")
            elif not map_topic.strip():
                st.warning("Informe um tema para o mapa mental.")
            else:
                st.markdown(
                    f"""
                    <div class="placeholder-output">
                        Diagrama pendente para <strong>{map_topic}</strong>.<br>
                        Estrutura sugerida: tema central, conceitos, evidencias, autores e conclusoes.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_table:
        st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
        table_topic = st.text_input("Dados que deseja extrair", placeholder="Ex.: amostra, metodo, variaveis, resultados")
        if st.button("Gerar tabela", use_container_width=True):
            if not st.session_state.sources:
                st.warning("Carregue pelo menos um PDF antes de gerar uma tabela.")
            elif not table_topic.strip():
                st.warning("Informe quais dados devem entrar na tabela.")
            else:
                st.dataframe(
                    [
                        {
                            "Documento": "Fonte PDF",
                            "Campo": table_topic,
                            "Valor": "Pendente de extracao pela LLM",
                        }
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Euclides", page_icon="E", layout="wide")
    init_state()
    render_styles()
    render_sources()
    render_configuration_sidebar()
    render_header()

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        render_chat()
    with right:
        render_tools()
        render_ai_readiness_panel()


if __name__ == "__main__":
    main()
