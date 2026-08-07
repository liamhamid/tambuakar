"""Identity Resolution Engine (IRE) v1 — peringkat entiti + link mention.

Purpose: satukan **entiti** (kelab/atlet/brand) merentas sumber jadi profil
    kanonik, dan **link mention** (berita/trend) ke entiti — bukan jadikan
    berita/trend sebagai entiti.
Method: entiti — deterministik (nama ternormal sama) + fuzzy (difflib), block
    ikut `kind`. Mention — trend padan nama; berita link bila nama entiti muncul
    dalam tajuk.
Dependencies: pustaka standard (`difflib`, `re`). Tiada kunci API, tiada kos.
Future: swap difflib -> `rapidfuzz`; alias/abbreviation ("Man Utd"); NER untuk
    ekstrak entiti dari teks berita; padanan ID silang-sumber (Wikidata QID).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .ports import Record

# Kind yang mewakili ENTITI (boleh diresolusi jadi profil bersatu).
ENTITY_KINDS = frozenset({"football_club", "athlete", "brand", "league", "team", "venue"})
# Kind yang mewakili MENTION (rujukan kepada entiti, bukan entiti sendiri).
MENTION_KINDS = frozenset({"news", "trend"})

# Akhiran nama kelab yang dibuang semasa normalisasi ("Arsenal F.C." == "Arsenal").
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
    """Satu entiti kanonik: gabungan record entiti + mention terlink."""

    entity_id: str
    kind: str
    canonical_name: str
    members: list[tuple[str, str]] = field(default_factory=list)
    sources: set[str] = field(default_factory=set)
    attrs: dict[str, str] = field(default_factory=dict)
    mentions: list[dict[str, str]] = field(default_factory=list)


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _phrase_in(phrase: str, text: str) -> bool:
    """Betul jika `phrase` muncul sebagai perkataan penuh dalam `text`."""
    return bool(phrase) and f" {phrase} " in f" {text} "


def _resolve_entities(
    records: list[Record], threshold: float
) -> tuple[list[Entity], dict[str, dict[str, str]]]:
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


def _link_mentions(
    entities: list[Entity], mentions: list[Record], identity_map: dict[str, dict[str, str]]
) -> None:
    for rec in mentions:
        norm = normalize(rec.name)
        best: Entity | None = None
        score = 0.0
        for ent in entities:
            ent_norm = normalize(ent.canonical_name)
            if not ent_norm:
                continue
            if rec.kind == "trend":
                ratio = 1.0 if ent_norm == norm else _similar(ent_norm, norm)
                if ratio >= 0.9 and ratio > score:
                    best, score = ent, ratio
            elif _phrase_in(ent_norm, norm) and len(ent_norm) > score:
                # Nama entiti terpanjang yang muncul dalam tajuk = padanan paling spesifik.
                best, score = ent, float(len(ent_norm))

        key = f"{rec.source}:{rec.source_id}"
        if best is None:
            identity_map[key] = {"method": "unlinked", "confidence": "0.00", "entity_id": ""}
            continue
        mention = {
            "kind": rec.kind,
            "source": rec.source,
            "source_id": rec.source_id,
            "ref": rec.name,
        }
        # Bawa metadata berguna untuk paparan (bila/di mana), jika ada.
        for meta in ("seendate", "domain", "value", "date"):
            if meta in rec.attrs:
                mention[meta] = rec.attrs[meta]
        best.mentions.append(mention)
        best.sources.add(rec.source)
        identity_map[key] = {
            "method": "mention",
            "confidence": "1.00",
            "entity_id": best.entity_id,
        }


def resolve(
    records: list[Record], threshold: float = 0.88
) -> tuple[list[Entity], dict[str, dict[str, str]]]:
    """Resolusi entiti + link mention. Pulang (entities, identity_map).

    Record `kind` dalam MENTION_KINDS (news/trend) dilink ke entiti; selainnya
    diresolusi sebagai entiti.
    """
    entity_recs = [r for r in records if r.kind not in MENTION_KINDS]
    mention_recs = [r for r in records if r.kind in MENTION_KINDS]
    entities, identity_map = _resolve_entities(entity_recs, threshold)
    _link_mentions(entities, mention_recs, identity_map)
    return entities, identity_map
