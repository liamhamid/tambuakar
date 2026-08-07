"""Ports (interfaces) — sempadan Clean Architecture untuk Tambuakar.

Purpose: takrif port `KnowledgeSource` supaya setiap sumber data dunia jadi
    adapter yang boleh ditukar ganti di belakang satu kontrak.
Responsibilities: bentuk `Record` (dengan provenance) + protokol sumber.
Dependencies: pustaka standard sahaja.
Future: tambah `StoragePort` bila Bronze/Silver berpindah dari fail ke Postgres.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Record:
    """Satu item mentah dari sumber, dengan asal-usul (provenance).

    `source` + `source_id` = kunci unik setiap rekod (dipakai untuk dedup dan,
    kemudian, oleh Identity Resolution Engine).
    """

    source: str
    source_id: str
    kind: str
    name: str
    attrs: dict[str, str] = field(default_factory=dict)


class KnowledgeSource(Protocol):
    """Adapter untuk satu sumber data dunia (sah + berlesen guna)."""

    name: str

    def fetch(self) -> list[Record]:
        """Ambil rekod mentah dari sumber."""
        ...
