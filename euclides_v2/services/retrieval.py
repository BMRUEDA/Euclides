from __future__ import annotations

from collections import Counter
import re
import unicodedata

from models.source import DocumentChunk, RetrievedChunk


STOPWORDS = {
    "a",
    "as",
    "ao",
    "aos",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "ou",
    "para",
    "por",
    "que",
    "um",
    "uma",
}

BILINGUAL_TERMS = {
    "amostra": ["sample"],
    "analise": ["analysis"],
    "artigo": ["article", "paper"],
    "autor": ["author"],
    "autores": ["authors"],
    "conclusao": ["conclusion"],
    "dados": ["data"],
    "discussao": ["discussion"],
    "estudo": ["study"],
    "experimento": ["experiment"],
    "hipotese": ["hypothesis"],
    "introducao": ["introduction"],
    "metodo": ["method"],
    "metodos": ["methods"],
    "metodologia": ["methodology", "methods"],
    "objetivo": ["objective", "aim", "goal"],
    "objetivos": ["objectives", "aims", "goals"],
    "participantes": ["participants"],
    "pesquisa": ["research"],
    "resultado": ["result"],
    "resultados": ["results", "findings"],
    "revisao": ["review"],
    "tabela": ["table"],
    "variavel": ["variable"],
    "variaveis": ["variables"],
}


def normalize_text(value: str) -> str:
    without_accents = unicodedata.normalize("NFKD", value)
    ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def tokenize(value: str) -> list[str]:
    normalized = normalize_text(value)
    terms = re.findall(r"[a-z0-9]{3,}", normalized)
    return [term for term in terms if term not in STOPWORDS]


def expand_query_terms(query_terms: list[str]) -> list[str]:
    expanded_terms: list[str] = []
    seen = set()

    for term in query_terms:
        candidates = [term, *BILINGUAL_TERMS.get(term, [])]
        for candidate in candidates:
            normalized_candidate = normalize_text(candidate)
            if normalized_candidate not in seen:
                expanded_terms.append(normalized_candidate)
                seen.add(normalized_candidate)

    return expanded_terms


def score_chunk(query_terms: list[str], chunk: DocumentChunk) -> RetrievedChunk | None:
    chunk_term_counts = Counter(tokenize(chunk.text))
    matched_terms: list[str] = []
    score = 0.0

    for term in query_terms:
        frequency = chunk_term_counts[term]
        if frequency <= 0:
            continue

        matched_terms.append(term)
        score += 1.0 + min(frequency, 6) * 0.25

    if not matched_terms:
        return None

    coverage = len(set(matched_terms)) / max(len(set(query_terms)), 1)
    score += coverage * 2.0

    return RetrievedChunk(
        chunk=chunk,
        score=score,
        matched_terms=sorted(set(matched_terms)),
    )


def retrieve_relevant_chunks(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> list[DocumentChunk]:
    return [
        result.chunk
        for result in retrieve_ranked_chunks(query=query, chunks=chunks, limit=limit)
    ]


def retrieve_ranked_chunks(
    query: str,
    chunks: list[DocumentChunk],
    limit: int = 5,
) -> list[RetrievedChunk]:
    query_terms = expand_query_terms(tokenize(query))

    if not query_terms:
        return [
            RetrievedChunk(chunk=chunk, score=0.0, matched_terms=[])
            for chunk in chunks[:limit]
        ]

    ranked_chunks: list[RetrievedChunk] = []
    for chunk in chunks:
        result = score_chunk(query_terms, chunk)
        if result:
            ranked_chunks.append(result)

    ranked_chunks.sort(
        key=lambda result: (
            -result.score,
            len(result.chunk.text),
        ),
    )
    return ranked_chunks[:limit]
