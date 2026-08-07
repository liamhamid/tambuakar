"""Pipeline — orkestrasi satu kitaran: source.fetch() -> Bronze -> Silver.

Purpose: jalankan satu kitaran kutipan hujung ke hujung.
Responsibilities: sambung satu `KnowledgeSource` ke storan Medallion.
Dependencies: pustaka standard + modul tempatan.
Future: fan-out banyak sumber; Identity Resolution sebelum Gold.
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
