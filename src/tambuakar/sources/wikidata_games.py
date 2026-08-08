"""Adapter Wikidata (Games) — 🟢 terbuka (CC0). Sejarah temasya multi-sukan.

Purpose: tarik EDISI temasya multi-sukan bersejarah (SEA Games, SUKMA) — nama,
    tahun, tuan rumah — sebagai entiti `games_edition`. Tapak untuk data SEA Games
    2027 + sukan Malaysia dunia.
Method: SPARQL — item yang "part of series" (P179) atau "instance of" (P31) satu
    siri Games yang dikonfigur. Resilient: siri yang tiada padanan pulang kosong.
Dependencies: pustaka standard (`urllib`) sahaja — tiada kunci API, tiada kos.
Future: tarik atlet/pemenang pingat per edisi; padan ID silang-sumber (QID).
"""

from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request

from ..ports import Record

_ENDPOINT = "https://query.wikidata.org/sparql"

# Siri Games (QID Wikidata, disahkan). Edisi berkait via P179 (part of the series).
# Tambah QID calon supaya edisi lama (dimodel tak konsisten) turut tertangkap.
_SEA_GAMES = "Q877484"  # SEA Games
_SEA_GAMES_ALT = "Q170385"  # varian "Southeast Asian Games"
_SUKMA = "Q137161"  # Sukma Games (Sukan Malaysia)

# Edisi = item yang tergolong dalam siri (P179) atau instance-of siri (P31).
# (Elak P361: ia tarik acara sub-sukan "Badminton at the SEA Games", bukan edisi.)
_QUERY = """
SELECT DISTINCT ?ed ?edLabel ?date ?hostLabel WHERE {
  VALUES ?series { %(series)s }
  { ?ed wdt:P179 ?series } UNION { ?ed wdt:P31 ?series }
  OPTIONAL { ?ed wdt:P585 ?date. }
  OPTIONAL { ?ed wdt:P17 ?host. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC(?date)
LIMIT %(limit)d
"""

# Frasa yang menandakan acara SUB-SUKAN (bukan edisi penuh) — dibuang.
_SUBEVENT_HINTS = (" at the ", " at sukan", " at sea games")

_HEADERS = {
    "User-Agent": "Tambuakar/0.1 (sports-marketing data; +https://tambuakar.com)",
    "Accept": "application/sparql-results+json",
}


class WikidataGamesSource:
    """Sumber edisi temasya multi-sukan (sejarah) dari Wikidata."""

    name = "wikidata_games"

    def __init__(
        self, series: list[str] | None = None, limit: int = 80, timeout: float = 30.0
    ) -> None:
        self._series = series if series is not None else [_SEA_GAMES, _SEA_GAMES_ALT, _SUKMA]
        self._limit = limit
        self._timeout = timeout

    def fetch(self) -> list[Record]:
        values = " ".join(f"wd:{qid}" for qid in self._series)
        raw = self._query(_QUERY % {"series": values, "limit": self._limit})
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
            uri = row.get("ed", {}).get("value", "")
            source_id = uri.rsplit("/", 1)[-1]  # Q-id
            name = row.get("edLabel", {}).get("value", "")
            if not source_id or not name or source_id == name:
                continue
            low = name.lower()
            if any(hint in low for hint in _SUBEVENT_HINTS):
                continue  # langkau acara sub-sukan, simpan edisi penuh sahaja
            attrs: dict[str, str] = {}
            date = row.get("date", {}).get("value", "")
            if len(date) >= 4 and date[:4].isdigit():
                attrs["year"] = date[:4]
            host = row.get("hostLabel", {}).get("value")
            if host:
                attrs["host"] = host
            out.append(
                Record(
                    source="wikidata_games",
                    source_id=source_id,
                    kind="games_edition",
                    name=name,
                    attrs=attrs,
                )
            )
        return out
