from __future__ import annotations

from models.source import RetrievedChunk
from services.context_builder import build_context_prompt, build_sources_summary


def answer_with_context(question: str, retrieved_chunks: list[RetrievedChunk]) -> str:
    if not retrieved_chunks:
        return (
            "Nao encontrei trechos relevantes nos PDFs carregados. "
            "Tente reformular a pergunta ou carregar documentos com texto extraivel."
        )

    context_prompt = build_context_prompt(question, retrieved_chunks)
    sources = build_sources_summary(retrieved_chunks)
    best_result = retrieved_chunks[0]
    best_chunk = best_result.chunk

    return (
        "Resposta simulada baseada nos trechos recuperados.\n\n"
        f"Pergunta: {question}\n\n"
        "Sintese preliminar:\n"
        f"O trecho mais relevante encontrado esta em {best_chunk.source_name}, "
        f"pagina {best_chunk.page_number}. Ele parece relacionado a pergunta porque "
        f"contem os termos: {', '.join(best_result.matched_terms) or 'consulta ampla'}.\n\n"
        "Evidencia principal:\n"
        f"{best_chunk.text[:900]}\n\n"
        f"Fontes usadas: {sources}\n\n"
        "Prompt que sera enviado ao modelo na proxima etapa:\n"
        "```text\n"
        f"{context_prompt}\n"
        "```\n\n"
        "Observacao: esta resposta ainda e simulada. A estrutura de contexto ja esta pronta "
        "para substituir esta funcao por uma chamada real a Ollama, OpenAI ou Gemini."
    )
