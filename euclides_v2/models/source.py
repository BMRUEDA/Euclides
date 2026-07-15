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

