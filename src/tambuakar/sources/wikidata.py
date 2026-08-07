"""Adapter Wikidata (SPARQL) — 🟢 terbuka (CC0), guna komersial OK.

Purpose: tarik fakta sukan dunia berstruktur (mula: kelab bola sepak) dari Wikidata.
Responsibilities: jalankan satu pertanyaan SPARQL, petakan baris -> `Record`.
Dependencies: pustaka standard (`urllib`) sahaja — tiada kunci API, tiada kos.
Future: parameterkan pertanyaan; tambah atlet/penaja; halaman (pagination).
"""

from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request

from ..ports import Record

_ENDPOINT = "https://query.wikidata.org/sparql"

# Kelab bola sepak (instance-of `association football club`, wd:Q476028) + negara.
_QUERY = """
SELECT ?club ?clubLabel ?countryLabel WHERE {
  ?club wdt:P31 wd:Q476028 .
  OPTIONAL { ?club wdt:P17 ?country . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT %d
"""

_HEADERS = {
    "User-Agent": "Tambuakar/0.1 (sports-marketing data; +https://tambuakar.com)",
    "Accept": "application/sparql-results+json",
}


class WikidataSource:
    """Sumber kelab bola sepak dunia dari Wikidata."""

    name = "wikidata"

    def __init__(self, limit: int = 50, timeout: float = 30.0) -> None:
        self._limit = limit
        self._timeout = timeout

    def fetch(self) -> list[Record]:
        raw = self._query(_QUERY % self._limit)
        return self._to_records(raw)

    def _query(self, sparql: str) -> dict:
        params = urllib.parse.urlencode({"query": sparql, "format": "json"})
        req = urllib.request.Request(f"{_ENDPOINT}?{params}", headers=_HEADERS)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=self._timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _to_records(raw: dict) -> list[Record]:
        out: list[Record] = []
        for row in raw.get("results", {}).get("bindings", []):
            uri = row.get("club", {}).get("value", "")
            source_id = uri.rsplit("/", 1)[-1]  # Q-id, cth Q18656
            name = row.get("clubLabel", {}).get("value", "")
            if not source_id or not name or source_id == name:
                continue
            attrs: dict[str, str] = {}
            country = row.get("countryLabel", {}).get("value")
            if country:
                attrs["country"] = country
            out.append(
                Record(
                    source="wikidata",
                    source_id=source_id,
                    kind="football_club",
                    name=name,
                    attrs=attrs,
                )
            )
        return out
