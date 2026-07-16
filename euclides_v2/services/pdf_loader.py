from __future__ import annotations

from io import BytesIO
from typing import Iterable

import streamlit as st
from pypdf import PdfReader

from models.source import DocumentChunk, PdfCorpus, PdfDiagnostic, SourceFile
from services.chunking import split_text_into_chunks


def extract_pdf_chunks(sources: Iterable[SourceFile]) -> list[DocumentChunk]:
    return load_pdf_corpus(sources).chunks


@st.cache_data(show_spinner=False)
def load_pdf_corpus(sources: Iterable[SourceFile]) -> PdfCorpus:
    chunks: list[DocumentChunk] = []
    diagnostics: list[PdfDiagnostic] = []

    for source in sources:
        source_chunks, diagnostic = read_pdf_source(source)
        diagnostics.append(diagnostic)

        if diagnostic.error:
            continue

        chunks.extend(source_chunks)

    return PdfCorpus(chunks=chunks, diagnostics=diagnostics)


def extract_source_chunks(source: SourceFile) -> list[DocumentChunk]:
    reader = PdfReader(BytesIO(source.content))
    return extract_source_chunks_from_reader(source, reader)


def inspect_pdf_source(source: SourceFile) -> PdfDiagnostic:
    _, diagnostic = read_pdf_source(source)
    return diagnostic


def read_pdf_source(source: SourceFile) -> tuple[list[DocumentChunk], PdfDiagnostic]:
    try:
        reader = PdfReader(BytesIO(source.content))
        page_count = len(reader.pages)
        chunks = extract_source_chunks_from_reader(source, reader)
    except Exception as exc:
        return (
            [],
            PdfDiagnostic(
                source_name=source.name,
                page_count=0,
                extracted_pages=0,
                chunk_count=0,
                preview="",
                error=f"Nao foi possivel ler este PDF: {exc}",
            ),
        )

    extracted_pages = len({chunk.page_number for chunk in chunks})
    preview = "\n\n".join(chunk.text[:700] for chunk in chunks[:2])

    return (
        chunks,
        PdfDiagnostic(
            source_name=source.name,
            page_count=page_count,
            extracted_pages=extracted_pages,
            chunk_count=len(chunks),
            preview=preview,
        ),
    )


def extract_source_chunks_from_reader(
    source: SourceFile,
    reader: PdfReader,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        page_chunks = split_text_into_chunks(text)
        for chunk_text in page_chunks:
            chunks.append(
                DocumentChunk(
                    source_name=source.name,
                    page_number=index,
                    text=chunk_text,
                )
            )

    return chunks
