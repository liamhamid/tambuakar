"""Ujian untuk modul analisis Tier 1 (sentimen + momentum) — tempatan, tiada rangkaian."""

from __future__ import annotations

from tambuakar.analysis import analyse, momentum, sentiment
from tambuakar.identity import Entity


def test_sentiment_positive_negative_none() -> None:
    assert sentiment([])["label"] == "none"
    assert sentiment(["Club signs record sponsorship deal, boost for fans"])["label"] == "positive"
    assert sentiment(["Coach sacked after defeat and injury crisis"])["label"] == "negative"
    assert sentiment(["Club plays match on Sunday"])["label"] == "neutral"


def _ent(name: str, prominence: str, news: int = 0) -> Entity:
    e = Entity(entity_id="x", kind="football_club", canonical_name=name)
    e.attrs["prominence"] = prominence
    for i in range(news):
        e.mentions.append({"kind": "news", "ref": f"headline {i}"})
    return e


def _score(entity: Entity, max_prominence: int) -> int:
    s = momentum(entity, max_prominence=max_prominence)["score"]
    assert isinstance(s, int)
    return s


def test_momentum_scales_with_prominence_and_buzz() -> None:
    big = _score(_ent("Big", "100"), 100)
    small = _score(_ent("Small", "5"), 100)
    assert 0 <= small < big <= 100
    # Berita terkini menaikkan buzz + tanda "up".
    buzzy = momentum(_ent("Buzzy", "100", news=3), max_prominence=100)
    assert buzzy["trend"] == "up"
    assert _score(_ent("Buzzy", "100", news=3), 100) >= big


def test_momentum_handles_zero_and_bad_prominence() -> None:
    assert momentum(_ent("None", "0"), max_prominence=0)["score"] == 0
    assert momentum(_ent("Bad", "abc"), max_prominence=100)["score"] == 0


def test_analyse_shape() -> None:
    out = analyse(_ent("JDT", "80", news=1), max_prominence=80)
    assert set(out) == {"sentiment", "momentum"}
    sent = out["sentiment"]
    mom = out["momentum"]
    assert isinstance(sent, dict) and isinstance(mom, dict)
    assert "score" in mom and "label" in sent
