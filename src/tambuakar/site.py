"""Site — bina ringkasan awam (Layer A) dari entiti Gold untuk papan pemuka.

Purpose: tukar entiti kanonik (hasil IRE) jadi satu payload JSON ringkas &
    selamat-klien yang page statik (IMPAX) boleh baca terus — tiada rahsia,
    tiada data mentah, tiada data peribadi (Layer B kekal berasingan).
Responsibilities: agregat KPI, pilih & susun entiti teratas, sertakan berita
    (deal) terkini per-entiti. Fungsi tulen (mudah diuji, tiada I/O).
Dependencies: pustaka standard sahaja.
Future: sertakan siri masa trend bila nilai Google Trends dikekalkan; benchmark
    nilai media (bila kaedah dipersetujui); tapisan ikut projek/klien.
"""

from __future__ import annotations

from .identity import ENTITY_KINDS, Entity

# Kind yang dikira sebagai "pasukan" untuk KPI (kelab/liga/pasukan).
_TEAM_KINDS = frozenset({"football_club", "team", "league"})
_MAX_ENTITIES = 6
_MAX_NEWS = 3


def _news_of(entity: Entity) -> list[dict[str, str]]:
    """Berita (deal) terkini untuk satu entiti, terbaru dahulu."""
    news = [m for m in entity.mentions if m.get("kind") == "news"]
    # `seendate` GDELT = "YYYYMMDDTHHMMSSZ" -> susun rentetan = susun masa.
    news.sort(key=lambda m: m.get("seendate", ""), reverse=True)
    out: list[dict[str, str]] = []
    for m in news[:_MAX_NEWS]:
        out.append(
            {
                "title": m.get("ref", ""),
                "domain": m.get("domain", ""),
                "seen": m.get("seendate", ""),
            }
        )
    return out


def _rank(entity: Entity) -> tuple[int, int, int]:
    news = sum(1 for m in entity.mentions if m.get("kind") == "news")
    # Utamakan entiti paling aktif: banyak sumber, banyak mention (minat+berita),
    # banyak berita. Seri dikekalkan ikut susunan input (Wikidata sudah tertib
    # keterkenalan) — `sorted` stabil, jadi kelab besar kekal di atas.
    return (len(entity.sources), len(entity.mentions), news)


def build_site(entities: list[Entity], *, generated_at: str) -> dict[str, object]:
    """Bina payload awam Layer A. Fungsi tulen — tiada rangkaian/fail.

    `generated_at`: cap masa (dibekalkan oleh pemanggil, cth ISO date).
    Susunan `entities` dianggap mengikut keterkenalan (sumber utama tertibkan).
    """
    real_entities = [e for e in entities if e.kind in ENTITY_KINDS]
    deals = sum(
        1 for e in entities for m in e.mentions if m.get("kind") == "news"
    )
    teams = sum(1 for e in real_entities if e.kind in _TEAM_KINDS)
    # Hanya sumber yang benar-benar menyumbang data (bukan sekadar dikonfigur).
    present_sources = sorted({s for e in entities for s in e.sources})

    ranked = sorted(real_entities, key=_rank, reverse=True)[:_MAX_ENTITIES]
    entity_cards: list[dict[str, object]] = []
    for e in ranked:
        entity_cards.append(
            {
                "name": e.canonical_name,
                "kind": e.kind,
                "sources": sorted(e.sources),
                "country": e.attrs.get("country", ""),
                "news": _news_of(e),
                "deals": sum(1 for m in e.mentions if m.get("kind") == "news"),
            }
        )

    return {
        "generated_at": generated_at,
        "kpis": {
            "entities": len(real_entities),
            "deals": deals,
            "sources": len(present_sources),
            "teams": teams,
        },
        "sources": present_sources,
        "entities": entity_cards,
    }
