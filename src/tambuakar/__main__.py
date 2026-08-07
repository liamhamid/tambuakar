"""Titik masuk CLI: `python -m tambuakar` — jalankan satu kitaran kutipan.

Guna oleh GitHub Actions (cron) nanti. Simpan hasil ke `./data`.
"""

from __future__ import annotations

from pathlib import Path

from .pipeline import run
from .sources.wikidata import WikidataSource


def main() -> None:
    source = WikidataSource(limit=50)
    stats = run(source, Path("data"))
    print(f"[tambuakar] {source.name}: fetched {stats['fetched']}, silver {stats['silver']}")


if __name__ == "__main__":
    main()
