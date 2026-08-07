"""Adapter Google Trends (pytrends) — 🟢 percuma; minat audiens ikut masa & negara.

Purpose: ukur minat orang terhadap sukan/pasukan/brand (isyarat audiens).
Responsibilities: tanya pytrends, petakan siri masa -> `Record` (kind="trend").
Dependencies: `pytrends` (lihat tambuakar/requirements.txt). Import dilindungi —
    modul lain tidak gagal walau pytrends belum dipasang; fetch() beri mesej jelas.
Future: bandingkan pasukan/brand; minat mengikut negeri (audiens tempatan).
"""

from __future__ import annotations

import time
from collections.abc import Iterable

from ..ports import Record

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None


class GoogleTrendsSource:
    """Sumber minat audiens (siri masa) dari Google Trends."""

    name = "google_trends"

    def __init__(
        self,
        terms: Iterable[str],
        geo: str = "MY",
        timeframe: str = "today 3-m",
        tz: int = 480,
        retries: int = 3,
        backoff: float = 3.0,
    ) -> None:
        self._terms = list(terms)
        self._geo = geo
        self._timeframe = timeframe
        self._tz = tz
        self._retries = retries
        self._backoff = backoff

    def fetch(self) -> list[Record]:
        if TrendReq is None:
            raise RuntimeError(
                "pytrends belum dipasang — `pip install -r tambuakar/requirements.txt`"
            )
        rows = self._fetch_rows()
        return self._to_records(rows)

    def _fetch_rows(self) -> list[dict[str, str]]:
        # Google Trends kerap 429 pada IP dikongsi — cuba semula dengan backoff.
        trend_cls = TrendReq
        if trend_cls is None:  # pragma: no cover — dijaga oleh fetch()
            raise RuntimeError("pytrends belum dipasang")
        last: Exception | None = None
        for attempt in range(self._retries + 1):
            try:
                client = trend_cls(hl="en-US", tz=self._tz, retries=2, backoff_factor=0.5)
                client.build_payload(self._terms, geo=self._geo, timeframe=self._timeframe)
                frame = client.interest_over_time()
                rows: list[dict[str, str]] = []
                for idx, row in frame.iterrows():
                    date = str(idx)
                    for term in self._terms:
                        if term in row:
                            rows.append(
                                {"term": term, "date": date, "value": str(int(row[term]))}
                            )
                return rows
            except Exception as exc:  # pytrends/requests: 429, timeout, parse
                last = exc
                if attempt >= self._retries:
                    break
                time.sleep(self._backoff * (2**attempt))
        raise RuntimeError(f"Google Trends gagal selepas cuba semula: {last}")

    @staticmethod
    def _to_records(rows: list[dict[str, str]]) -> list[Record]:
        out: list[Record] = []
        for row in rows:
            term = row.get("term", "")
            date = row.get("date", "")
            if not term or not date:
                continue
            out.append(
                Record(
                    source="google_trends",
                    source_id=f"{term}:{date}",
                    kind="trend",
                    name=term,
                    attrs={"date": date, "value": row.get("value", "")},
                )
            )
        return out
