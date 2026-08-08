"""Ujian untuk profil audiens sukan (struktur & liputan) — tiada rangkaian."""

from __future__ import annotations

from tambuakar.sport_audience import SPORTS_AUDIENCE, profiles


def test_profiles_shape_and_bilingual() -> None:
    ps = profiles()
    assert len(ps) == len(SPORTS_AUDIENCE)
    for p in ps:
        assert p["key"] and p["pop"]
        for lang in ("en", "ms"):
            block = p[lang]
            assert isinstance(block, dict)
            for field in ("sport", "age", "gender", "communities", "regions", "also"):
                assert block.get(field), f"{p['key']} missing {lang}.{field}"


def test_core_sports_present() -> None:
    keys = set(SPORTS_AUDIENCE)
    for want in ("football", "badminton", "takraw", "running"):
        assert want in keys
