"""Ujian offline untuk parser jadual pingat (SEA Games) — tiada rangkaian."""

from __future__ import annotations

import pytest

pytest.importorskip("pandas")

from tambuakar.medals import parse_medal_table  # noqa: E402

_MEDAL_HTML = """
<table class="wikitable">
<tr><th>Rank</th><th>Nation</th><th>Gold</th><th>Silver</th><th>Bronze</th><th>Total</th></tr>
<tr><td>1</td><td>Thailand</td><td>2,438</td><td>2,182</td><td>2,144</td><td>6,764</td></tr>
<tr><td>2</td><td>Indonesia</td><td>1,865</td><td>1,819</td><td>2,001</td><td>5,685</td></tr>
<tr><td>3</td><td>Malaysia</td><td>1,376</td><td>1,411</td><td>1,838</td><td>4,625</td></tr>
<tr><td></td><td>Total</td><td>10000</td><td>10000</td><td>10000</td><td>30000</td></tr>
</table>
"""


def test_parses_nations_and_skips_total() -> None:
    rows = parse_medal_table(_MEDAL_HTML)
    assert len(rows) == 3  # baris "Total" dilangkau
    nations = [r["nation"] for r in rows]
    assert nations == ["Thailand", "Indonesia", "Malaysia"]
    my = next(r for r in rows if r["nation"] == "Malaysia")
    assert my["gold"] == 1376  # koma dibersihkan
    assert my["silver"] == 1411
    assert my["bronze"] == 1838
    assert my["total"] == 4625
    assert my["rank"] == 3


def test_total_computed_when_column_absent() -> None:
    html = (
        '<table class="wikitable">'
        "<tr><th>Rank</th><th>Nation</th><th>Gold</th><th>Silver</th><th>Bronze</th></tr>"
        "<tr><td>1</td><td>Malaysia</td><td>10</td><td>5</td><td>2</td></tr></table>"
    )
    rows = parse_medal_table(html)
    assert len(rows) == 1
    assert rows[0]["total"] == 17  # 10+5+2 bila tiada lajur Total


def test_ignores_tables_without_medal_columns() -> None:
    html = (
        '<table class="wikitable"><tr><th>Year</th><th>Host</th></tr>'
        "<tr><td>2027</td><td>Malaysia</td></tr></table>"
    )
    assert parse_medal_table(html) == []
