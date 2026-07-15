from __future__ import annotations

import streamlit as st

from models.source import RetrievedChunk
from services.pdf_loader import load_pdf_corpus
from services.retrieval import retrieve_ranked_chunks
from services.tool_service import (
    build_data_table,
    build_mind_map,
    build_mind_map_prompt,
    build_summary,
    build_summary_prompt,
    build_table_prompt,
)


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

    results = retrieve_ranked_chunks(
        query=topic,
        chunks=corpus.chunks,
        limit=st.session_state.retrieval_k,
    )
    if not results:
        st.warning("Nenhum trecho relevante foi encontrado para esse topico.")
        return None

    return results


def render_study_tools() -> None:
    st.subheader("Ferramentas de estudo")

    tab_summary, tab_map, tab_table = st.tabs(["Resumo", "Mapa mental", "Tabela de dados"])

    with tab_summary:
        topic = st.text_input("Topico para resumir", key="summary_topic_v2")
        if st.button("Gerar resumo", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                st.markdown(build_summary(topic, results))
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(build_summary_prompt(topic, results), language="text")

    with tab_map:
        topic = st.text_input("Tema do mapa mental", key="mind_map_topic_v2")
        if st.button("Gerar mapa mental", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                st.markdown(build_mind_map(topic, results))
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(build_mind_map_prompt(topic, results), language="text")

    with tab_table:
        topic = st.text_input("Dados que deseja extrair", key="table_topic_v2")
        if st.button("Gerar tabela", use_container_width=True):
            results = get_relevant_results_or_warn(topic)
            if results:
                rows = build_data_table(topic, results)
                st.dataframe(rows, use_container_width=True, hide_index=True)
                with st.expander("Prompt preparado para a LLM", expanded=False):
                    st.code(build_table_prompt(topic, results), language="text")
