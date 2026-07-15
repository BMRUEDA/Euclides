from __future__ import annotations

from models.source import DocumentChunk


def build_summary(topic: str, chunks: list[DocumentChunk]) -> str:
    if not chunks:
        return "Nenhum trecho encontrado para gerar resumo."

    return (
        f"Resumo simulado sobre: {topic}\n\n"
        f"Base inicial: {chunks[0].text[:900]}\n\n"
        "Proxima fase: gerar resumo real com uma LLM."
    )


def build_mind_map(topic: str, chunks: list[DocumentChunk]) -> str:
    source_hint = chunks[0].source_name if chunks else "sem fonte"
    return (
        f"- {topic}\n"
        f"  - Conceitos principais\n"
        f"  - Evidencias encontradas\n"
        f"  - Fonte inicial: {source_hint}\n"
        f"  - Conclusoes"
    )


def build_data_table(topic: str, chunks: list[DocumentChunk]) -> list[dict[str, str]]:
    if not chunks:
        return []

    return [
        {
            "Documento": chunk.source_name,
            "Pagina": str(chunk.page_number),
            "Campo": topic,
            "Trecho": chunk.text[:240],
        }
        for chunk in chunks
    ]

