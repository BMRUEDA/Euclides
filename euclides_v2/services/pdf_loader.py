from __future__ import annotations

from io import BytesIO
from typing import Iterable

from pypdf import PdfReader

from models.source import DocumentChunk, SourceFile


def extract_pdf_chunks(sources: Iterable[SourceFile]) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []

    for source in sources:
        reader = PdfReader(BytesIO(source.content))
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            cleaned_text = " ".join(text.split())
            if cleaned_text:
                chunks.append(
                    DocumentChunk(
                        source_name=source.name,
                        page_number=index,
                        text=cleaned_text,
                    )
                )

    return chunks

