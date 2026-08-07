"""Publish — jalankan satu kitaran kutipan lalu tulis ringkasan awam untuk page.

Purpose: titik masuk yang GitHub Actions guna untuk menjadikan papan pemuka IMPAX
    "hidup": kutip Layer A (Wikidata/GDELT/Google Trends) -> Gold -> tulis
    `docs/data.json` (selamat-klien) yang page statik baca.
Responsibilities: pilih sumber, orkestrasi kutipan, serialisasi payload site.
Dependencies: pustaka standard + modul tempatan.
Future: parameter query per-projek/klien; tulis banyak fail (per-klien).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .pipeline import collect
from .ports import KnowledgeSource
from .site import build_site
from .sources.gdelt import GdeltSource
from .sources.google_trends import GoogleTrendsSource
from .sources.wikidata import WikidataSource


def _sources() -> list[KnowledgeSource]:
    # Fokus pasaran Sportswork: kelab Malaysia + minat audiens kelab utama.
    return [
        WikidataSource(limit=60),
        GdeltSource(
            query=(
                '("Johor Darul Ta\'zim" OR "Selangor FC" OR "Kedah Darul Aman" OR '
                '"Terengganu FC" OR "Malaysia Super League") '
                "(sponsor OR sponsorship OR partnership OR kit OR deal)"
            ),
            max_records=75,
            retries=4,
            backoff=3.0,
        ),
        GoogleTrendsSource(
            terms=[
                "Johor Darul Ta'zim",
                "Selangor FC",
                "Kedah Darul Aman FC",
                "Terengganu FC",
            ],
            geo="MY",
        ),
    ]


def main(out: Path | None = None, data_dir: Path | None = None) -> dict[str, object]:
    """Kutip -> Gold -> tulis payload site. Pulang payload (untuk ujian)."""
    out = out or Path("docs/data.json")
    data_dir = data_dir or Path("data")
    sources = _sources()
    entities, results = collect(sources, data_dir)
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    payload = build_site(entities, generated_at=generated, connectors=len(sources))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, stats in results.items():
        print(f"[tambuakar] {name}: {stats}")
    print(f"[tambuakar] site -> {out} kpis={payload['kpis']}")
    return payload


if __name__ == "__main__":
    main()
