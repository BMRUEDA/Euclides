from __future__ import annotations

import streamlit as st

from services.pdf_loader import extract_pdf_chunks
from services.retrieval import retrieve_relevant_chunks
from services.tool_service import build_data_table, build_mind_map, build_summary


def render_study_tools() -> None:
    st.subheader("Ferramentas de estudo")

    tab_summary, tab_map, tab_table = st.tabs(["Resumo", "Mapa mental", "Tabela de dados"])

    with tab_summary:
        topic = st.text_input("Topico para resumir", key="summary_topic_v2")
        if st.button("Gerar resumo", use_container_width=True):
            chunks = retrieve_relevant_chunks(topic, extract_pdf_chunks(st.session_state.sources))
            st.write(build_summary(topic, chunks))

    with tab_map:
        topic = st.text_input("Tema do mapa mental", key="mind_map_topic_v2")
        if st.button("Gerar mapa mental", use_container_width=True):
            chunks = retrieve_relevant_chunks(topic, extract_pdf_chunks(st.session_state.sources))
            st.markdown(build_mind_map(topic, chunks))

    with tab_table:
        topic = st.text_input("Dados que deseja extrair", key="table_topic_v2")
        if st.button("Gerar tabela", use_container_width=True):
            chunks = retrieve_relevant_chunks(topic, extract_pdf_chunks(st.session_state.sources))
            rows = build_data_table(topic, chunks)
            if rows:
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum dado encontrado.")

