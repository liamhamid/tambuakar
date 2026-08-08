"""Sport audience — profil audiens per-sukan di Malaysia (siapa suka, umur, kaum).

Purpose: jawab "sukan ni siapa peminatnya?" — umur, jantina, komuniti, wilayah,
    dan sukan lain yang mereka ikut. Untuk penaja padankan jenama ke audiens sukan.
Method: garis dasar (baseline) berpandukan corak budaya sukan Malaysia yang dikenali
    umum. Ini ANGGARAN ARAH — diperhalusi dengan data sebenar: survey first-party
    (Layer B), IYRES (penglibatan sukan belia), DOSM (demografi), + analitik sosial
    (cth YouTube Julang). Segmen agregat sahaja — tiada individu (patuh PDPA).
Dependencies: pustaka standard sahaja. Tiada rangkaian.
Future: ganti baseline dengan data survey/IYRES sebenar; tambah lebih sukan.
"""

from __future__ import annotations

# key: {pop, en:{...}, ms:{...}}. Nilai ringkas & boleh-baca; ditanda "baseline".
SPORTS_AUDIENCE: dict[str, dict[str, object]] = {
    "football": {"pop": "#1 most followed",
        "en": {"sport": "Football", "age": "All ages (16–45 core)", "gender": "Male-leaning",
               "communities": "Broad — all communities", "regions": "Nationwide",
               "also": "Futsal · European leagues"},
        "ms": {"sport": "Bola sepak", "age": "Semua umur (teras 16–45)", "gender": "Cenderung lelaki",
               "communities": "Luas — semua kaum", "regions": "Seluruh negara",
               "also": "Futsal · liga Eropah"}},
    "badminton": {"pop": "#2 · national pride",
        "en": {"sport": "Badminton", "age": "All ages", "gender": "Balanced",
               "communities": "Very broad — strong Chinese & Malay", "regions": "Nationwide, urban strong",
               "also": "Football · table tennis"},
        "ms": {"sport": "Badminton", "age": "Semua umur", "gender": "Seimbang",
               "communities": "Sangat luas — kuat Cina & Melayu", "regions": "Seluruh negara, kuat bandar",
               "also": "Bola sepak · ping pong"}},
    "takraw": {"pop": "Traditional heartland",
        "en": {"sport": "Sepak takraw", "age": "25–55 core", "gender": "Male-leaning",
               "communities": "Strong Malay · rural/kampung", "regions": "East coast · northern states",
               "also": "Football · grassroots sports"},
        "ms": {"sport": "Sepak takraw", "age": "Teras 25–55", "gender": "Cenderung lelaki",
               "communities": "Kuat Melayu · luar bandar/kampung", "regions": "Pantai timur · negeri utara",
               "also": "Bola sepak · sukan akar umbi"}},
    "running": {"pop": "Fast-growing mass participation",
        "en": {"sport": "Running / marathon", "age": "25–45", "gender": "Balanced (female growing)",
               "communities": "Broad · urban middle-class", "regions": "KL · PJ · Penang · JB",
               "also": "Cycling · gym & fitness"},
        "ms": {"sport": "Larian / maraton", "age": "25–45", "gender": "Seimbang (wanita meningkat)",
               "communities": "Luas · kelas menengah bandar", "regions": "KL · PJ · Pulau Pinang · JB",
               "also": "Berbasikal · gim & kecergasan"}},
    "cycling": {"pop": "Growing · higher-income",
        "en": {"sport": "Cycling", "age": "30–55", "gender": "Male-leaning",
               "communities": "Broad · affluent urban", "regions": "Klang Valley · Penang · JB",
               "also": "Running · triathlon"},
        "ms": {"sport": "Berbasikal", "age": "30–55", "gender": "Cenderung lelaki",
               "communities": "Luas · bandar berpendapatan tinggi", "regions": "Lembah Klang · Pulau Pinang · JB",
               "also": "Larian · triatlon"}},
    "motorsport": {"pop": "Big event draw (Sepang)",
        "en": {"sport": "Motorsport (MotoGP)", "age": "18–40", "gender": "Male-leaning",
               "communities": "Broad", "regions": "Klang Valley + nationwide fans",
               "also": "Football · automotive"},
        "ms": {"sport": "Motorsport (MotoGP)", "age": "18–40", "gender": "Cenderung lelaki",
               "communities": "Luas", "regions": "Lembah Klang + peminat seluruh negara",
               "also": "Bola sepak · automotif"}},
    "esports": {"pop": "Explosive youth growth",
        "en": {"sport": "E-sports", "age": "15–30", "gender": "Male-leaning (female rising)",
               "communities": "Broad · urban youth", "regions": "Nationwide",
               "also": "Football · streaming"},
        "ms": {"sport": "E-sukan", "age": "15–30", "gender": "Cenderung lelaki (wanita meningkat)",
               "communities": "Luas · belia bandar", "regions": "Seluruh negara",
               "also": "Bola sepak · streaming"}},
    "futsal": {"pop": "Huge participation base",
        "en": {"sport": "Futsal", "age": "15–35", "gender": "Male-leaning",
               "communities": "Broad · urban youth", "regions": "Nationwide urban",
               "also": "Football"},
        "ms": {"sport": "Futsal", "age": "15–35", "gender": "Cenderung lelaki",
               "communities": "Luas · belia bandar", "regions": "Bandar seluruh negara",
               "also": "Bola sepak"}},
    "hockey": {"pop": "Niche but historic",
        "en": {"sport": "Hockey", "age": "School–35", "gender": "Balanced",
               "communities": "Strong Malay & Indian · school-linked", "regions": "Selected states (KL · Johor · Perak)",
               "also": "Football"},
        "ms": {"sport": "Hoki", "age": "Sekolah–35", "gender": "Seimbang",
               "communities": "Kuat Melayu & India · berkait sekolah", "regions": "Negeri terpilih (KL · Johor · Perak)",
               "also": "Bola sepak"}},
    "basketball": {"pop": "Urban youth niche",
        "en": {"sport": "Basketball", "age": "15–35", "gender": "Balanced",
               "communities": "Urban · strong Chinese community", "regions": "Urban centres",
               "also": "NBA following"},
        "ms": {"sport": "Bola keranjang", "age": "15–35", "gender": "Seimbang",
               "communities": "Bandar · kuat komuniti Cina", "regions": "Pusat bandar",
               "also": "Ikutan NBA"}},
}


def profiles() -> list[dict[str, object]]:
    """Senarai profil audiens sukan (untuk lapisan sajian)."""
    return [{"key": k, "pop": v["pop"], "en": v["en"], "ms": v["ms"]} for k, v in SPORTS_AUDIENCE.items()]
