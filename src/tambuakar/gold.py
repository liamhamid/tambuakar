"""Gold — tulis profil entiti bersatu + identity_map (hasil IRE), JSONL.

Purpose: simpan lapisan Gold (sedia guna) yang Ajis/Serving API baca.
Responsibilities: serialisasi `Entity` + identity_map ke fail.
Dependencies: pustaka standard sahaja.
Future: tulis ke Postgres (jadual sajian) + agregat (benchmark penajaan).
"""

from __future__ import annotations

import json
from pathlib import Path

from .identity import Entity


def _entity_dict(entity: Entity) -> dict[str, object]:
    return {
        "entity_id": entity.entity_id,
        "kind": entity.kind,
        "canonical_name": entity.canonical_name,
        "members": [{"source": s, "source_id": i} for s, i in entity.members],
        "sources": sorted(entity.sources),
        "attrs": entity.attrs,
    }


def write_gold(
    entities: list[Entity], identity_map: dict[str, dict[str, str]], root: Path
) -> Path:
    """Tulis entities.jsonl + identity_map.jsonl. Pulang laluan entities."""
    root.mkdir(parents=True, exist_ok=True)
    entities_path = root / "entities.jsonl"
    with entities_path.open("w", encoding="utf-8") as fh:
        for entity in entities:
            fh.write(json.dumps(_entity_dict(entity), ensure_ascii=False) + "\n")
    map_path = root / "identity_map.jsonl"
    with map_path.open("w", encoding="utf-8") as fh:
        for key, val in identity_map.items():
            fh.write(json.dumps({"key": key, **val}, ensure_ascii=False) + "\n")
    return entities_path
