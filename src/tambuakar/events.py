"""Events — kalendar temasya sukan Malaysia (terdepan / forward-looking).

Purpose: jawab "apa temasya sukan akan datang?" — daripada Games besar (SEA Games,
    SUKMA) hingga acara kecil (larian, basikal, badminton, takraw, motorsport).
Method: daftar acara berulang (cadence tahunan/dwitahunan/sekali) + unjuran tarikh
    ke hadapan dari "hari ini". Fungsi tulen — auto-roll setiap kitaran kutipan,
    jadi senarai "akan datang" sentiasa terkini tanpa sentuhan manusia.
Dependencies: pustaka standard (`datetime`, `dataclasses`) sahaja. Tiada rangkaian.
Future: gabung feed rasmi (MASOC untuk SEA Games 2027) + scraper aggregator larian/
    basikal untuk acara kecil yang tiada dalam daftar ini (perlu server — Fasa 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

_MONTHS = ["", "Jan", "Feb", "Mac", "Apr", "Mei", "Jun", "Jul", "Ogos", "Sep", "Okt", "Nov", "Dis"]


@dataclass(frozen=True)
class Event:
    """Satu acara berulang/sekali dalam kalendar sukan Malaysia."""

    name: str
    sport: str
    category: str  # games | running | cycling | racket | takraw | football | motorsport | multisport | other
    level: str  # international | national | state | grassroots
    scope: str  # lokasi/liputan, cth "Kuala Lumpur", "Kebangsaan"
    month: int  # bulan lazim 1-12 (0 = belum pasti / TBC)
    cadence: str  # annual | biennial | oneoff
    anchor: int  # tahun rujukan edisi diketahui (biennial), atau tahun tetap (oneoff)


# Daftar acara — kecil hingga besar, merentas sukan. Bulan = anggaran lazim.
EVENTS: list[Event] = [
    Event("Sukan SEA (SEA Games)", "multi-sukan", "games", "international", "Kuala Lumpur (tuan rumah)", 8, "oneoff", 2027),
    Event("SUKMA", "multi-sukan", "games", "national", "Kebangsaan (negeri lawan negeri)", 8, "biennial", 2024),
    Event("Para SUKMA", "multi-sukan (para)", "games", "national", "Kebangsaan", 9, "biennial", 2024),
    Event("Sukan Universiti (MASUM)", "multi-sukan", "multisport", "national", "Universiti awam", 4, "annual", 0),
    Event("MSSM (Sukan Sekolah)", "multi-sukan", "multisport", "national", "Sekolah kebangsaan", 6, "annual", 0),
    Event("Malaysia Open (Badminton, BWF S1000)", "badminton", "racket", "international", "Axiata Arena, KL", 1, "annual", 0),
    Event("Malaysia Masters (Badminton, BWF S500)", "badminton", "racket", "international", "Malaysia", 5, "annual", 0),
    Event("Le Tour de Langkawi", "berbasikal", "cycling", "international", "Jelajah kebangsaan", 3, "annual", 0),
    Event("KL Century Ride (Basikal)", "berbasikal", "cycling", "national", "Kuala Lumpur", 7, "annual", 0),
    Event("Sepak Takraw League (STL)", "sepak takraw", "takraw", "national", "Kebangsaan", 3, "annual", 0),
    Event("ISTAF SuperSeries (Takraw)", "sepak takraw", "takraw", "international", "Malaysia", 7, "annual", 0),
    Event("Standard Chartered KL Marathon", "larian", "running", "international", "Kuala Lumpur", 10, "annual", 0),
    Event("Penang Bridge International Marathon", "larian", "running", "international", "Pulau Pinang", 11, "annual", 0),
    Event("Borneo International Marathon", "larian", "running", "national", "Kota Kinabalu, Sabah", 5, "annual", 0),
    Event("Putrajaya Night Marathon", "larian", "running", "national", "Putrajaya", 11, "annual", 0),
    Event("Ironman Malaysia (Triatlon)", "triatlon", "running", "international", "Langkawi", 11, "annual", 0),
    Event("Powerman Malaysia (Duatlon)", "duatlon", "running", "international", "Malaysia", 3, "annual", 0),
    Event("Liga Super Malaysia (mula musim)", "bola sepak", "football", "national", "Kebangsaan", 5, "annual", 0),
    Event("Piala Malaysia (Final)", "bola sepak", "football", "national", "Kebangsaan", 12, "annual", 0),
    Event("Malaysian Grand Prix (MotoGP, Sepang)", "motosikal", "motorsport", "international", "Sepang", 11, "annual", 0),
    Event("Sepang 1000KM (Ketahanan)", "kereta lumba", "motorsport", "national", "Sepang", 12, "annual", 0),
    Event("Monsoon Cup (Pelayaran)", "pelayaran", "watersport", "international", "Terengganu", 11, "annual", 0),
    Event("Piala Sultan Azlan Shah (Hoki)", "hoki", "hockey", "international", "Ipoh, Perak", 5, "annual", 0),
    Event("Liga Hoki Malaysia (MHL)", "hoki", "hockey", "national", "Kebangsaan", 1, "annual", 0),
    Event("Maybank Championship (Golf)", "golf", "golf", "international", "Kuala Lumpur", 4, "annual", 0),
    Event("Kejohanan Squash Kebangsaan", "skuasy", "squash", "national", "Kebangsaan", 6, "annual", 0),
    Event("Kejohanan Boling Kebangsaan", "boling", "bowling", "national", "Kebangsaan", 9, "annual", 0),
    Event("MIMMA (Seni Bela Diri Campuran)", "MMA", "combat", "national", "Kebangsaan", 8, "annual", 0),
    Event("Piala Sumbangsih (Bola Sepak)", "bola sepak", "football", "national", "Kebangsaan", 2, "annual", 0),
    Event("Piala FA Malaysia (Final)", "bola sepak", "football", "national", "Kebangsaan", 7, "annual", 0),
    Event("Kuching Marathon", "larian", "running", "national", "Kuching, Sarawak", 8, "annual", 0),
    Event("Larian Merdeka", "larian", "running", "grassroots", "Kebangsaan", 8, "annual", 0),
    Event("The Most Beautiful Thing (TMBT) Ultra", "larian trail", "running", "national", "Sabah", 9, "annual", 0),
    Event("Ironman 70.3 Desaru Coast", "triatlon", "running", "international", "Desaru, Johor", 9, "annual", 0),
    Event("Great Eastern Women's Run", "larian", "running", "national", "Kuala Lumpur", 11, "annual", 0),
    Event("OCBC Cycle Malaysia", "berbasikal", "cycling", "national", "Kuala Lumpur", 6, "annual", 0),
    Event("Kejohanan Olahraga Terbuka Malaysia", "olahraga", "athletics", "national", "Kebangsaan", 6, "annual", 0),
    Event("Kejohanan Renang Kebangsaan", "renang", "watersport", "national", "Kebangsaan", 4, "annual", 0),
]


def _next_year(ev: Event, y: int, m: int) -> int:
    """Tahun kejadian seterusnya bagi acara, pada/selepas (y, m). 0 jika tamat."""
    if ev.cadence == "oneoff":
        return ev.anchor if ev.anchor >= y else 0
    if ev.cadence == "annual":
        # Bulan sudah lepas tahun ini -> tahun depan. Bulan 0 (TBC) -> tahun ini.
        return y if (ev.month == 0 or ev.month >= m) else y + 1
    # biennial: melangkah 2 tahun dari edisi rujukan sehingga >= sekarang.
    yr = ev.anchor or y
    while yr < y or (yr == y and ev.month and ev.month < m):
        yr += 2
    return yr


def _label(month: int, year: int) -> str:
    return f"{_MONTHS[month]} {year}" if month else f"{year} (TBC)"


def upcoming(today: date, horizon_months: int = 24) -> list[dict[str, object]]:
    """Acara akan datang dalam tempoh `horizon_months`, tersusun ikut tarikh."""
    y, m = today.year, today.month
    out: list[dict[str, object]] = []
    for ev in EVENTS:
        ny = _next_year(ev, y, m)
        if not ny:
            continue
        mm = ev.month or 6  # untuk susunan bila TBC
        delta = (ny - y) * 12 + (mm - m)
        if delta < 0 or delta > horizon_months:
            continue
        out.append(
            {
                "name": ev.name,
                "sport": ev.sport,
                "category": ev.category,
                "level": ev.level,
                "scope": ev.scope,
                "year": ny,
                "month": ev.month,
                "when": _label(ev.month, ny),
            }
        )
    out.sort(key=lambda e: (e["year"], e["month"] or 6, e["name"]))
    return out
