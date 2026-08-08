"""Ujian offline untuk parser jadual Wikipedia (edisi Games) — tiada rangkaian."""

from __future__ import annotations

import pytest

pytest.importorskip("pandas")

from tambuakar.sources.wikipedia_games import WikipediaGamesSource  # noqa: E402

_SEA_HTML = """
<table class="wikitable">
<tr><th>Year</th><th>Edition</th><th>Host city</th><th>Host country</th><th>Dates</th></tr>
<tr><td>1959</td><td>I</td><td>Bangkok</td><td>Thailand</td><td>12 Dec</td></tr>
<tr><td>2017[a]</td><td>29th</td><td>Kuala Lumpur</td><td>Malaysia</td><td>Aug</td></tr>
<tr><td>2027</td><td>34th</td><td>Kuala Lumpur</td><td>Malaysia</td><td>Sep</td></tr>
</table>
<table class="wikitable"><tr><th>Rank</th><th>Nation</th><th>Gold</th></tr>
<tr><td>1</td><td>Thailand</td><td>100</td></tr></table>
"""


def test_parses_editions_and_skips_medal_table() -> None:
    recs = WikipediaGamesSource._editions(_SEA_HTML, "Southeast Asian Games")
    years = {r.attrs["year"] for r in recs}
    assert years == {"1959", "2017", "2027"}  # 3 edisi; jadual pingat dilangkau
    rec = next(r for r in recs if r.attrs["year"] == "2017")
    assert rec.kind == "games_edition"
    assert rec.attrs["host"] == "Malaysia"  # footnote [a] dibersihkan
    assert rec.name == "2017 Southeast Asian Games"


def test_host_state_column() -> None:
    html = (
        '<table class="wikitable"><tr><th>Year</th><th>Host state</th></tr>'
        "<tr><td>2024</td><td>Sarawak</td></tr></table>"
    )
    recs = WikipediaGamesSource._editions(html, "Sukma Games")
    assert len(recs) == 1 and recs[0].attrs["host"] == "Sarawak"
