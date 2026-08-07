"""Pipeline — orkestrasi: sumber -> Bronze -> Silver -> (IRE) -> Gold.

Purpose: jalankan satu/banyak sumber, lepas tu satukan identiti jadi Gold.
Responsibilities: sambung `KnowledgeSource` ke Medallion + IRE; tahan ralat
    per-sumber supaya satu sumber gagal tidak menjatuhkan yang lain.
Dependencies: pustaka standard + modul tempatan.
Future: jadual/concurrency; Gold ke Postgres.
"""

from __future__ import annotations

from pathlib import Path

from .gold import write_gold
from .identity import resolve
from .medallion import to_silver, write_bronze, write_silver
from .ports import KnowledgeSource, Record


def _collect(source: KnowledgeSource, data_dir: Path) -> tuple[list[Record], list[Record]]:
    records = source.fetch()
    write_bronze(records, data_dir / "bronze" / source.name)
    silver = to_silver(records)
    write_silver(silver, data_dir / "silver" / source.name)
    return records, silver


def run(source: KnowledgeSource, data_dir: Path) -> dict[str, int]:
    """Satu sumber -> Bronze + Silver. Pulang statistik."""
    records, silver = _collect(source, data_dir)
    return {"fetched": len(records), "silver": len(silver)}


def run_all(sources: list[KnowledgeSource], data_dir: Path) -> dict[str, dict[str, object]]:
    """Semua sumber -> Silver, kemudian IRE merentas semua -> Gold. Resilient."""
    results: dict[str, dict[str, object]] = {}
    all_silver: list[Record] = []
    for source in sources:
        try:
            records, silver = _collect(source, data_dir)
            all_silver.extend(silver)
            results[source.name] = {"fetched": len(records), "silver": len(silver)}
        except Exception as exc:
            results[source.name] = {"error": str(exc)}

    entities, identity_map = resolve(all_silver)
    write_gold(entities, identity_map, data_dir / "gold")
    results["_gold"] = {"entities": len(entities), "mapped": len(identity_map)}
    return results
