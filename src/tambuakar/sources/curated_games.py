"""Sumber terkurasi — sejarah PENUH edisi SEA Games (tahun + tuan rumah).

Purpose: senarai edisi yang lengkap & tepat (deterministik) — lebih boleh
    dipercayai daripada scrape buta untuk senarai sejarah yang terhad & diketahui.
    Bergabung dengan sumber Wikidata/Wikipedia melalui IRE (edisi sama = 1 entiti).
Method: daftar edisi SEA Games 1959–2027 (SEAP Games 1959–75 → SEA Games 1977+).
Dependencies: pustaka standard sahaja. Tiada rangkaian, tiada kos.
Future: SUKMA penuh bila hos disahkan; pingat via sumber rasmi/MASOC.
"""

from __future__ import annotations

from ..ports import Record

_SERIES = "Southeast Asian Games"

# (tahun, negara tuan rumah) — 34 edisi. 1963 dibatalkan (tiada edisi).
_SEA_GAMES: list[tuple[int, str]] = [
    (1959, "Thailand"), (1961, "Myanmar"), (1965, "Malaysia"), (1967, "Thailand"),
    (1969, "Myanmar"), (1971, "Malaysia"), (1973, "Singapore"), (1975, "Thailand"),
    (1977, "Malaysia"), (1979, "Indonesia"), (1981, "Philippines"), (1983, "Singapore"),
    (1985, "Thailand"), (1987, "Indonesia"), (1989, "Malaysia"), (1991, "Philippines"),
    (1993, "Singapore"), (1995, "Thailand"), (1997, "Indonesia"), (1999, "Brunei"),
    (2001, "Malaysia"), (2003, "Vietnam"), (2005, "Philippines"), (2007, "Thailand"),
    (2009, "Laos"), (2011, "Indonesia"), (2013, "Myanmar"), (2015, "Singapore"),
    (2017, "Malaysia"), (2019, "Philippines"), (2021, "Vietnam"), (2023, "Cambodia"),
    (2025, "Thailand"), (2027, "Malaysia"),
]


class CuratedGamesSource:
    """Sumber edisi SEA Games terkurasi (sejarah penuh, deterministik)."""

    name = "curated_games"

    def fetch(self) -> list[Record]:
        out: list[Record] = []
        for year, host in _SEA_GAMES:
            out.append(
                Record(
                    source="curated_games",
                    source_id=f"{_SERIES}:{year}",
                    kind="games_edition",
                    name=f"{year} {_SERIES}",
                    attrs={"year": str(year), "host": host, "series": _SERIES},
                )
            )
        return out
