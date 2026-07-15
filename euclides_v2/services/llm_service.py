from __future__ import annotations

from models.source import DocumentChunk


def answer_with_context(question: str, context_chunks: list[DocumentChunk]) -> str:
    if not context_chunks:
        return (
            "Nao encontrei trechos relevantes nos PDFs carregados. "
            "Tente reformular a pergunta ou carregar documentos com texto extraivel."
        )

    citations = ", ".join(
        f"{chunk.source_name}, p. {chunk.page_number}"
        for chunk in context_chunks
    )
    preview = context_chunks[0].text[:700]

    return (
        "Resposta simulada com contexto recuperado.\n\n"
        f"Pergunta: {question}\n\n"
        f"Trecho mais relevante: {preview}\n\n"
        f"Fontes consultadas: {citations}\n\n"
        "Proxima fase: substituir esta funcao por uma chamada real a uma LLM."
    )

