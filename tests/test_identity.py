"""Ujian offline untuk Identity Resolution Engine (IRE) — tiada rangkaian."""

from __future__ import annotations

from tambuakar.identity import normalize, resolve
from tambuakar.ports import Record


def _club(source: str, sid: str, name: str) -> Record:
    return Record(source=source, source_id=sid, kind="football_club", name=name)


def test_normalize_strips_club_suffix() -> None:
    assert normalize("Arsenal F.C.") == "arsenal"
    assert normalize("  Manchester   United  ") == "manchester united"


def test_ire_merges_same_club_across_sources() -> None:
    records = [
        _club("wikidata", "Q1", "Manchester United F.C."),
        _club("gdelt", "u1", "Manchester United"),
        _club("wikidata", "Q2", "Selangor FC"),
    ]
    entities, imap = resolve(records)
    assert len(entities) == 2
    # Kedua rekod Man Utd -> satu entity_id yang sama (deterministik selepas normalisasi).
    assert imap["wikidata:Q1"]["entity_id"] == imap["gdelt:u1"]["entity_id"]
    assert imap["wikidata:Q2"]["entity_id"] != imap["wikidata:Q1"]["entity_id"]


def test_ire_fuzzy_merges_near_names() -> None:
    records = [
        _club("a", "1", "Johor Darul Tazim"),
        _club("b", "2", "Johor Darul Ta'zim"),
    ]
    entities, imap = resolve(records)
    assert len(entities) == 1
    assert imap["b:2"]["method"] in ("fuzzy", "deterministic")


def test_ire_blocks_by_kind() -> None:
    records = [
        Record(source="a", source_id="1", kind="football_club", name="Nike"),
        Record(source="b", source_id="2", kind="brand", name="Nike"),
    ]
    entities, _ = resolve(records)
    assert len(entities) == 2
