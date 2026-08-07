"""Pipeline — orkestrasi kitaran: source.fetch() -> Bronze -> Silver.

Purpose: jalankan satu (atau banyak) sumber hujung ke hujung.
Responsibilities: sambung `KnowledgeSource` ke storan Medallion; tahan ralat
    per-sumber supaya satu sumber gagal tidak menjatuhkan yang lain.
Dependencies: pustaka standard + modul tempatan.
Future: Identity Resolution sebelum Gold; jadual/concurrency.
"""

from __future__ import annotations

from pathlib import Path

from .medallion import to_silver, write_bronze, write_silver
from .ports import KnowledgeSource


def run(source: KnowledgeSource, data_dir: Path) -> dict[str, int]:
    """Ambil dari `source`, tulis Bronze, hasilkan & tulis Silver. Pulang statistik."""
    records = source.fetch()
    write_bronze(records, data_dir / "bronze" / source.name)
    silver = to_silver(records)
    write_silver(silver, data_dir / "silver" / source.name)
    return {"fetched": len(records), "silver": len(silver)}


def run_all(sources: list[KnowledgeSource], data_dir: Path) -> dict[str, dict[str, object]]:
    """Jalankan setiap sumber; tangkap ralat per-sumber (resilient)."""
    results: dict[str, dict[str, object]] = {}
    for source in sources:
        try:
            results[source.name] = dict(run(source, data_dir))
        except Exception as exc:
            results[source.name] = {"error": str(exc)}
    return results
