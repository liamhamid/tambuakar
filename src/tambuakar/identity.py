"""Identity Resolution Engine (IRE) v1 — peringkat entiti.

Purpose: satukan `Record` yang merujuk entiti sama merentas sumber -> entiti
    kanonik + `identity_map` (source:source_id -> entity_id).
Method: **deterministik** (nama ternormal sama) + **fuzzy** (difflib ratio),
    di-block ikut `kind` supaya kelab tak dipadan dengan atlet/brand.
Dependencies: pustaka standard (`difflib`, `re`). Tiada kunci API, tiada kos.
Future: swap difflib -> `rapidfuzz` (laju + alias/abbreviation "Man Utd"),
    padanan ID silang-sumber (Wikidata QID), embeddings untuk padanan semantik.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .ports import Record

# Akhiran nama kelab yang dibuang semasa normalisasi (supaya "Arsenal F.C." dan
# "Arsenal" dikenali sama).
_SUFFIXES = (" fc", " f c", " afc", " sc", " football club", " fk")


def normalize(name: str) -> str:
    """Nama -> bentuk ternormal: huruf kecil, tanpa tanda, akhiran kelab dibuang."""
    text = re.sub(r"[^a-z0-9 ]+", " ", name.lower())
    text = " ".join(text.split())
    for suffix in _SUFFIXES:
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
            break
    return text


@dataclass
class Entity:
    """Satu entiti kanonik hasil penyatuan beberapa Record."""

    entity_id: str
    kind: str
    canonical_name: str
    members: list[tuple[str, str]] = field(default_factory=list)
    sources: set[str] = field(default_factory=set)
    attrs: dict[str, str] = field(default_factory=dict)


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def resolve(
    records: list[Record], threshold: float = 0.88
) -> tuple[list[Entity], dict[str, dict[str, str]]]:
    """Kelompokkan record jadi entiti kanonik. Pulang (entities, identity_map)."""
    clusters: list[Entity] = []
    identity_map: dict[str, dict[str, str]] = {}

    for rec in records:
        norm = normalize(rec.name)
        best: Entity | None = None
        method = "new"
        conf = 1.0
        for ent in clusters:
            if ent.kind != rec.kind:
                continue
            ent_norm = normalize(ent.canonical_name)
            if ent_norm == norm:
                best, method, conf = ent, "deterministic", 1.0
                break
            ratio = _similar(ent_norm, norm)
            if ratio >= threshold and (best is None or ratio > conf):
                best, method, conf = ent, "fuzzy", ratio

        if best is None:
            best = Entity(entity_id="", kind=rec.kind, canonical_name=rec.name)
            clusters.append(best)
            method, conf = "new", 1.0

        best.members.append((rec.source, rec.source_id))
        best.sources.add(rec.source)
        if len(rec.name) > len(best.canonical_name):
            best.canonical_name = rec.name
        best.attrs.update(rec.attrs)
        identity_map[f"{rec.source}:{rec.source_id}"] = {
            "method": method,
            "confidence": f"{conf:.2f}",
        }

    for ent in clusters:
        ent.entity_id = f"{ent.kind}:{normalize(ent.canonical_name).replace(' ', '-')}"
        for source, source_id in ent.members:
            identity_map[f"{source}:{source_id}"]["entity_id"] = ent.entity_id

    return clusters, identity_map
