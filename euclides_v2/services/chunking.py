from __future__ import annotations


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 180


def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []

    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks: list[str] = []
    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        target_end = min(start + chunk_size, text_length)
        end = _find_sentence_boundary(cleaned_text, start, target_end)
        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(end - overlap, 0)
        while start < text_length and cleaned_text[start].isspace():
            start += 1

    return chunks


def _find_sentence_boundary(text: str, start: int, target_end: int) -> int:
    if target_end >= len(text):
        return len(text)

    search_start = max(start + int((target_end - start) * 0.65), start)
    candidates = [
        text.rfind(boundary, search_start, target_end)
        for boundary in (". ", "? ", "! ", "\n")
    ]
    boundary_index = max(candidates)

    if boundary_index > start:
        return boundary_index + 1

    fallback = text.rfind(" ", search_start, target_end)
    if fallback > start:
        return fallback

    return target_end
