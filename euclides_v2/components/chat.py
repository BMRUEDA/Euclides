from __future__ import annotations

import streamlit as st

from components.sidebar import current_llm_settings, final_system_prompt
from services.llm_service import answer_with_context
from services.pdf_loader import load_pdf_corpus
from services.vector_retrieval import retrieve_chunks_with_status


def render_chat() -> None:
    st.subheader("Chat com os artigos")
    st.caption(
        f"Modelo: {st.session_state.model_provider} / {st.session_state.model_name} | "
        f"Modo: {st.session_state.teaching_mode}"
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Pergunte algo sobre os documentos...")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})

    corpus = load_pdf_corpus(st.session_state.sources)
    if not corpus.has_sources:
        answer = "Carregue pelo menos um PDF antes de perguntar sobre os documentos."
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    if not corpus.has_text:
        answer = (
            "Nao encontrei texto extraivel nos PDFs carregados. "
            "Verifique o Diagnostico das fontes; talvez o PDF seja escaneado ou imagem."
        )
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    retrieval_result = retrieve_chunks_with_status(
        query=prompt,
        chunks=corpus.chunks,
        limit=st.session_state.retrieval_k,
        mode=st.session_state.retrieval_mode,
    )
    answer = answer_with_context(
        question=prompt,
        retrieved_chunks=retrieval_result.chunks,
        system_prompt=final_system_prompt(),
        settings=current_llm_settings(),
    )
    if retrieval_result.warning:
        answer = f"{retrieval_result.warning}\n\n{answer}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
