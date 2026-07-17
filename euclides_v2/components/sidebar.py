from __future__ import annotations

import streamlit as st

from models.source import SourceFile
from services.embedding_service import has_embedding_api_key
from services.llm_service import DEFAULT_GEMINI_MODEL, LlmSettings


MAX_SOURCES = 3
DEFAULT_SYSTEM_PROMPT = """Voce e o Euclides, um assistente de estudo academico.
Use apenas as fontes em PDF carregadas pelo usuario.
Explique com clareza, cite o documento quando possivel e avise quando algo nao estiver nas fontes.
Modo de ensino: [[TEACHING_MODE]]
Fontes carregadas: [[SOURCES]]
Estilo de citacao: [[CITATION_STYLE]]
Estrategia de resposta: [[ANSWER_STRATEGY]]
"""


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def source_names() -> str:
    if not st.session_state.sources:
        return "Nenhum PDF carregado ainda."
    return ", ".join(source.name for source in st.session_state.sources)


def final_system_prompt() -> str:
    return (
        st.session_state.base_system_prompt
        .replace("[[TEACHING_MODE]]", st.session_state.teaching_mode)
        .replace("[[SOURCES]]", source_names())
        .replace("[[CITATION_STYLE]]", st.session_state.citation_style)
        .replace("[[ANSWER_STRATEGY]]", st.session_state.answer_strategy)
    )


def current_llm_settings() -> LlmSettings:
    return LlmSettings(
        provider=st.session_state.model_provider,
        model_name=st.session_state.model_name,
        temperature=float(st.session_state.temperature),
        max_tokens=int(st.session_state.max_tokens),
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Fontes")
        st.caption(f"Adicione ate {MAX_SOURCES} documentos em PDF.")

        uploaded_files = st.file_uploader(
            "Adicionar fontes",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            current_names = {source.name for source in st.session_state.sources}
            remaining_slots = MAX_SOURCES - len(st.session_state.sources)

            for uploaded_file in uploaded_files[:remaining_slots]:
                if uploaded_file.name not in current_names:
                    st.session_state.sources.append(
                        SourceFile(
                            name=uploaded_file.name,
                            size=uploaded_file.size,
                            content=uploaded_file.getvalue(),
                        )
                    )

        st.divider()
        st.subheader("Arquivos carregados")

        if not st.session_state.sources:
            st.info("Nenhum PDF carregado.")
            return

        for source in st.session_state.sources:
            st.write(f"**{source.name}**")
            st.caption(format_size(source.size))
            if st.button("Remover", key=f"remove-{source.name}", use_container_width=True):
                st.session_state.sources = [
                    item for item in st.session_state.sources if item.name != source.name
                ]
                st.rerun()

        st.caption(f"{len(st.session_state.sources)} de {MAX_SOURCES} fontes adicionadas.")


def render_configuration_sidebar() -> None:
    with st.sidebar:
        st.divider()
        st.header("Configuracao futura")
        st.caption("Configuracao para modelo real, RAG e ferramentas.")

        with st.expander("Model settings", expanded=False):
            st.selectbox(
                "Provedor",
                ["Placeholder", "Ollama", "OpenAI", "Gemini"],
                key="model_provider",
            )
            st.text_input("Modelo", key="model_name", placeholder=DEFAULT_GEMINI_MODEL)
            st.slider("Temperatura", 0.0, 1.5, key="temperature", step=0.1)
            st.number_input(
                "Max tokens",
                min_value=256,
                max_value=16000,
                step=256,
                key="max_tokens",
            )

        with st.expander("Model config", expanded=False):
            st.selectbox(
                "Modo de busca",
                ["Lexical", "Vetorial", "Hibrida"],
                key="retrieval_mode",
                help=(
                    "Lexical nao usa API. Vetorial usa embeddings Gemini quando ha chave. "
                    "Hibrida combina embeddings com busca lexical."
                ),
            )
            if st.session_state.retrieval_mode == "Lexical":
                st.caption("Busca local sem custo de API.")
            elif st.session_state.retrieval_mode == "Vetorial":
                st.caption("Usa embeddings Gemini quando GEMINI_API_KEY esta configurada.")
            else:
                st.caption("Recomendado para qualidade: embeddings Gemini + busca lexical.")

            if st.session_state.retrieval_mode != "Lexical":
                if has_embedding_api_key():
                    st.caption("GEMINI_API_KEY detectada para embeddings.")
                else:
                    st.warning(
                        "GEMINI_API_KEY nao configurada. A busca vai voltar para lexical.",
                    )
            st.number_input(
                "Trechos recuperados por pergunta",
                min_value=1,
                max_value=20,
                key="retrieval_k",
            )
            st.checkbox("Mostrar etapas quando disponivel", key="show_reasoning")
            st.selectbox(
                "Formato de citacao",
                ["Nome do arquivo", "Arquivo + pagina", "ABNT simplificado"],
                key="citation_style",
            )
            st.selectbox(
                "Estrategia de resposta",
                [
                    "Responder somente com as fontes",
                    "Permitir conhecimento geral marcado",
                    "Perguntar quando faltar contexto",
                ],
                key="answer_strategy",
            )

        with st.expander("Teaching mode", expanded=False):
            st.radio(
                "Modo",
                [
                    "Tutor socratico",
                    "Explicacao direta",
                    "Preparacao para prova",
                    "Revisao critica",
                    "Passo a passo",
                ],
                key="teaching_mode",
            )

        with st.expander("Active tools", expanded=False):
            st.multiselect(
                "Ferramentas disponiveis",
                ["Chat", "Resumo", "Mapa mental", "Tabela de dados", "Citas", "Flashcards", "Quiz"],
                key="active_tools",
            )
            if st.session_state.active_tools:
                st.write(", ".join(st.session_state.active_tools))

        with st.expander("Final system prompt preview", expanded=False):
            st.text_area(
                "Prompt base",
                key="base_system_prompt",
                height=180,
                help="Use placeholders como [[TEACHING_MODE]] e [[SOURCES]].",
            )
            st.code(final_system_prompt(), language="text")
