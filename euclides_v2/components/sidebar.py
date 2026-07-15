from __future__ import annotations

import streamlit as st

from models.source import SourceFile


MAX_SOURCES = 3


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


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

