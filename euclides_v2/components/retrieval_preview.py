from __future__ import annotations

import streamlit as st

from services.pdf_loader import load_pdf_corpus
from services.vector_retrieval import retrieve_chunks_with_status


def render_retrieval_preview() -> None:
    st.subheader("Teste de busca")

    with st.expander("Buscar trechos nos PDFs", expanded=False):
        st.caption(
            "A busca pode usar modo lexical, vetorial ou hibrido, conforme a configuracao da sidebar."
        )
        query = st.text_input(
            "Consulta de teste",
            placeholder="Ex.: metodologia, resultados, amostra",
            key="retrieval_preview_query",
        )

        if not st.button("Buscar trechos", use_container_width=True):
            return

        if not query.strip():
            st.warning("Informe uma consulta para testar a busca.")
            return

        corpus = load_pdf_corpus(st.session_state.sources)
        if not corpus.has_sources:
            st.warning("Carregue pelo menos um PDF antes de testar a busca.")
            return

        if not corpus.has_text:
            st.warning("Nao ha texto extraivel para buscar.")
            return

        retrieval_result = retrieve_chunks_with_status(
            query=query,
            chunks=corpus.chunks,
            limit=st.session_state.retrieval_k,
            mode=st.session_state.retrieval_mode,
        )
        results = retrieval_result.chunks

        if retrieval_result.warning:
            st.warning(retrieval_result.warning)
        else:
            st.caption(f"Modo efetivo: {retrieval_result.effective_mode}")

        if not results:
            st.warning("Nenhum trecho encontrado para essa consulta.")
            return

        for index, result in enumerate(results, start=1):
            chunk = result.chunk
            st.write(
                f"**{index}. {chunk.source_name}, pagina {chunk.page_number}** "
                f"- score {result.score:.2f}"
            )
            if result.matched_terms:
                st.caption(f"Termos encontrados: {', '.join(result.matched_terms)}")
            st.write(chunk.text[:900])
