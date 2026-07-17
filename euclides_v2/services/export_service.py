from __future__ import annotations

from datetime import datetime
import re
from typing import Mapping, Sequence

from models.source import RetrievedChunk
from services.context_builder import build_sources_summary


def timestamp_label() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def filename_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def safe_filename(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    normalized = normalized.strip("-")
    return normalized or "exportacao"


def txt_filename(prefix: str, topic: str = "") -> str:
    parts = [safe_filename(prefix)]
    if topic.strip():
        parts.append(safe_filename(topic)[:48])
    parts.append(filename_timestamp())
    return "-".join(parts) + ".txt"


def build_chat_export(messages: list[dict[str, str]]) -> str:
    lines = [
        "Euclides v2 - Chat exportado",
        f"Data: {timestamp_label()}",
        "",
    ]

    if not messages:
        lines.append("Nenhuma mensagem no chat.")
        return "\n".join(lines)

    for index, message in enumerate(messages, start=1):
        role = "Usuario" if message.get("role") == "user" else "Euclides"
        lines.extend(
            [
                f"[{index}] {role}",
                str(message.get("content", "")).strip(),
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def build_tool_export(
    tool_name: str,
    topic: str,
    content: str | Sequence[Mapping[str, str]],
    results: list[RetrievedChunk] | None = None,
) -> str:
    lines = [
        f"Euclides v2 - {tool_name}",
        f"Data: {timestamp_label()}",
        f"Topico: {topic.strip() or 'Nao informado'}",
        "",
        "Conteudo",
        "--------",
        format_content(content),
        "",
    ]

    if results:
        lines.extend(
            [
                "Fontes usadas",
                "-------------",
                build_sources_summary(results),
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def format_content(content: str | Sequence[Mapping[str, str]]) -> str:
    if isinstance(content, str):
        return content.strip()

    if not content:
        return "Sem dados para exportar."

    blocks: list[str] = []
    for index, row in enumerate(content, start=1):
        row_lines = [f"{index}."]
        for key, value in row.items():
            row_lines.append(f"{key}: {value}")
        blocks.append("\n".join(row_lines))

    return "\n\n".join(blocks)
