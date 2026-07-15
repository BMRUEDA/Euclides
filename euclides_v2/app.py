from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from components.chat import render_chat
from components.sidebar import render_sidebar
from components.study_tools import render_study_tools


def init_state() -> None:
    st.session_state.setdefault("sources", [])
    st.session_state.setdefault("messages", [])


def main() -> None:
    st.set_page_config(page_title="Euclides v2", page_icon="E", layout="wide")
    init_state()

    render_sidebar()

    st.title("Euclides v2")
    st.caption("Versao separada para evoluir PDF, busca, chat e ferramentas em fases.")

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        render_chat()
    with right:
        render_study_tools()


if __name__ == "__main__":
    main()

