"""Ujian offline untuk transform Silver + petaan Wikidata — tiada rangkaian."""

from __future__ import annotations

from tambuakar.medallion import to_silver
from tambuakar.ports import Record
from tambuakar.sources.wikidata import WikidataSource


def _rec(sid: str, name: str) -> Record:
    return Record(source="wikidata", source_id=sid, kind="football_club", name=name)


def test_silver_dedupes_by_source_id() -> None:
    records = [_rec("Q1", "Club A"), _rec("Q1", "Club A"), _rec("Q2", "Club B")]
    out = to_silver(records)
    assert len(out) == 2
    assert {r.source_id for r in out} == {"Q1", "Q2"}


def test_silver_normalises_whitespace() -> None:
    out = to_silver([_rec("Q3", "  Manchester   United  ")])
    assert out[0].name == "Manchester United"


def test_wikidata_maps_bindings_and_skips_incomplete() -> None:
    raw = {
        "results": {
            "bindings": [
                {
                    "club": {"value": "http://www.wikidata.org/entity/Q18656"},
                    "clubLabel": {"value": "Manchester United F.C."},
                    "countryLabel": {"value": "United Kingdom"},
                },
                # Baris tanpa label -> dilangkau.
                {"club": {"value": "http://www.wikidata.org/entity/Q9999"}},
            ]
        }
    }
    records = WikidataSource._to_records(raw)
    assert len(records) == 1
    rec = records[0]
    assert rec.source_id == "Q18656"
    assert rec.name == "Manchester United F.C."
    assert rec.attrs["country"] == "United Kingdom"
