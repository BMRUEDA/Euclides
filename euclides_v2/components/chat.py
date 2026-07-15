from __future__ import annotations

import streamlit as st

from services.llm_service import answer_with_context
from services.pdf_loader import extract_pdf_chunks
from services.retrieval import retrieve_relevant_chunks


def render_chat() -> None:
    st.subheader("Chat com os artigos")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Pergunte algo sobre os documentos...")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})

    chunks = extract_pdf_chunks(st.session_state.sources)
    relevant_chunks = retrieve_relevant_chunks(prompt, chunks)
    answer = answer_with_context(prompt, relevant_chunks)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

