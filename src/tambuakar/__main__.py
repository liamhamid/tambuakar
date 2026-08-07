"""Titik masuk CLI: `python -m tambuakar` — jalankan satu kitaran semua sumber.

Guna oleh GitHub Actions (cron) nanti. Simpan hasil ke `./data`. Sumber yang
gagal (cth Google Trends tanpa pytrends) dilaporkan, tidak menjatuhkan yang lain.
"""

from __future__ import annotations

from pathlib import Path

from .pipeline import run_all
from .ports import KnowledgeSource
from .sources.gdelt import GdeltSource
from .sources.google_trends import GoogleTrendsSource
from .sources.wikidata import WikidataSource


def main() -> None:
    sources: list[KnowledgeSource] = [
        WikidataSource(limit=50),
        GdeltSource(query="sports sponsorship", max_records=50),
        GoogleTrendsSource(terms=["Manchester United", "Johor Darul Ta'zim"], geo="MY"),
    ]
    results = run_all(sources, Path("data"))
    for name, stats in results.items():
        print(f"[tambuakar] {name}: {stats}")


if __name__ == "__main__":
    main()
