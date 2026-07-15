from __future__ import annotations

import streamlit as st

from services.pdf_loader import load_pdf_corpus


def render_source_diagnostics() -> None:
    st.subheader("Diagnostico das fontes")

    if not st.session_state.sources:
        st.info("Carregue um PDF para verificar se o texto pode ser extraido.")
        return

    corpus = load_pdf_corpus(st.session_state.sources)

    total_pages = sum(diagnostic.page_count for diagnostic in corpus.diagnostics)
    extracted_pages = sum(diagnostic.extracted_pages for diagnostic in corpus.diagnostics)
    st.caption(
        f"{len(corpus.diagnostics)} fonte(s), {total_pages} pagina(s), "
        f"{extracted_pages} pagina(s) com texto."
    )

    with st.expander("Preview do texto extraido", expanded=False):
        for diagnostic in corpus.diagnostics:

            st.write(f"**{diagnostic.source_name}**")

            if diagnostic.error:
                st.error(diagnostic.error)
                continue

            col_pages, col_text, col_chunks = st.columns(3)
            col_pages.metric("Paginas", diagnostic.page_count)
            col_text.metric("Paginas com texto", diagnostic.extracted_pages)
            col_chunks.metric("Trechos", diagnostic.chunk_count)

            if not diagnostic.has_text:
                st.warning(
                    "Nenhum texto extraivel foi encontrado. "
                    "Este PDF pode ser escaneado ou composto por imagens."
                )
                continue

            st.text_area(
                "Amostra extraida",
                diagnostic.preview,
                height=180,
                key=f"preview-{diagnostic.source_name}",
                disabled=True,
            )
