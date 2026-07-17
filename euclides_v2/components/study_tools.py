from __future__ import annotations

import streamlit as st

from models.source import RetrievedChunk
from components.sidebar import current_llm_settings, final_system_prompt
from services.export_service import build_tool_export, txt_filename
from services.llm_service import generate_response
from services.pdf_loader import load_pdf_corpus
from services.tool_service import (
    build_citations,
    build_citations_prompt,
    build_data_table,
    build_flashcards,
    build_flashcards_prompt,
    build_mind_map,
    build_mind_map_prompt,
    build_quiz,
    build_quiz_prompt,
    build_summary,
    build_summary_prompt,
    build_table_prompt,
)
from services.vector_retrieval import retrieve_chunks_with_status


def should_use_real_model() -> bool:
    return st.session_state.model_provider != "Placeholder"


def get_relevant_results_or_warn(topic: str) -> list[RetrievedChunk] | None:
    if not topic.strip():
        st.warning("Informe um topico para orientar a ferramenta.")
        return None

    corpus = load_pdf_corpus(st.session_state.sources)
    if not corpus.has_sources:
        st.warning("Carregue pelo menos um PDF antes de usar esta ferramenta.")
        return None

    if not corpus.has_text:
        st.warning(
            "Nao ha texto extraivel nos PDFs carregados. "
            "Verifique o Diagnostico das fontes."
        )
        return None

    retrieval_result = retrieve_chunks_with_status(
        query=topic,
        chunks=corpus.chunks,
        limit=st.session_state.retrieval_k,
        mode=st.session_state.retrieval_mode,
    )
    results = retrieval_result.chunks
    if retrieval_result.warning:
        st.warning(retrieval_result.warning)

    if not results:
        st.warning("Nenhum trecho relevante foi encontrado para esse topico.")
        return None

    return results


def render_study_tools() -> None:
    st.subheader("Ferramentas de estudo")

    enabled_tools = [
        tool
        for tool in ["Resumo", "Mapa mental", "Tabela de dados", "Citas", "Flashcards", "Quiz"]
        if tool in st.session_state.active_tools
    ]

    if not enabled_tools:
        st.info("Ative pelo menos uma ferramenta de estudo na sidebar.")
        return

    tabs = st.tabs(enabled_tools)
    tab_by_tool = dict(zip(enabled_tools, tabs))

    if "Resumo" in tab_by_tool:
        render_summary_tool(tab_by_tool["Resumo"])

    if "Mapa mental" in tab_by_tool:
        render_mind_map_tool(tab_by_tool["Mapa mental"])

    if "Tabela de dados" in tab_by_tool:
        render_table_tool(tab_by_tool["Tabela de dados"])

    if "Citas" in tab_by_tool:
        render_citations_tool(tab_by_tool["Citas"])

    if "Flashcards" in tab_by_tool:
        render_flashcards_tool(tab_by_tool["Flashcards"])

    if "Quiz" in tab_by_tool:
        render_quiz_tool(tab_by_tool["Quiz"])


def render_summary_tool(tab) -> None:
    with tab:
        topic = st.text_input("Topico para resumir", key="summary_topic_v2")
        if st.button("Gerar resumo", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                prompt = build_summary_prompt(topic, results, final_system_prompt())
                if should_use_real_model():
                    content = generate_response(prompt, current_llm_settings())
                else:
                    content = build_summary(topic, results)
                st.markdown(content)
                render_txt_download("Resumo", topic, content, results)
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(prompt, language="text")


def render_mind_map_tool(tab) -> None:
    with tab:
        topic = st.text_input("Tema do mapa mental", key="mind_map_topic_v2")
        if st.button("Gerar mapa mental", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                prompt = build_mind_map_prompt(topic, results, final_system_prompt())
                if should_use_real_model():
                    content = generate_response(prompt, current_llm_settings())
                else:
                    content = build_mind_map(topic, results)
                st.markdown(content)
                render_txt_download("Mapa mental", topic, content, results)
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(prompt, language="text")


def render_table_tool(tab) -> None:
    with tab:
        topic = st.text_input("Dados que deseja extrair", key="table_topic_v2")
        if st.button("Gerar tabela", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                prompt = build_table_prompt(topic, results, final_system_prompt())
                if should_use_real_model():
                    content = generate_response(prompt, current_llm_settings())
                    st.markdown(content)
                else:
                    content = build_data_table(topic, results)
                    st.dataframe(content, use_container_width=True, hide_index=True)
                render_txt_download("Tabela de dados", topic, content, results)
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(prompt, language="text")


def render_citations_tool(tab) -> None:
    with tab:
        topic = st.text_input("Tema para selecionar citas", key="citations_topic_v2")
        if st.button("Gerar citas", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                prompt = build_citations_prompt(topic, results, final_system_prompt())
                if should_use_real_model():
                    content = generate_response(prompt, current_llm_settings())
                else:
                    content = build_citations(topic, results)
                st.markdown(content)
                render_txt_download("Citas", topic, content, results)
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(prompt, language="text")


def render_flashcards_tool(tab) -> None:
    with tab:
        topic = st.text_input("Tema dos flashcards", key="flashcards_topic_v2")
        if st.button("Gerar flashcards", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                prompt = build_flashcards_prompt(topic, results, final_system_prompt())
                if should_use_real_model():
                    content = generate_response(prompt, current_llm_settings())
                    st.markdown(content)
                else:
                    content = build_flashcards(topic, results)
                    st.dataframe(content, use_container_width=True, hide_index=True)
                render_txt_download("Flashcards", topic, content, results)
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(prompt, language="text")


def render_quiz_tool(tab) -> None:
    with tab:
        topic = st.text_input("Tema do quiz", key="quiz_topic_v2")
        if st.button("Gerar quiz", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                prompt = build_quiz_prompt(topic, results, final_system_prompt())
                if should_use_real_model():
                    content = generate_response(prompt, current_llm_settings())
                else:
                    content = build_quiz(topic, results)
                st.markdown(content)
                render_txt_download("Quiz", topic, content, results)
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(prompt, language="text")


def render_txt_download(
    tool_name: str,
    topic: str,
    content,
    results: list[RetrievedChunk],
) -> None:
    st.download_button(
        f"Exportar {tool_name} TXT",
        data=build_tool_export(tool_name, topic, content, results),
        file_name=txt_filename(tool_name, topic),
        mime="text/plain",
        use_container_width=True,
    )
