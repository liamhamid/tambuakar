"""Ujian untuk kalendar temasya sukan (unjuran ke hadapan) — tiada rangkaian."""

from __future__ import annotations

from datetime import date

from tambuakar.events import upcoming


def test_upcoming_sorted_and_within_horizon() -> None:
    rows = upcoming(date(2026, 8, 1), horizon_months=24)
    assert rows, "sepatutnya ada acara akan datang"
    # Tersusun ikut (tahun, bulan).
    keys = [(r["year"], r["month"] or 6) for r in rows]
    assert keys == sorted(keys)
    # Semua dalam horizon (<= 2028-08).
    for r in rows:
        assert (2026, 8) <= (r["year"], r["month"] or 6) <= (2028, 8)


def test_sea_games_2027_present() -> None:
    rows = upcoming(date(2026, 8, 1), horizon_months=24)
    names = [str(r["name"]) for r in rows]
    assert any("SEA Games" in n for n in names)


def test_annual_rolls_to_next_year_when_month_passed() -> None:
    # Pada Dis 2026, Malaysia Open (Jan) sepatutnya jatuh pada Jan 2027.
    rows = upcoming(date(2026, 12, 1), horizon_months=6)
    mo = [r for r in rows if "Malaysia Open" in str(r["name"])]
    assert mo and mo[0]["year"] == 2027 and mo[0]["month"] == 1


def test_biennial_sukma_projects_forward() -> None:
    rows = upcoming(date(2026, 1, 1), horizon_months=24)
    sukma = [r for r in rows if r["name"] == "SUKMA"]
    assert sukma and sukma[0]["year"] == 2026  # anchor 2024 -> 2026
