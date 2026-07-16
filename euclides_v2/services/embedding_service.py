from __future__ import annotations

import json
import math
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import streamlit as st


DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"
REQUEST_TIMEOUT_SECONDS = 60


class EmbeddingError(RuntimeError):
    pass


@st.cache_data(show_spinner=False)
def embed_text(
    text: str,
    task_type: str,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[float]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise EmbeddingError("GEMINI_API_KEY nao esta configurada.")

    url = EMBEDDING_API_URL.format(model=quote(model_name, safe=""))
    payload = {
        "taskType": task_type,
        "content": {
            "parts": [{"text": text}],
        },
    }
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise EmbeddingError(format_embedding_http_error(exc)) from exc
    except URLError as exc:
        raise EmbeddingError(f"Nao foi possivel conectar ao Gemini Embeddings: {exc.reason}") from exc
    except TimeoutError as exc:
        raise EmbeddingError("A chamada de embeddings excedeu o tempo limite.") from exc

    return extract_embedding_values(data)


def embed_query(query: str) -> list[float]:
    return embed_text(query, task_type="RETRIEVAL_QUERY")


def embed_document(text: str) -> list[float]:
    return embed_text(text, task_type="RETRIEVAL_DOCUMENT")


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0

    dot_product = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    return dot_product / (left_norm * right_norm)


def extract_embedding_values(data: dict) -> list[float]:
    embedding = data.get("embedding") or {}
    values = embedding.get("values")
    if isinstance(values, list):
        return [float(value) for value in values]

    embeddings = data.get("embeddings") or []
    if embeddings and isinstance(embeddings[0].get("values"), list):
        return [float(value) for value in embeddings[0]["values"]]

    raise EmbeddingError("A resposta de embeddings nao trouxe um vetor valido.")


def format_embedding_http_error(exc: HTTPError) -> str:
    try:
        body = json.loads(exc.read().decode("utf-8"))
        message = body.get("error", {}).get("message")
    except Exception:
        message = None

    if exc.code == 401 or exc.code == 403:
        return f"Chave do Gemini invalida ou sem permissao para embeddings. {message or ''}".strip()
    if exc.code == 404:
        return f"Modelo de embeddings nao encontrado. {message or ''}".strip()
    if exc.code == 429:
        return f"Limite gratuito ou rate limit de embeddings atingido. {message or ''}".strip()

    return f"Erro HTTP em embeddings ({exc.code}). {message or exc.reason}"
