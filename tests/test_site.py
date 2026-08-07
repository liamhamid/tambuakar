"""Ujian offline untuk pembina payload site (Layer A) — tiada rangkaian."""

from __future__ import annotations

from tambuakar.identity import resolve
from tambuakar.ports import Record
from tambuakar.site import build_site


def _records() -> list[Record]:
    return [
        Record("wikidata", "Q1", "football_club", "Johor Darul Ta'zim", {"country": "Malaysia"}),
        Record("gdelt", "u1", "football_club", "Johor Darul Ta'zim"),
        Record("wikidata", "Q2", "football_club", "Selangor FC", {"country": "Malaysia"}),
        Record(
            "gdelt",
            "https://x.com/a",
            "news",
            "Johor Darul Ta'zim signs new sleeve sponsor",
            {"domain": "x.com", "seendate": "20260805T000000Z"},
        ),
        Record(
            "gdelt",
            "https://x.com/b",
            "news",
            "Johor Darul Ta'zim announces kit deal",
            {"domain": "y.com", "seendate": "20260806T000000Z"},
        ),
        # Berita tanpa entiti sepadan -> tidak dikira sebagai deal entiti.
        Record("gdelt", "https://x.com/c", "news", "Random athletics update", {}),
    ]


def _payload() -> dict[str, object]:
    entities, _ = resolve(_records())
    return build_site(entities, generated_at="2026-08-07")


def test_kpis_count_real_entities_and_deals() -> None:
    body = _payload()
    kpis = body["kpis"]
    assert isinstance(kpis, dict)
    assert kpis["entities"] == 2  # dua kelab
    assert kpis["teams"] == 2
    assert kpis["deals"] == 2  # dua berita terlink; yang tak terlink tak dikira
    assert kpis["sources"] >= 2


def test_top_entity_has_news_newest_first() -> None:
    body = _payload()
    entities = body["entities"]
    assert isinstance(entities, list)
    top = entities[0]
    assert top["name"] == "Johor Darul Ta'zim"
    assert top["country"] == "Malaysia"
    assert top["deals"] == 2
    # Berita terbaru (06) mendahului yang lama (05).
    assert top["news"][0]["title"] == "Johor Darul Ta'zim announces kit deal"


def test_payload_is_client_safe() -> None:
    body = _payload()
    # Tiada nama dalaman engine atau data mentah dalam payload.
    blob = str(body).lower()
    assert "tambuakar" not in blob
    assert "identity_map" not in blob
    assert body["generated_at"] == "2026-08-07"
