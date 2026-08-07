"""Analysis (Tier 1) — isyarat AI tempatan: sentimen + momentum.

Purpose: beri "otak" ringan pada setiap entiti tanpa kos/AI luar — sentimen
    berita (leksikon) + skor momentum (jangkauan + buzz terkini). Ini tapak
    untuk tangga AI seterusnya (insight bahasa, padanan, ramalan).
Method: sentimen = kira perkataan positif/negatif dalam tajuk berita (leksikon
    dwibidang sukan/pemasaran). Momentum = asas jangkauan (keterkenalan, skala
    log) + buzz (bilangan berita/trend terkini). Fungsi tulen, 100% tempatan.
Dependencies: pustaka standard sahaja (`re`, `math`). Tiada model luar, tiada kos.
Future: model transformer kecil untuk sentimen; buzz berpemberat-masa sebenar;
    momentum relatif-mingguan bila sejarah trend dikekalkan.
"""

from __future__ import annotations

import math
import re

from .identity import Entity

# Leksikon ringkas, ditala untuk berita sukan/pemasaran.
_POS = frozenset(
    {
        "win", "wins", "won", "victory", "champion", "champions", "title", "sign",
        "signs", "signed", "deal", "sponsor", "sponsors", "sponsorship", "partner",
        "partners", "partnership", "boost", "record", "star", "glory", "promoted",
        "promotion", "unbeaten", "triumph", "success", "extend", "renew", "renews",
        "launch", "launches", "top", "surge", "rise", "growth", "clinch", "secure",
    }
)
_NEG = frozenset(
    {
        "loss", "lose", "lost", "defeat", "sack", "sacked", "ban", "banned",
        "scandal", "injury", "injured", "crisis", "relegated", "relegation", "debt",
        "fine", "fined", "drop", "decline", "controversy", "suspended", "axed",
        "exit", "terminate", "fail", "fails", "protest", "boycott", "row", "slump",
    }
)


def sentiment(texts: list[str]) -> dict[str, object]:
    """Sentimen agregat merentas beberapa tajuk. `none` bila tiada teks."""
    if not texts:
        return {"label": "none", "score": 0.0, "pos": 0, "neg": 0}
    pos = neg = 0
    for text in texts:
        for word in re.findall(r"[a-z']+", text.lower()):
            if word in _POS:
                pos += 1
            elif word in _NEG:
                neg += 1
    total = pos + neg
    if total == 0:
        return {"label": "neutral", "score": 0.0, "pos": 0, "neg": 0}
    score = round((pos - neg) / total, 2)
    label = "positive" if score > 0.15 else "negative" if score < -0.15 else "neutral"
    return {"label": label, "score": score, "pos": pos, "neg": neg}


def momentum(entity: Entity, *, max_prominence: int) -> dict[str, object]:
    """Skor 0-100: asas jangkauan (keterkenalan, log) + buzz (berita/trend)."""
    news = sum(1 for m in entity.mentions if m.get("kind") == "news")
    trends = sum(1 for m in entity.mentions if m.get("kind") == "trend")
    try:
        prominence = int(entity.attrs.get("prominence", "0") or 0)
    except ValueError:
        prominence = 0
    reach = 0.0
    if max_prominence > 0 and prominence > 0:
        reach = 60.0 * (math.log1p(prominence) / math.log1p(max_prominence))
    buzz = min(40, news * 10 + trends * 4)
    score = int(round(min(100.0, reach + buzz)))
    return {"score": score, "trend": "up" if buzz >= 10 else "flat", "buzz": buzz, "news": news}


def analyse(entity: Entity, *, max_prominence: int) -> dict[str, object]:
    """Gabung sentimen + momentum untuk satu entiti (untuk lapisan sajian)."""
    titles = [m.get("ref", "") for m in entity.mentions if m.get("kind") == "news"]
    return {
        "sentiment": sentiment(titles),
        "momentum": momentum(entity, max_prominence=max_prominence),
    }
