"""Medals — jadual pingat semua-masa (SEA Games) dari Wikipedia.

Purpose: contoh Fasa 2 — tunjuk pencapaian pingat (agregat) untuk pitch penaja.
    Mula: jadual pingat semua-masa SEA Games ikut negara (Malaysia ditonjol).
Method: `pandas.read_html` baca jadual, kesan jadual pingat (ada lajur emas/perak/
    gangsa + lajur negara), petakan baris -> rekod pingat. Fungsi tulen untuk parse.
Dependencies: `pandas` + `lxml` (guard import). Tiada kunci API, tiada kos.
Future: pingat per-edisi + per-atlet; SUKMA ikut negeri; sumber rasmi (MASOC).
"""

from __future__ import annotations

import io
import re
import ssl
import urllib.request

from .sources.wikipedia_games import _clean, _flat_cols, _pick

try:
    import pandas as pd
except ImportError:
    pd = None

_ALLTIME_SEA = "https://en.wikipedia.org/wiki/All-time_Southeast_Asian_Games_medal_table"
_HEADERS = {"User-Agent": "Tambuakar/0.1 (sports-marketing data; +https://tambuakar.com)"}
_NUM = re.compile(r"\d[\d,]*")


def _int(val: object) -> int:
    m = _NUM.search(_clean(val))
    return int(m.group(0).replace(",", "")) if m else 0


def _get(url: str, timeout: float = 30.0) -> str:
    req = urllib.request.Request(url, headers=_HEADERS)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_medal_table(html: str) -> list[dict[str, object]]:
    """Ekstrak jadual pingat terbesar (negara + emas/perak/gangsa). Fungsi tulen."""
    if pd is None:
        return []
    try:
        tables = pd.read_html(io.StringIO(html))
    except Exception:
        return []
    best: list[dict[str, object]] = []
    for df in tables:
        cols = _flat_cols(df)
        g = _pick(cols, "gold")
        s = _pick(cols, "silver")
        b = _pick(cols, "bronze")
        nc = _pick(cols, "nation")
        if nc < 0:
            nc = _pick(cols, "team")
        if nc < 0:
            nc = _pick(cols, "noc")
        if min(g, s, b, nc) < 0:
            continue
        tc = _pick(cols, "total")
        rows: list[dict[str, object]] = []
        for i, (_, row) in enumerate(df.iterrows(), start=1):
            nation = _clean(row.iloc[nc])
            if not nation or "total" in nation.lower() or nation.lower() == "nan":
                continue
            gold, silver, bronze = _int(row.iloc[g]), _int(row.iloc[s]), _int(row.iloc[b])
            total = _int(row.iloc[tc]) if tc >= 0 else gold + silver + bronze
            rows.append(
                {"rank": i, "nation": nation, "gold": gold, "silver": silver,
                 "bronze": bronze, "total": total}
            )
        if len(rows) > len(best):
            best = rows
    return best


def fetch_sea_alltime() -> list[dict[str, object]]:
    """Jadual pingat semua-masa SEA Games (ikut negara). [] jika gagal/tiada pandas."""
    if pd is None:
        return []
    try:
        return parse_medal_table(_get(_ALLTIME_SEA))
    except Exception:
        return []
