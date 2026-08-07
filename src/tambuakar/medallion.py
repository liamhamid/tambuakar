"""Storan Medallion — Bronze (mentah) & Silver (bersih), JSONL atas cakera.

Purpose: simpan data berlapis supaya recall bersih, bukan longgokan mentah.
Responsibilities: tulis Bronze (persis diambil) & Silver (dedup + normalisasi).
Dependencies: pustaka standard sahaja. Adapter Postgres/object-storage kemudian.
Future: tukar fail -> Postgres (Silver/Gold) + object storage (Bronze).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .ports import Record


def _write_jsonl(records: list[Record], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
    return path


def write_bronze(records: list[Record], root: Path) -> Path:
    """Simpan rekod persis seperti diambil (arkib, boleh ulang proses)."""
    return _write_jsonl(records, root / "bronze.jsonl")


def to_silver(records: list[Record]) -> list[Record]:
    """Dedup ikut (source, source_id) + normalisasi ruang dalam nama."""
    seen: set[tuple[str, str]] = set()
    out: list[Record] = []
    for rec in records:
        key = (rec.source, rec.source_id)
        if key in seen:
            continue
        seen.add(key)
        clean_name = " ".join(rec.name.split())
        out.append(
            Record(
                source=rec.source,
                source_id=rec.source_id,
                kind=rec.kind,
                name=clean_name,
                attrs=rec.attrs,
            )
        )
    return out


def write_silver(records: list[Record], root: Path) -> Path:
    """Simpan rekod bersih (sudah dedup + dinormalisasi)."""
    return _write_jsonl(records, root / "silver.jsonl")
