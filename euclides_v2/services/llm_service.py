from __future__ import annotations

from dataclasses import dataclass
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from models.source import RetrievedChunk
from services.context_builder import build_context_prompt, build_sources_summary


DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
REQUEST_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class LlmSettings:
    provider: str
    model_name: str
    temperature: float
    max_tokens: int


def answer_with_context(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
    system_prompt: str | None = None,
    settings: LlmSettings | None = None,
) -> str:
    if not retrieved_chunks:
        return (
            "Nao encontrei trechos relevantes nos PDFs carregados. "
            "Tente reformular a pergunta ou carregar documentos com texto extraivel."
        )

    context_prompt = build_context_prompt(question, retrieved_chunks, system_prompt)

    if settings and settings.provider != "Placeholder":
        return generate_response(context_prompt, settings)

    return build_simulated_answer(question, retrieved_chunks, context_prompt)


def generate_response(prompt: str, settings: LlmSettings) -> str:
    provider = settings.provider.strip()
    if provider == "Gemini":
        return call_gemini(prompt, settings)

    if provider == "Placeholder":
        return (
            "O provedor Placeholder nao executa uma LLM real. "
            "Selecione Gemini e configure GEMINI_API_KEY para usar a Fase 5."
        )

    return f"O provedor {provider} ainda nao foi implementado nesta fase."


def call_gemini(prompt: str, settings: LlmSettings) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return (
            "Gemini ainda nao esta configurado.\n\n"
            "Defina a variavel de ambiente GEMINI_API_KEY e reinicie o Streamlit."
        )

    model_name = normalized_model_name(settings)
    url = f"{GEMINI_API_URL.format(model=quote(model_name, safe=''))}?key={quote(api_key, safe='')}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": settings.temperature,
            "maxOutputTokens": settings.max_tokens,
        },
    }
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return format_gemini_http_error(exc)
    except URLError as exc:
        return f"Nao foi possivel conectar ao Gemini: {exc.reason}"
    except TimeoutError:
        return "A chamada ao Gemini excedeu o tempo limite. Tente reduzir os trechos ou max tokens."
    except Exception as exc:
        return f"Erro inesperado ao chamar o Gemini: {exc}"

    return extract_gemini_text(data)


def normalized_model_name(settings: LlmSettings) -> str:
    model_name = settings.model_name.strip()
    if not model_name or model_name == "Modelo ainda nao conectado":
        return DEFAULT_GEMINI_MODEL
    return model_name


def extract_gemini_text(data: dict) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        prompt_feedback = data.get("promptFeedback") or {}
        block_reason = prompt_feedback.get("blockReason")
        if block_reason:
            return f"O Gemini bloqueou a resposta. Motivo: {block_reason}."
        return "O Gemini nao retornou uma resposta de texto."

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    if text_parts:
        return "\n".join(text_parts).strip()

    finish_reason = candidates[0].get("finishReason")
    if finish_reason:
        return f"O Gemini terminou sem texto. Motivo: {finish_reason}."

    return "O Gemini retornou uma resposta sem texto legivel."


def format_gemini_http_error(exc: HTTPError) -> str:
    try:
        body = json.loads(exc.read().decode("utf-8"))
        message = body.get("error", {}).get("message")
    except Exception:
        message = None

    if exc.code == 400:
        return f"Gemini rejeitou a requisicao. {message or 'Verifique o modelo e o prompt.'}"
    if exc.code == 401 or exc.code == 403:
        return f"Chave do Gemini invalida ou sem permissao. {message or ''}".strip()
    if exc.code == 404:
        return f"Modelo Gemini nao encontrado. {message or 'Verifique o nome do modelo.'}"
    if exc.code == 429:
        return f"Limite gratuito ou rate limit do Gemini atingido. {message or 'Tente novamente depois.'}"

    return f"Erro HTTP do Gemini ({exc.code}). {message or exc.reason}"


def build_simulated_answer(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
    context_prompt: str,
) -> str:
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
