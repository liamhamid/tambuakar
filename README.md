# Tambuakar 🐉 — Enjin Kepintaran Data Sukan Dunia

> **Layer A v1** — kutip + susun data sukan/pemasaran dunia dari sumber sah,
> susun ikut **Medallion** (Bronze → Silver → Gold), sedia untuk Identity
> Resolution & Ajis. Modul ini **berasingan** dari Ajis (`aicto`) — tiada
> pergantungan dua hala; ia akan dipindah ke **repo sendiri** di fasa deploy.

Rujuk pelan penuh: `../BLUEPRINT-TAMBUAKAR.md` · flow: artifact di GUMUM-TASKS.

## Struktur

```
tambuakar/
  src/tambuakar/
    ports.py            # port KnowledgeSource + Record (Clean Architecture)
    sources/
      wikidata.py       # kelab bola sepak (SPARQL, 🟢 CC0, tiada API key)
      gdelt.py          # berita/deal global (GDELT DOC 2.0, 🟢, tiada API key)
      google_trends.py  # minat audiens (pytrends, 🟢) — import dilindungi
    medallion.py        # Bronze (mentah) + Silver (dedup/normalisasi), JSONL
    identity.py         # Identity Resolution Engine (IRE): satukan entiti sama
    gold.py             # Gold: profil entiti bersatu + identity_map (JSONL)
    pipeline.py         # orkestrasi: fetch -> Bronze -> Silver -> IRE -> Gold
    __main__.py         # CLI: `python -m tambuakar` (jalan semua sumber)
  tests/                # ujian offline (tiada rangkaian)
  requirements.txt      # deps pihak ketiga (pytrends); teras = stdlib sahaja
  collect.yml.template  # templat GitHub Actions (cron) — aktif bila repo sendiri
```

## Jalankan (setempat)

```bash
# Ujian (offline, tiada rangkaian):
PYTHONPATH=tambuakar/src python -m pytest tambuakar/tests -q

# (Pilihan) pasang deps pihak ketiga untuk Google Trends:
pip install -r tambuakar/requirements.txt

# Satu kitaran kutipan sebenar (perlu internet) -> tulis ke ./data:
PYTHONPATH=tambuakar/src python -m tambuakar
```

## Status & seterusnya

- ✅ v1: adapter **Wikidata + GDELT + Google Trends** + Medallion (Bronze/Silver,
  multi-sumber, resilient) + **IRE** (entiti: deterministik + fuzzy difflib) + **Gold**
  (profil bersatu + identity_map) + 9 ujian.
- ⏭️ **Serving API** (FastAPI) + sambung Ajis (read-only, Tailscale).
- ⏭️ Alias/abbreviation untuk IRE ("Man Utd" = "Manchester United"); swap ke `rapidfuzz`.
- ⏭️ Layer B (Person/CDP) — hanya bila consent sedia (lihat `../BLUEPRINT-TAMBUAKAR-LAYER-B.md`).

## Prinsip (dikunci)

- **Sumber SAH sahaja** + provenance (tag 🟢 boleh-jual / 🟡 rujukan-dalaman).
- **Percuma dulu** (pure-Python, GitHub Actions). Naik kos bila terbukti berbaloi.
- **Tak kacau Ajis**, **bukan Forge** (wilayah DIONE), **jangan gabung paksa**.
