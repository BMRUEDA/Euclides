from __future__ import annotations

from models.source import DocumentChunk, RetrievedChunk
from services.embedding_service import EmbeddingError, cosine_similarity, embed_document, embed_query
from services.retrieval import retrieve_ranked_chunks, tokenize


LEXICAL_MODE = "Lexical"
VECTOR_MODE = "Vetorial"
HYBRID_MODE = "Hibrida"


def retrieve_chunks(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
    mode: str = LEXICAL_MODE,
) -> list[RetrievedChunk]:
    if mode == VECTOR_MODE:
        return semantic_retrieve_with_fallback(query, chunks, limit)

    if mode == HYBRID_MODE:
        return hybrid_retrieve(query, chunks, limit)

    return retrieve_ranked_chunks(query=query, chunks=chunks, limit=limit)


def semantic_retrieve_with_fallback(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> list[RetrievedChunk]:
    try:
        return semantic_retrieve(query, chunks, limit)
    except EmbeddingError:
        return retrieve_ranked_chunks(query=query, chunks=chunks, limit=limit)


def semantic_retrieve(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> list[RetrievedChunk]:
    if not query.strip() or not chunks:
        return []

    query_embedding = embed_query(query)
    results: list[RetrievedChunk] = []

    for chunk in chunks:
        document_embedding = embed_document(chunk.text)
        similarity = cosine_similarity(query_embedding, document_embedding)
        if similarity <= 0:
            continue

        results.append(
            RetrievedChunk(
                chunk=chunk,
                score=similarity,
                matched_terms=["semantic"],
            )
        )

    results.sort(key=lambda result: (-result.score, len(result.chunk.text)))
    return results[:limit]


def hybrid_retrieve(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> list[RetrievedChunk]:
    lexical_results = retrieve_ranked_chunks(query=query, chunks=chunks, limit=limit * 2)

    try:
        semantic_results = semantic_retrieve(query, chunks, limit * 2)
    except EmbeddingError:
        return lexical_results[:limit]

    lexical_max = max((result.score for result in lexical_results), default=1.0)
    combined: dict[tuple[str, int, str], RetrievedChunk] = {}

    for result in semantic_results:
        key = chunk_key(result.chunk)
        combined[key] = RetrievedChunk(
            chunk=result.chunk,
            score=result.score * 0.65,
            matched_terms=["semantic"],
        )

    for result in lexical_results:
        key = chunk_key(result.chunk)
        lexical_score = (result.score / lexical_max) * 0.35 if lexical_max else 0.0
        existing = combined.get(key)
        if existing:
            combined[key] = RetrievedChunk(
                chunk=result.chunk,
                score=existing.score + lexical_score,
                matched_terms=merge_terms(existing.matched_terms, result.matched_terms),
            )
        else:
            combined[key] = RetrievedChunk(
                chunk=result.chunk,
                score=lexical_score,
                matched_terms=result.matched_terms or tokenize(query),
            )

    results = list(combined.values())
    results.sort(key=lambda result: (-result.score, len(result.chunk.text)))
    return results[:limit]


def chunk_key(chunk: DocumentChunk) -> tuple[str, int, str]:
    return (chunk.source_name, chunk.page_number, chunk.text)


def merge_terms(left: list[str], right: list[str]) -> list[str]:
    seen = set()
    merged: list[str] = []
    for term in [*left, *right]:
        if term not in seen:
            merged.append(term)
            seen.add(term)
    return merged
