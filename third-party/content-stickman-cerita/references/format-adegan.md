# Format `proyek.json` — semua field

```json
{
  "judul": "Sehari Bersama Raka",
  "ukuran": [1920, 1080],          // 9:16 → [1080, 1920]
  "fps": 30,
  "vo": "input/vo.mp3",            // null = draf bisu (mulut tokoh bergerak palsu)
  "musik": "auto",                 // "auto" | "none" | "input/musik.mp3"
  "mood_musik": "ceria",           // suasana bawaan bila adegan tak menyebut
  "vol_musik": 0.17,               // opsional
  "subtitle": true,                // subtitle per kata (kata yang diucapkan menyala kuning)
  "gaya_subtitle": "komik",        // "komik" (putih bergaris hitam) | "pil" (kotak putih)
  "fade_masuk": 0.5, "fade_keluar": 0.8,
  "sfx": true,
  "tokoh": { "raka": "raka", "guru": {"dasar": "guru", "kacamata": false} },   // daftar pemeran (lihat karakter-dan-aksi.md)
  "adegan": [ { ... } ]
}
```

## Adegan biasa

| field | isi |
|---|---|
| `latar` | `kamar` `sekolah_luar` `taman` `kelas` `ruang_belajar` `ruang_tamu` `jalan` `kantin` `lapangan` `rumah_depan` `meja_makan` `padang` `polos` (alias di `dunia-dan-benda.md`) |
| `waktu` | `pagi` `siang` `sore` `malam` — mengubah langit, matahari/bulan, warna keseluruhan, lampu menyala |
| `narasi` | **potongan naskah persis** yang diucapkan selama adegan ini, berurutan, lengkap. Dipakai membagi waktu, subtitle, dan pemicu `kata` |
| `musik` | suasana musik adegan: `ceria santai hangat sedih tegang semangat lucu misteri malam` |
| `tokoh` | daftar aktor (di bawah) |
| `kamera` | `{ "awal": ..., "gerak": [...] }` — lihat `kamera.md` |
| `benda` | benda/ikon bebas |
| `balon` | gelembung ucapan/pikiran |
| `teks` | judul, kapsul, onomatopoeia |
| `efek` | efek layar penuh |
| `sfx` | `[{ "t"|"kata": .., "jenis": "pop|ding|boing|thud|whoosh|sparkle|alarm|tanya|zzz|seru|kilat|iris", "gain": 1 }]` efek suara tambahan |
| `transisi` | transisi **masuk** ke adegan ini: `"geser"` atau `{"jenis":"iris","x":0.4,"y":0.6,"dur":0.6}` |
| `mulai` / `durasi` | paksa waktu mulai (koreksi sinkron) / lama adegan (hanya tanpa VO) |
| `opsi` | opsi khusus latar: `jam` ("07:00"), `alarm` (weker bergetar+bunyi), `papan` (teks papan nama: "SMP"/"KANTIN"), `papan_tulis` (tulisan di papan kelas), `selimut` (true/false), `selimut_warna`, `warna` (latar `polos`), `lampu_nyala`, `kursi_x`, `lampu_x`, `sofa_x`. Boleh juga ditulis langsung di adegan (`"jam": "07:00"`) |

### Waktu: `t` atau `kata`
Setiap item bertanggal (aksi, benda, balon, teks, efek, gerakan kamera) memakai salah satu:
- `"t": 1.5` — detik sejak awal adegan
- `"kata": "hari pertamanya"` — saat frasa itu diucapkan (diperkirakan dari VO). Tambah `"geser": -0.2` untuk maju/mundur, `"urutan": 1` untuk kemunculan ke-2.
- penutup: `"sampai": 4.0` atau `"sampai_kata": "frasa"`.
Frasa tidak ditemukan → render mencetak `[PERIKSA] ...` dan memakai t=0. **Selalu baca baris `[PERIKSA]`** dan perbaiki ejaan frasa.

### Aktor (`tokoh[]`)
```json
{ "id": "raka", "x": -200, "y": 0, "skala": 1.0, "hadap": "kanan|kiri|depan",
  "pose": "diam", "ekspresi": "senang", "ransel": true, "bawa": "hp", "lapis": 0,
  "bicara": true,                          // mulut bergerak mengikuti VO (dialog), atau [[t0,t1],[t0,t1]]
  "masuk":  {"dari": "kiri|kanan|atas|pop", "t": 0.2, "dur": 1.0, "gaya": "jalan|lari|jatuh|lompat|pop", "jarak": 1300},
  "keluar": {"ke": "kanan|kiri", "t": 6, "dur": 1.2},
  "aksi": [ ... ] }
```
`aksi[]` — tiap entri boleh berisi (semua opsional): `pose`, `ekspresi`, `hadap`, `lihat: [x,y]` (arah pupil −1…1), `bawa`, `ransel`, `skala`, `bicara`, gerak `ke_x`/`ke_y` + `durasi` + `gaya` (`jalan` `lari` `geser` `lompat`), dan ikon di atas kepala `efek` + `efek_dur`.
Pose lama→baru dicampur halus 0,3 dtk. `ke_x` otomatis memutar `hadap` dan menggerakkan kaki/lengan.
Dialog dengan dua suara: beri `bicara` pada **pembicara saja**; narator murni = tanpa `bicara`.

`bawa`: `"hp"` | `"buku"` | `"stik"` | `"pensil"` | `"bola"` | `"kertas"` | `"gelas"` | `"payung"` | `"kado"` | `"bunga"` | `"uang"` | `"laptop"` — atau `{"jenis":"hp","tangan":"kiri","layar":[r,g,b],"play":true}`.

### Benda & ikon bebas (`benda[]`)
`{ "jenis": "bohlam", "x": 100, "y": -500, "skala": 1, "t": 2, "sampai": 4, "ikut": "raka", "dx": 80, "dy": -40, "melayang": 40, "lapis": "belakang|depan" }`
`ikut` menempelkan ke kepala tokoh. Jenis: benda (daftar `bawa` + `weker`/`jam` dengan `"jam":"07:00"`) dan ikon `tanda_seru tanya hati bintang kilau zzz bohlam not keringat centang silang koin debu gerak awan_pikir awan`.

### Balon (`balon[]`)
`{ "oleh": "raka", "teks": "Hai!", "kata": "melambai", "sampai": 5, "gaya": "bicara|pikir|teriak", "sisi": "kiri|kanan|auto", "lebar": 560, "ukuran": 40, "warna": "merah" }` — muncul di atas kepala, mengetik huruf demi huruf, selalu di dalam layar. Maks ±10 kata.

### Teks (`teks[]`)
`{ "isi": "SMP!", "gaya": "seru|judul|kapsul|kata_besar", "posisi": "atas|tengah|bawah|kiri_atas|kanan_atas|[0.7,0.3]", "t": 2, "sampai": 4, "ukuran": 62, "warna": "biru", "sudut": -7 }`
- `judul`: pil berwarna (seperti "Karakter Pria") untuk bab/judul. `kapsul`: label kecil putih ("Pagi · 07:00"). `seru`: onomatopoeia komik ("BRAAK!", "TING!") — goyang & miring. `kata_besar`: satu kata besar bergaris.
- Jangan menggandakan subtitle: teks layar hanya untuk judul, label, angka, onomatopoeia.

### Efek (`efek[]`)
`flash` (`dur`,`kuat`) · `gelap` (`kuat`,`sampai`) · `vinyet` (`kuat`,`sampai`) · `garis_kecepatan` (`dur`) · `bar` (letterbox) · `hujan` · `salju`. **Jangan pakai `konfeti`** (partikel kecil dilarang; pakai ikon `kilau`/`hati`/`bintang` atau `flash`).

## Adegan komik (`"tipe": "komik"`)
Halaman panel (seperti lembar komik): tiap panel = mini-adegan lengkap.
```json
{ "tipe": "komik", "grid": [3, 2], "narasi": "...", "warna_halaman": "krem",
  "zoom": { "panel": 3, "kata": "belajar", "dur": 1.2 },   // kamera masuk ke satu panel sampai memenuhi layar
  "panel": [ { "muncul": {"kata": "berangkat"}, "latar": "sekolah_luar", "tokoh": [...], "kamera": {"awal": {"ukuran":"lebar"}} } ] }
```
Panel muncul memantul saat `muncul`; waktu di dalam panel dihitung sejak ia muncul. Cocok untuk rangkuman, "jadwal sehari", perbandingan, atau pembuka "ini yang akan terjadi".
