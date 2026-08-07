"""Ujian offline untuk petaan sumber GDELT & Google Trends — tiada rangkaian."""

from __future__ import annotations

import urllib.error

import pytest
from tambuakar.sources import gdelt
from tambuakar.sources.gdelt import GdeltSource
from tambuakar.sources.google_trends import GoogleTrendsSource


def test_gdelt_maps_articles_and_skips_incomplete() -> None:
    raw = {
        "articles": [
            {
                "url": "https://example.com/a",
                "title": "Nike signs record deal with football club",
                "domain": "example.com",
                "seendate": "20260101T000000Z",
                "sourcecountry": "United States",
            },
            {"url": "https://example.com/b"},  # tiada tajuk -> dilangkau
        ]
    }
    records = GdeltSource._to_records(raw)
    assert len(records) == 1
    rec = records[0]
    assert rec.kind == "news"
    assert rec.source_id == "https://example.com/a"
    assert rec.attrs["domain"] == "example.com"


def test_gdelt_retries_on_429_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    class _Resp:
        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def read(self) -> bytes:
            return b'{"articles": []}'

    def _fake_urlopen(req: urllib.request.Request, timeout: float, context: object) -> _Resp:
        calls["n"] += 1
        if calls["n"] < 3:
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {}, None)  # type: ignore[arg-type]
        return _Resp()

    monkeypatch.setattr(gdelt.urllib.request, "urlopen", _fake_urlopen)
    monkeypatch.setattr(gdelt.time, "sleep", lambda _s: None)
    result = GdeltSource(retries=3, backoff=0.01).fetch()
    assert calls["n"] == 3  # 2 kali 429 + 1 berjaya
    assert result == []


def test_trends_maps_rows() -> None:
    rows = [
        {"term": "Johor Darul Ta'zim", "date": "2026-08-01", "value": "80"},
        {"term": "", "date": "2026-08-01", "value": "10"},  # tiada term -> dilangkau
    ]
    records = GoogleTrendsSource._to_records(rows)
    assert len(records) == 1
    rec = records[0]
    assert rec.kind == "trend"
    assert rec.name == "Johor Darul Ta'zim"
    assert rec.attrs["value"] == "80"
