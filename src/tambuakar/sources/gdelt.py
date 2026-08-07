"""Adapter GDELT DOC 2.0 — 🟢 terbuka; berita global (deal/penajaan/trend).

Purpose: jejak berita sukan & pemasaran dunia (pengumuman penajaan, aktiviti brand).
Responsibilities: pertanyaan GDELT DOC API, petakan artikel -> `Record` (kind="news").
Dependencies: pustaka standard (`urllib`) sahaja — tiada kunci API, tiada kos.
Future: tapis ikut tema/negara; ekstrak entiti penaja dari tajuk (untuk IRE).
"""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

from ..ports import Record

_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"
_HEADERS = {
    "User-Agent": "Tambuakar/0.1 (sports-marketing data; +https://tambuakar.com)",
}
# Kod HTTP yang wajar dicuba semula (GDELT selalu 429 pada IP dikongsi).
_RETRY_CODES = frozenset({429, 500, 502, 503, 504})


class GdeltSource:
    """Sumber berita global (sukan/penajaan) dari GDELT."""

    name = "gdelt"

    def __init__(
        self,
        query: str = "sports sponsorship",
        max_records: int = 50,
        timeout: float = 30.0,
        retries: int = 3,
        backoff: float = 2.0,
    ) -> None:
        self._query = query
        self._max_records = max_records
        self._timeout = timeout
        self._retries = retries
        self._backoff = backoff

    def fetch(self) -> list[Record]:
        return self._to_records(self._query_api())

    def _query_api(self) -> dict:
        params = urllib.parse.urlencode(
            {
                "query": self._query,
                "mode": "artlist",
                "format": "json",
                "maxrecords": self._max_records,
                "sort": "datedesc",
            }
        )
        url = f"{_ENDPOINT}?{params}"
        ctx = ssl.create_default_context()
        # Cuba semula dengan backoff eksponen bila kena 429/5xx (transient).
        for attempt in range(self._retries + 1):
            try:
                req = urllib.request.Request(url, headers=_HEADERS)
                with urllib.request.urlopen(req, timeout=self._timeout, context=ctx) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if attempt >= self._retries or exc.code not in _RETRY_CODES:
                    raise
            except urllib.error.URLError:
                if attempt >= self._retries:
                    raise
            time.sleep(self._backoff * (2**attempt))
        raise RuntimeError("unreachable")  # pragma: no cover

    @staticmethod
    def _to_records(raw: dict) -> list[Record]:
        out: list[Record] = []
        for art in raw.get("articles", []):
            url = art.get("url", "")
            title = art.get("title", "")
            if not url or not title:
                continue
            attrs: dict[str, str] = {}
            for key in ("domain", "seendate", "sourcecountry", "language"):
                value = art.get(key)
                if value:
                    attrs[key] = value
            out.append(
                Record(source="gdelt", source_id=url, kind="news", name=title, attrs=attrs)
            )
        return out
