"""Adapter Wikipedia (Games) — sejarah PENUH edisi temasya (jadual).

Purpose: backfill sejarah lengkap — SEMUA edisi SEA Games & SUKMA (tahun + tuan
    rumah) dari jadual Wikipedia, lengkapkan apa yang Wikidata tak link.
Method: baca halaman, `pandas.read_html` ekstrak jadual, kesan jadual "edisi"
    (ada lajur tahun + tuan rumah) secara heuristik, petakan baris -> `Record`.
Dependencies: `pandas` + `lxml` (lihat requirements.txt). Import dilindungi.
Future: tarik jadual pingat semua-masa (ikut negara/negeri) sebagai payload
    berasingan; sumber rasmi (MASOC) untuk 2027.
"""

from __future__ import annotations

import io
import re
import ssl
import urllib.request
from typing import TYPE_CHECKING

from ..ports import Record

if TYPE_CHECKING:
    from pandas import DataFrame

try:
    import pandas as pd
except ImportError:
    pd = None

_PAGES = [
    ("https://en.wikipedia.org/wiki/Southeast_Asian_Games", "Southeast Asian Games"),
    ("https://en.wikipedia.org/wiki/Sukma_Games", "Sukma Games"),
]
_HEADERS = {"User-Agent": "Tambuakar/0.1 (sports-marketing data; +https://tambuakar.com)"}
_YEAR = re.compile(r"(19|20)\d{2}")


def _flat_cols(df: DataFrame) -> list[str]:
    out = []
    for c in df.columns:
        if isinstance(c, tuple):
            parts = [str(p) for p in c if str(p) and "Unnamed" not in str(p)]
            out.append(" ".join(dict.fromkeys(parts)).strip().lower())
        else:
            out.append(str(c).strip().lower())
    return out


def _pick(cols: list[str], *musts: str) -> int:
    for i, c in enumerate(cols):
        if all(m in c for m in musts):
            return i
    return -1


def _clean(val: object) -> str:
    text = re.sub(r"\[[^\]]*\]", "", str(val))  # buang rujukan [1]
    return re.sub(r"\s+", " ", text).strip()


class WikipediaGamesSource:
    """Sumber edisi temasya (sejarah penuh) dari jadual Wikipedia."""

    name = "wikipedia_games"

    def __init__(self, pages: list[tuple[str, str]] | None = None, timeout: float = 30.0) -> None:
        self._pages = pages if pages is not None else _PAGES
        self._timeout = timeout

    def fetch(self) -> list[Record]:
        if pd is None:
            raise RuntimeError("pandas belum dipasang — `pip install -r requirements.txt`")
        out: list[Record] = []
        for url, series in self._pages:
            out.extend(self._editions(self._get(url), series))
        return out

    def _get(self, url: str) -> str:
        req = urllib.request.Request(url, headers=_HEADERS)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=self._timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", "replace")

    @staticmethod
    def _editions(html: str, series: str) -> list[Record]:
        if pd is None:
            return []
        try:
            tables = pd.read_html(io.StringIO(html))
        except Exception:
            return []
        out: list[Record] = []
        seen: set[str] = set()
        for df in tables:
            cols = _flat_cols(df)
            yc = _pick(cols, "year")
            if yc < 0:
                yc = _pick(cols, "edition")
            hc = _pick(cols, "host", "nation")
            if hc < 0:
                hc = _pick(cols, "host", "country")
            if hc < 0:
                hc = _pick(cols, "host", "state")
            if hc < 0:
                hc = _pick(cols, "host")
            if yc < 0 or hc < 0:
                continue
            for _, row in df.iterrows():
                m = _YEAR.search(_clean(row.iloc[yc]))
                if not m:
                    continue
                year = m.group(0)
                host = _clean(row.iloc[hc])
                sid = f"{series}:{year}"
                if sid in seen or not host or host.lower() in ("nan", "tbd", "tba"):
                    continue
                seen.add(sid)
                out.append(
                    Record(
                        source="wikipedia_games",
                        source_id=sid,
                        kind="games_edition",
                        name=f"{year} {series}",
                        attrs={"year": year, "host": host, "series": series},
                    )
                )
        return out
