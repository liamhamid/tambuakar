# Deploy Tambuakar ke Oracle Always Free (24 jam, private)

> Tanpa SSH. Server auto-pasang sendiri guna **cloud-init**. Data & token duduk di
> server (kau kawal); repo ni cuma kod collector (tiada rahsia).

## Langkah (untuk Liam — GUMUM guide)

**1. Jana Tailscale auth key**
- login.tailscale.com/admin/settings/keys → **Generate auth key** → salin
  (guna sekali, boleh set reusable/ephemeral ikut suka).

**2. Fikir satu API token**
- Mana-mana rahsia panjang (cth 24+ aksara rawak). Ajis guna ini untuk baca API.

**3. Buat VM di Oracle**
- Console → **Compute → Instances → Create instance**
- Image: **Ubuntu** · Shape: **Always Free (Ampere/ VM.Standard.A1.Flex atau Micro)**
- **Advanced options → Management → cloud-init / user data:** paste kandungan
  `oracle-cloud-init.yaml`, GANTI `<<TAILSCALE_AUTHKEY>>` dan `<<API_TOKEN>>` dahulu.
- **Create.**

**4. Siap**
- Selepas ~2-3 minit, server:
  - masuk Tailscale (nama `tambuakar`)
  - jalankan **API** di `http://tambuakar:8790` (private, dalam tailnet kau)
  - kutip data pertama + set cron harian
- Uji dari device dalam tailnet: `http://tambuakar:8790/health` → `{"status":"ok"}`

## Sambung Ajis
Ajis (NAS) tarik Gold read-only:
```
GET http://tambuakar:8790/entities        Header: Authorization: Bearer <API_TOKEN>
```
GUMUM sambungkan bahagian ini di sebelah Ajis.

## Keselamatan
- API **fail-closed** (wajib token). Port 8790 **tidak dibuka** ke internet (firewall
  Oracle default) — hanya tailnet kau capai. Data mentah kekal di server.
