from __future__ import annotations

from models.source import RetrievedChunk
from services.context_builder import (
    DEFAULT_CONTEXT_SYSTEM_PROMPT,
    build_context_block,
    build_sources_summary,
)


def build_tool_prompt(
    tool_name: str,
    instruction: str,
    topic: str,
    results: list[RetrievedChunk],
    system_prompt: str | None = None,
) -> str:
    prompt_base = (system_prompt or DEFAULT_CONTEXT_SYSTEM_PROMPT).strip()
    return (
        f"{prompt_base}\n\n"
        f"Ferramenta solicitada: {tool_name}.\n"
        "Use somente os trechos recuperados dos PDFs.\n"
        "Inclua citacoes no formato (arquivo, p. numero) em cada informacao baseada nas fontes.\n"
        "Se o contexto for insuficiente, escreva claramente: "
        "'Nao encontrei essa informacao nos PDFs carregados.'\n"
        "Nao invente dados, secoes, autores, conclusoes ou relacoes que nao aparecam no contexto.\n\n"
        f"Pedido do usuario:\n{topic}\n\n"
        f"Instrucao da ferramenta:\n{instruction}\n\n"
        f"Contexto recuperado:\n{build_context_block(results)}\n\n"
        "Saida:"
    )


def build_summary(topic: str, results: list[RetrievedChunk]) -> str:
    if not results:
        return "Nenhum trecho encontrado para gerar resumo."

    sources = build_sources_summary(results)
    evidence_items = []
    for index, result in enumerate(results[:3], start=1):
        chunk = result.chunk
        evidence_items.append(
            f"{index}. {chunk.text[:420]} ({chunk.source_name}, p. {chunk.page_number})"
        )

    return (
        f"### Resumo simulado: {topic}\n\n"
        "**Ideia central:**\n"
        "Os trechos recuperados indicam que este topico aparece nas fontes carregadas, "
        "mas a sintese final ainda sera gerada por uma LLM na proxima etapa.\n\n"
        "**Evidencias recuperadas:**\n"
        + "\n".join(evidence_items)
        + "\n\n"
        f"**Fontes usadas:** {sources}"
    )


def build_mind_map(topic: str, results: list[RetrievedChunk]) -> str:
    if not results:
        return "Nenhum trecho encontrado para gerar mapa mental."

    sources = build_sources_summary(results)
    branches = []
    for result in results[:4]:
        chunk = result.chunk
        terms = ", ".join(result.matched_terms) or "trecho recuperado"
        branches.append(
            f"  - {terms}\n"
            f"    - Evidencia: {chunk.text[:260]}\n"
            f"    - Fonte: {chunk.source_name}, p. {chunk.page_number}"
        )

    return (
        f"### Mapa mental simulado: {topic}\n\n"
        f"- {topic}\n"
        + "\n".join(branches)
        + "\n"
        "  - Sintese final\n"
        "    - A organizacao final sera refinada por uma LLM na proxima etapa.\n\n"
        f"**Fontes usadas:** {sources}"
    )


def build_data_table(topic: str, results: list[RetrievedChunk]) -> list[dict[str, str]]:
    if not results:
        return []

    return [
        {
            "Documento": result.chunk.source_name,
            "Pagina": str(result.chunk.page_number),
            "Campo": topic,
            "Score": f"{result.score:.2f}",
            "Termos": ", ".join(result.matched_terms),
            "Trecho": result.chunk.text[:260],
        }
        for result in results
    ]


def build_citations(topic: str, results: list[RetrievedChunk]) -> str:
    if not results:
        return "Nenhum trecho encontrado para listar citacoes."

    items = []
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        items.append(
            f"{index}. \"{chunk.text[:360]}\" "
            f"({chunk.source_name}, p. {chunk.page_number})"
        )

    return (
        f"### Citas simuladas: {topic}\n\n"
        + "\n\n".join(items)
        + "\n\n"
        f"**Fontes usadas:** {build_sources_summary(results)}"
    )


def build_flashcards(topic: str, results: list[RetrievedChunk]) -> list[dict[str, str]]:
    if not results:
        return []

    cards = []
    for index, result in enumerate(results[:6], start=1):
        chunk = result.chunk
        terms = ", ".join(result.matched_terms) or topic
        cards.append(
            {
                "Frente": f"{index}. O que o documento indica sobre {terms}?",
                "Verso": (
                    f"{chunk.text[:320]} "
                    f"({chunk.source_name}, p. {chunk.page_number})"
                ),
            }
        )

    return cards


def build_quiz(topic: str, results: list[RetrievedChunk]) -> str:
    if not results:
        return "Nenhum trecho encontrado para gerar quiz."

    questions = []
    for index, result in enumerate(results[:5], start=1):
        chunk = result.chunk
        terms = ", ".join(result.matched_terms) or topic
        questions.append(
            f"{index}. Explique, com base na fonte, como o trecho se relaciona com "
            f"`{terms}`.\n"
            f"   - Gabarito esperado: mencionar a evidencia em "
            f"({chunk.source_name}, p. {chunk.page_number}).\n"
            f"   - Evidencia: {chunk.text[:260]}"
        )

    return (
        f"### Quiz simulado: {topic}\n\n"
        + "\n\n".join(questions)
        + "\n\n"
        f"**Fontes usadas:** {build_sources_summary(results)}"
    )


def build_table_prompt(
    topic: str,
    results: list[RetrievedChunk],
    system_prompt: str | None = None,
) -> str:
    return build_tool_prompt(
        tool_name="Tabela de dados",
        instruction=(
            "Extraia campos relevantes em uma tabela Markdown. Cada linha deve conter "
            "documento, pagina, campo, valor extraido, citacao e observacao quando houver incerteza. "
            "Use 'Nao encontrado nos PDFs' quando um campo nao aparecer no contexto."
        ),
        topic=topic,
        results=results,
        system_prompt=system_prompt,
    )


def build_citations_prompt(
    topic: str,
    results: list[RetrievedChunk],
    system_prompt: str | None = None,
) -> str:
    return build_tool_prompt(
        tool_name="Citas",
        instruction=(
            "Selecione as citacoes mais uteis para estudo academico. Para cada uma, "
            "inclua citacao curta, documento, pagina, motivo de relevancia e limite de uso."
        ),
        topic=topic,
        results=results,
        system_prompt=system_prompt,
    )


def build_flashcards_prompt(
    topic: str,
    results: list[RetrievedChunk],
    system_prompt: str | None = None,
) -> str:
    return build_tool_prompt(
        tool_name="Flashcards",
        instruction=(
            "Crie flashcards em Markdown com frente e verso. Cada verso deve ser curto, "
            "baseado no contexto e conter citacao da fonte."
        ),
        topic=topic,
        results=results,
        system_prompt=system_prompt,
    )


def build_quiz_prompt(
    topic: str,
    results: list[RetrievedChunk],
    system_prompt: str | None = None,
) -> str:
    return build_tool_prompt(
        tool_name="Quiz",
        instruction=(
            "Crie um quiz curto com perguntas, alternativas quando couber, resposta correta "
            "e justificativa citada. Nao use conhecimento fora dos trechos recuperados."
        ),
        topic=topic,
        results=results,
        system_prompt=system_prompt,
    )


def build_summary_prompt(
    topic: str,
    results: list[RetrievedChunk],
    system_prompt: str | None = None,
) -> str:
    return build_tool_prompt(
        tool_name="Resumo",
        instruction=(
            "Produza um resumo academico curto em Markdown, organizado em: "
            "ideia central, pontos principais, evidencias e limites do contexto."
        ),
        topic=topic,
        results=results,
        system_prompt=system_prompt,
    )


def build_mind_map_prompt(
    topic: str,
    results: list[RetrievedChunk],
    system_prompt: str | None = None,
) -> str:
    return build_tool_prompt(
        tool_name="Mapa mental",
        instruction=(
            "Organize o tema em uma estrutura hierarquica em Markdown com conceito central, "
            "ramos principais, evidencias citadas e limites do contexto."
        ),
        topic=topic,
        results=results,
        system_prompt=system_prompt,
    )
