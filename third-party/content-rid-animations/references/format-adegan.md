# Format proyek.json & tipe adegan

```json
{
  "judul": "Apa itu Inflasi",
  "ukuran": [1920, 1080],        // 16:9. Untuk Reels/TikTok/Shorts: [1080, 1920]
  "fps": 30,
  "vo": "input/vo.mp3",          // relatif ke folder proyek; null = draf tanpa suara
  "musik": "auto",               // "auto" (musik ceria orisinal) | "none" | "input/musik.mp3"
  "vol_musik": 0.16,             // opsional
  "sfx": true,                   // pop/ding/whoosh otomatis
  "adegan": [ { ... }, { ... } ]
}
```

## Field umum (semua tipe)

| field | isi |
|---|---|
| `tipe` | salah satu tipe di bawah |
| `narasi` | **teks VO persis** yang diucapkan selama adegan ini. Dipakai untuk membagi waktu & memunculkan item tepat saat katanya diucapkan. Urutan adegan = urutan naskah; gabungan semua `narasi` = seluruh naskah. |
| `tokoh` | `"pria"` (peci hitam, baju koko putih) atau `"wanita"` (hijab pink) untuk adegan satu tokoh |
| `ekspresi` | `senang` (default), `senyum`, `tertawa`, `kaget`, `mikir`, `marah`, `sedih`, `bingung` |
| `pose` | `diam`, `tunjuk_samping` (telapak terbuka menunjuk panel), `tunjuk_atas` (jari telunjuk), `lambai`, `kepal`, `dua_kepal`, `mikir` (tangan di dagu) |
| `posisi` | `"kiri"` (default) / `"kanan"` — sisi tokoh; panel di sisi lain |
| `bicara` | siapa yang mulutnya bergerak: `pria` / `wanita` / `keduanya` / `tidak`. Default = tokoh adegan |
| `latar` | `kamar`, `kafe`, `bukit`, `biru`, `krem`, `hijau`, `ungu`, `pink`, `kuning`, `abu` (tiap tipe punya default) |
| `mulai` | (opsional) paksa detik mulai adegan — untuk koreksi sinkron manual |
| `durasi` | (opsional, hanya tanpa VO) lama adegan |

Teks mendukung `**kata**` = warna aksen (merah di kartu, kuning di pil judul) dan `\n` = baris baru.

## Tipe adegan

### `dialog` — dua tokoh mengobrol (pembuka, transisi, reaksi)
```json
{"tipe":"dialog","latar":"kamar","bicara":"pria",
 "pria":{"ekspresi":"senang","pose":"tunjuk_samping"},"wanita":{"ekspresi":"senyum"},
 "balon":"Teks balon kata (opsional, maks ±12 kata)","narasi":"..."}
```
Di 9:16 sebaiknya selalu pakai `balon`, supaya bagian atas layar tidak kosong.

### `tanya` — satu tokoh + balon besar berisi pertanyaan, kata kunci di pil biru
```json
{"tipe":"tanya","tokoh":"pria","teks":"Apa itu","sorot":"Inflasi?","narasi":"..."}
```

### `definisi` — tokoh + balon definisi, kata penting **merah**
```json
{"tipe":"definisi","tokoh":"wanita","teks":"Inflasi adalah **kenaikan harga** barang ...",
 "hias":"koin_naik","narasi":"..."}
```
`hias`: `"koin_naik"` (tumpukan koin + panah naik), nama ikon apa pun, atau `null`.

### `contoh` — grafik garis naik + 1–4 item dengan harga lama → baru
```json
{"tipe":"contoh","tokoh":"pria","judul":"Contohnya...",
 "item":[{"ikon":"roti","label":"Roti","dari":"Rp10.000","ke":"Rp12.000"}],"narasi":"..."}
```
`dari`/`ke` opsional (bisa dipakai untuk angka apa pun, misal "2010" → "2024").

### `ikon_grid` — judul + 2–4 ikon dalam lingkaran kuning (penyebab, jenis, langkah)
```json
{"tipe":"ikon_grid","judul":"Penyebab Inflasi",
 "item":[{"ikon":"troli","label":"Permintaan\nmeningkat"}],"narasi":"..."}
```
Tanpa `tokoh` = panel lebar penuh. Dengan `tokoh` = tokoh di samping.

### `daftar` — tokoh + pil judul + 2–4 baris kartu ikon+teks (dampak, ciri, fakta)
```json
{"tipe":"daftar","tokoh":"wanita","judul":"Dampak Inflasi",
 "item":[{"ikon":"celengan","teks":"Tabungan nilainya berkurang"}],"narasi":"..."}
```

### `checklist` — tokoh telunjuk ke atas + daftar centang hijau (tips, solusi)
```json
{"tipe":"checklist","tokoh":"pria","judul":"Cara Menghadapinya","ikon":"dompet",
 "item":["Atur pengeluaran dengan bijak","..."],"narasi":"..."}
```

### `angka` — angka besar merah (statistik, persen, nominal)
```json
{"tipe":"angka","tokoh":"wanita","ekspresi":"kaget","angka":"5,2%","label":"inflasi tahunan 2022","ikon":"grafik","narasi":"..."}
```
Pakai hanya untuk angka yang benar/bersumber; kalau ilustrasi, tulis "contoh" di label.

### `banding` — dua kartu kiri (merah) vs kanan (hijau): dulu vs sekarang, salah vs benar
```json
{"tipe":"banding","judul":"Dulu vs Sekarang",
 "kiri":{"judul":"Dulu","ikon":"koin","teks":"Rp10.000 dapat 5 roti"},
 "kanan":{"judul":"Sekarang","ikon":"roti","teks":"Rp10.000 dapat 3 roti"},"narasi":"..."}
```

### `sorak` — dua tokoh mengepalkan tangan + balon kuning (kesimpulan, semangat)
```json
{"tipe":"sorak","balon":"Dengan memahami inflasi, kita lebih siap!","narasi":"..."}
```

### `judul` — kartu judul pembuka, dua tokoh melambai
```json
{"tipe":"judul","judul":"Apa itu Inflasi?","subjudul":"Penjelasan 1 menit","narasi":"..."}
```

### `penutup` — pil judul navy di atas bukit hijau + 1–3 ikon (CTA)
```json
{"tipe":"penutup","teks":"Yuk, mulai kelola\nkeuanganmu sekarang!","ikon":["celengan","koin","tanaman"],"narasi":"..."}
```
Tambah `"tokoh":"wanita"` kalau mau tokoh melambai di pojok.

## Daftar ikon

`koin, celengan, tanaman, troli, kardus_turun, uang_naik, roti, bbm, susu, grafik, centang, dompet, rumah, lampu, jam, buku, tameng, bintang, hp, keranjang, seru, tanya, silang, orang, kalender, toko, target`

Nama yang tidak ada → bintang. Butuh ikon baru? Tambah fungsi `ic_<nama>(p)` di `scripts/rid2d.py` (kotak 200×200 unit, outline otomatis lewat `Pen`) lalu daftarkan di dict `IKON`, cek dengan `python3 scripts/galeri.py galeri.png`.
