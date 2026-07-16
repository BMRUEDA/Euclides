from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from components.chat import render_chat
from components.retrieval_preview import render_retrieval_preview
from components.sidebar import DEFAULT_SYSTEM_PROMPT, render_configuration_sidebar, render_sidebar
from components.source_diagnostics import render_source_diagnostics
from components.study_tools import render_study_tools
from services.llm_service import DEFAULT_GEMINI_MODEL


def init_state() -> None:
    st.session_state.setdefault("sources", [])
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("model_provider", "Placeholder")
    st.session_state.setdefault("model_name", DEFAULT_GEMINI_MODEL)
    st.session_state.setdefault("temperature", 0.2)
    st.session_state.setdefault("max_tokens", 1200)
    st.session_state.setdefault("retrieval_k", 5)
    st.session_state.setdefault("teaching_mode", "Tutor socratico")
    st.session_state.setdefault("show_reasoning", False)
    st.session_state.setdefault("citation_style", "Arquivo + pagina")
    st.session_state.setdefault("answer_strategy", "Responder somente com as fontes")
    st.session_state.setdefault("active_tools", ["Chat", "Resumo", "Mapa mental", "Tabela de dados"])
    st.session_state.setdefault("base_system_prompt", DEFAULT_SYSTEM_PROMPT)


def main() -> None:
    st.set_page_config(page_title="Euclides v2", page_icon="E", layout="wide")
    init_state()

    render_sidebar()
    render_configuration_sidebar()

    st.title("Euclides v2")
    st.caption("Versao separada para evoluir PDF, busca, chat e ferramentas em fases.")

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        render_chat()
    with right:
        render_source_diagnostics()
        render_retrieval_preview()
        render_study_tools()


if __name__ == "__main__":
    main()
