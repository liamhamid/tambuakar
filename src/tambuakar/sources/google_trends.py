"""Adapter Google Trends (pytrends) — 🟢 percuma; minat audiens ikut masa & negara.

Purpose: ukur minat orang terhadap sukan/pasukan/brand (isyarat audiens).
Responsibilities: tanya pytrends, petakan siri masa -> `Record` (kind="trend").
Dependencies: `pytrends` (lihat tambuakar/requirements.txt). Import dilindungi —
    modul lain tidak gagal walau pytrends belum dipasang; fetch() beri mesej jelas.
Future: bandingkan pasukan/brand; minat mengikut negeri (audiens tempatan).
"""

from __future__ import annotations

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
    ) -> None:
        self._terms = list(terms)
        self._geo = geo
        self._timeframe = timeframe
        self._tz = tz

    def fetch(self) -> list[Record]:
        if TrendReq is None:
            raise RuntimeError(
                "pytrends belum dipasang — `pip install -r tambuakar/requirements.txt`"
            )
        client = TrendReq(hl="en-US", tz=self._tz)
        client.build_payload(self._terms, geo=self._geo, timeframe=self._timeframe)
        frame = client.interest_over_time()
        rows: list[dict[str, str]] = []
        for idx, row in frame.iterrows():
            date = str(idx)
            for term in self._terms:
                if term in row:
                    rows.append({"term": term, "date": date, "value": str(int(row[term]))})
        return self._to_records(rows)

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
