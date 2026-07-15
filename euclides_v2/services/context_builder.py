from __future__ import annotations

from models.source import RetrievedChunk


MAX_CONTEXT_CHARS_PER_CHUNK = 1200


def format_citation(result: RetrievedChunk) -> str:
    chunk = result.chunk
    return f"{chunk.source_name}, p. {chunk.page_number}"


def build_context_block(results: list[RetrievedChunk]) -> str:
    if not results:
        return "Nenhum trecho relevante foi recuperado."

    context_parts: list[str] = []
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        excerpt = chunk.text[:MAX_CONTEXT_CHARS_PER_CHUNK]
        context_parts.append(
            "\n".join(
                [
                    f"[Fonte {index}] {format_citation(result)}",
                    f"Score: {result.score:.2f}",
                    f"Termos encontrados: {', '.join(result.matched_terms) or 'consulta ampla'}",
                    f"Trecho: {excerpt}",
                ]
            )
        )

    return "\n\n".join(context_parts)


def build_context_prompt(question: str, results: list[RetrievedChunk]) -> str:
    context_block = build_context_block(results)
    return (
        "Voce e o Euclides, um assistente de estudo academico.\n"
        "Responda somente com base nos trechos recuperados dos PDFs.\n"
        "Quando usar uma informacao, mencione a fonte no formato arquivo, pagina.\n"
        "Se os trechos nao forem suficientes, diga isso claramente.\n\n"
        f"Pergunta do usuario:\n{question}\n\n"
        f"Contexto recuperado:\n{context_block}\n\n"
        "Resposta:"
    )


def build_sources_summary(results: list[RetrievedChunk]) -> str:
    if not results:
        return "Nenhuma fonte consultada."

    citations = []
    seen = set()
    for result in results:
        citation = format_citation(result)
        if citation not in seen:
            citations.append(citation)
            seen.add(citation)

    return "; ".join(citations)
