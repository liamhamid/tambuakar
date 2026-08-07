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
      wikidata.py       # adapter #1: kelab bola sepak (SPARQL, 🟢 CC0, tiada API key)
    medallion.py        # Bronze (mentah) + Silver (dedup/normalisasi), JSONL
    pipeline.py         # orkestrasi: fetch -> Bronze -> Silver
    __main__.py         # CLI: `python -m tambuakar`
  tests/                # ujian offline (tiada rangkaian)
  collect.yml.template  # templat GitHub Actions (cron) — aktif bila repo sendiri
```

## Jalankan (setempat)

```bash
# Ujian (offline, tiada rangkaian):
PYTHONPATH=tambuakar/src python -m pytest tambuakar/tests -q

# Satu kitaran kutipan sebenar (perlu internet) -> tulis ke ./data:
PYTHONPATH=tambuakar/src python -m tambuakar
```

## Status & seterusnya

- ✅ v1: port + adapter Wikidata + Medallion (Bronze/Silver) + ujian.
- ⏭️ Sumber: **GDELT** (berita/deal), **Google Trends** (`pytrends`).
- ⏭️ **Identity Resolution Engine** (entiti dulu: `rapidfuzz` + deterministik).
- ⏭️ **Gold** + Serving API (FastAPI) + sambung Ajis (read-only, Tailscale).
- ⏭️ Layer B (Person/CDP) — hanya bila consent sedia (lihat `../BLUEPRINT-TAMBUAKAR-LAYER-B.md`).

## Prinsip (dikunci)

- **Sumber SAH sahaja** + provenance (tag 🟢 boleh-jual / 🟡 rujukan-dalaman).
- **Percuma dulu** (pure-Python, GitHub Actions). Naik kos bila terbukti berbaloi.
- **Tak kacau Ajis**, **bukan Forge** (wilayah DIONE), **jangan gabung paksa**.
