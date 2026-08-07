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


def test_mentions_link_to_entity_not_treated_as_entities() -> None:
    records = [
        _club("wikidata", "Q1", "Manchester United F.C."),
        Record(source="gdelt", source_id="n1", kind="news",
               name="Manchester United signs Adidas deal"),
        Record(source="google_trends", source_id="MU:2026", kind="trend",
               name="Manchester United"),
        Record(source="gdelt", source_id="n2", kind="news",
               name="Chelsea appoints new manager"),
    ]
    entities, imap = resolve(records)
    # Hanya kelab = entiti; berita/trend = mention, bukan entiti.
    assert len(entities) == 1
    club = entities[0]
    assert {m["kind"] for m in club.mentions} == {"news", "trend"}
    assert imap["gdelt:n1"]["entity_id"] == club.entity_id
    assert imap["google_trends:MU:2026"]["entity_id"] == club.entity_id
    # Berita tanpa entiti sepadan -> unlinked, BUKAN digabung salah.
    assert imap["gdelt:n2"]["method"] == "unlinked"


def test_distinct_news_not_merged_into_one_entity() -> None:
    records = [
        Record(source="g", source_id="a", kind="news",
               name="Nike signs sponsorship deal with Arsenal"),
        Record(source="g", source_id="b", kind="news",
               name="Nike signs sponsorship deal with Chelsea"),
    ]
    entities, _ = resolve(records)
    # Tiada entiti (semua berita) -> tiada gabungan salah.
    assert entities == []
