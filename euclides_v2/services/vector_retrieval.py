from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from models.source import DocumentChunk, RetrievedChunk
from services.embedding_service import EmbeddingError, cosine_similarity, embed_document, embed_query
from services.retrieval import retrieve_ranked_chunks, tokenize


LEXICAL_MODE = "Lexical"
VECTOR_MODE = "Vetorial"
HYBRID_MODE = "Hibrida"
HYBRID_CANDIDATE_MULTIPLIER = 4
MIN_HYBRID_CANDIDATES = 12


@dataclass(frozen=True)
class VectorIndexItem:
    chunk: DocumentChunk
    embedding: tuple[float, ...]


@dataclass(frozen=True)
class VectorIndex:
    items: tuple[VectorIndexItem, ...]

    @property
    def is_empty(self) -> bool:
        return not self.items


@dataclass(frozen=True)
class RetrievalResult:
    chunks: list[RetrievedChunk]
    requested_mode: str
    effective_mode: str
    warning: str | None = None


def retrieve_chunks(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
    mode: str = LEXICAL_MODE,
) -> list[RetrievedChunk]:
    return retrieve_chunks_with_status(
        query=query,
        chunks=chunks,
        limit=limit,
        mode=mode,
    ).chunks


def retrieve_chunks_with_status(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
    mode: str = LEXICAL_MODE,
) -> RetrievalResult:
    if mode == VECTOR_MODE:
        return semantic_retrieve_with_fallback(query, chunks, limit)

    if mode == HYBRID_MODE:
        return hybrid_retrieve(query, chunks, limit)

    return RetrievalResult(
        chunks=retrieve_ranked_chunks(query=query, chunks=chunks, limit=limit),
        requested_mode=mode,
        effective_mode=LEXICAL_MODE,
    )


def semantic_retrieve_with_fallback(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> RetrievalResult:
    try:
        return RetrievalResult(
            chunks=semantic_retrieve(query, chunks, limit),
            requested_mode=VECTOR_MODE,
            effective_mode=VECTOR_MODE,
        )
    except EmbeddingError as exc:
        return RetrievalResult(
            chunks=retrieve_ranked_chunks(query=query, chunks=chunks, limit=limit),
            requested_mode=VECTOR_MODE,
            effective_mode=LEXICAL_MODE,
            warning=f"Busca vetorial indisponivel; usando busca lexical. Detalhe: {exc}",
        )


def semantic_retrieve(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> list[RetrievedChunk]:
    if not query.strip() or not chunks:
        return []

    query_embedding = embed_query(query)
    vector_index = build_vector_index(tuple(chunks))
    if vector_index.is_empty:
        return []

    results: list[RetrievedChunk] = []

    for item in vector_index.items:
        similarity = cosine_similarity(query_embedding, list(item.embedding))
        if similarity <= 0:
            continue

        results.append(
            RetrievedChunk(
                chunk=item.chunk,
                score=similarity,
                matched_terms=["semantic"],
            )
        )

    results.sort(key=lambda result: (-result.score, len(result.chunk.text)))
    return results[:limit]


@st.cache_data(show_spinner=False)
def build_vector_index(chunks: tuple[DocumentChunk, ...]) -> VectorIndex:
    items: list[VectorIndexItem] = []

    for chunk in chunks:
        embedding = embed_document(chunk.text)
        items.append(
            VectorIndexItem(
                chunk=chunk,
                embedding=tuple(embedding),
            )
        )

    return VectorIndex(items=tuple(items))


def hybrid_retrieve(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> RetrievalResult:
    candidate_limit = max(limit * HYBRID_CANDIDATE_MULTIPLIER, MIN_HYBRID_CANDIDATES)
    lexical_results = retrieve_ranked_chunks(query=query, chunks=chunks, limit=candidate_limit)
    candidate_chunks = [result.chunk for result in lexical_results]

    if not candidate_chunks:
        semantic_result = semantic_retrieve_with_fallback(query, chunks, limit)
        return RetrievalResult(
            chunks=semantic_result.chunks,
            requested_mode=HYBRID_MODE,
            effective_mode=semantic_result.effective_mode,
            warning=semantic_result.warning,
        )

    try:
        semantic_results = semantic_retrieve(query, candidate_chunks, candidate_limit)
    except EmbeddingError as exc:
        return RetrievalResult(
            chunks=lexical_results[:limit],
            requested_mode=HYBRID_MODE,
            effective_mode=LEXICAL_MODE,
            warning=f"Busca hibrida indisponivel; usando busca lexical. Detalhe: {exc}",
        )

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
    return RetrievalResult(
        chunks=results[:limit],
        requested_mode=HYBRID_MODE,
        effective_mode=HYBRID_MODE,
    )


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
