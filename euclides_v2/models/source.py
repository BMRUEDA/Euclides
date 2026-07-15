from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceFile:
    name: str
    size: int
    content: bytes


@dataclass(frozen=True)
class DocumentChunk:
    source_name: str
    page_number: int
    text: str


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float
    matched_terms: list[str]


@dataclass(frozen=True)
class PdfDiagnostic:
    source_name: str
    page_count: int
    extracted_pages: int
    chunk_count: int
    preview: str
    error: str | None = None

    @property
    def has_text(self) -> bool:
        return self.chunk_count > 0


@dataclass(frozen=True)
class PdfCorpus:
    chunks: list[DocumentChunk]
    diagnostics: list[PdfDiagnostic]

    @property
    def has_sources(self) -> bool:
        return bool(self.diagnostics)

    @property
    def has_text(self) -> bool:
        return bool(self.chunks)

    @property
    def errors(self) -> list[str]:
        return [
            f"{diagnostic.source_name}: {diagnostic.error}"
            for diagnostic in self.diagnostics
            if diagnostic.error
        ]
