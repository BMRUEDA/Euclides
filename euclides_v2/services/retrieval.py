from __future__ import annotations

from models.source import DocumentChunk


def retrieve_relevant_chunks(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> list[DocumentChunk]:
    query_terms = {
        term.lower()
        for term in query.split()
        if len(term.strip()) >= 3
    }

    if not query_terms:
        return chunks[:limit]

    scored_chunks: list[tuple[int, DocumentChunk]] = []
    for chunk in chunks:
        text = chunk.text.lower()
        score = sum(1 for term in query_terms if term in text)
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored_chunks[:limit]]

