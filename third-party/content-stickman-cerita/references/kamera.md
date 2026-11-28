# Kamera sinematik — panduan lengkap

Mesin punya **satu kamera virtual** per adegan: `x, y` (titik dunia di tengah layar), `z` (zoom), `r` (roll/miring), `blur` (rack focus).
Latar tersusun dari lapisan jauh → dekat, jadi saat kamera bergerak **parallax** terjadi sendiri (langit & bukit bergeser pelan, semak depan cepat).
Kamera bukan hiasan: setiap gerakan harus **menjawab satu pertanyaan** — *apa yang baru ingin ditunjukkan ke penonton, dan kenapa gambar diam tidak cukup?*

> Dunia: lantai `y=0`, atas = negatif. Pose kamera bawaan `x=0, y=-300, z=1` memuat tokoh setinggi ±470 penuh. `z=2` = 2× lebih dekat.

---

## 1. Ukuran bidikan (`ukuran`) — pilih dulu sebelum bergerak

| `ukuran` | zoom | yang tampak | pakai untuk |
|---|---|---|---|
| `sangat_lebar` | 0.56 | seluruh tempat, tokoh kecil | pembuka lokasi (establishing), "dunia luas", kesepian, tiba di tempat baru |
| `lebar` | 0.86 | tokoh penuh + latar | default adegan; tokoh berjalan; grup 3 orang |
| `penuh` | 1.25 | satu tokoh kepala-kaki | aksi tubuh: lompat, senam, pose gaya |
| `sedang` | 1.9 | pinggang ke atas | dialog, reaksi, tokoh memegang benda |
| `dekat` | 3.0 | kepala + bahu | emosi, kaget, ide, momen penting |
| `sangat_dekat` | 5.2 | mata / mulut | detik drama: air mata, mata membelalak, "tiba-tiba…" |
| `insert` | `z` 2.5–4 di titik `x,y` | benda (jam, HP, surat) | menunjukkan benda/angka; pakai `{"x":..,"y":..,"z":3}` |

Menyebut `fokus`: `"raka"` atau daftar `["raka","bimo"]` (bidikan dua tokoh otomatis memuat semuanya). Tanpa `fokus` = tokoh pertama.
`dx`, `dy` menggeser titik pusat setelah `ukuran` dihitung (mis. beri ruang di depan hadap tokoh, atau tunjukkan benda di sebelahnya).

**Aturan komposisi singkat**
- **Ruang pandang:** tokoh yang `hadap` kanan diberi ruang di kanan (mesin sudah menggeser sedikit; tambah `dx` bila perlu).
- **Ruang kepala:** jangan potong kepala; pada `dekat` biarkan bagian atas rambut tetap terlihat.
- **Dua tokoh bicara:** bidikan `lebar`/`sedang` dua tokoh untuk pembuka, lalu **ganti-ganti `dekat`** pada yang sedang bicara/bereaksi (pola shot-reverse-shot).
- **Skala emosi:** makin kuat perasaan, makin dekat bidikan. Datar → lebar; naik → sedang; puncak → dekat/sangat_dekat; lega → tarik mundur.
- **Jangan biarkan bidikan sama > 4 detik tanpa perubahan.** Mesin menambah dorongan pelan 5% + napas halus otomatis, tapi itu bukan pengganti keputusan sutradara: sisipkan gerakan, ganti ukuran, atau potong.
- **Jangan pernah mendarat di frame kosong:** kamera tiba di tempat yang tokoh/benda utamanya sudah ada.

---

## 2. Katalog gerakan (`kamera.gerak[]`)

Setiap gerakan: `{"jenis": ..., "t": 1.2 | "kata": "frasa", "dur": 1.5, "ease": "io", "ke": {...}}`.
`ke` = target (ukuran/fokus/x/y/z/r/blur/dx/dy/z_kali). Gerakan berurutan, masing-masing mulai dari posisi akhir yang sebelumnya.
Easing: `io` (default, halus awal-akhir) · `out` (cepat lalu melambat) · `in` · `back` (melewati lalu kembali) · `spring` · `snap` (sangat cepat).

### Gerak dasar
| `jenis` | efek | parameter penting | rasa & pemakaian |
|---|---|---|---|
| `pindah` | ke pose mana pun | `ke`, `dur` | serbaguna |
| `push` / `mendekat` | **dolly-in**: makin dekat | `ke.ukuran` atau `kali` (default 1.4), `dur` 1.2–4 | fokus perhatian, tekanan, rasa ingin tahu. Push **lambat 3–5 dtk** = ketegangan/keintiman; **cepat 0.8 dtk** = kejutan |
| `pull` / `menjauh` | **dolly-out**: mundur | `ke.ukuran` / `kali` | **reveal** (ternyata ada orang lain / tempatnya besar), kesepian, lega, penutup |
| `pan` | geser **horizontal** | `ke.fokus` / `ke.x` / `dx` | mengikuti pandangan, pindah dari tokoh A ke B, menyapu latar |
| `tilt` | geser **vertikal** | `ke.y` / `dy` | menunjuk ke atas/bawah, melihat gedung tinggi, menyusuri tubuh |
| `crane` | tilt naik besar + sedikit tarik mundur | `ke.y`, `ke.z` | "wow" ke langit/papan nama, harapan, awal baru |
| `terbang` | **fly-to**: zoom-out sebentar lalu masuk ke target | `ke`, `dip` (0.12–0.5 otomatis) | pindah antar titik jauh dalam satu set tanpa potong (dari jam ke tokoh, dari tokoh ke jendela) |
| `potong` | **jump cut** instan ke pose | `ke` | ganti sudut tegas pada jeda ucapan; ritme komedi |
| `zoom_cepat` | snap-zoom 0.25 dtk | `ke` / `kali` | kejutan, "HAH?!", punchline |
| `whip` | **whip-pan** + motion blur | `ke.fokus`/`x`, `dur` 0.38 | pindah cepat antar tokoh, energi, komedi; bunyi whoosh otomatis |
| `reveal` | = `pull` dari bidikan dekat | mulai `awal: dekat`, `ke: lebar` | tunjukkan konteks setelah detail |

### Kamera yang **hidup** (overlay, bisa ditumpuk)
| `jenis` | efek | parameter | catatan |
|---|---|---|---|
| `ikut` | **tracking/follow**: kamera menempel pada tokoh yang berjalan, sedikit tertinggal (lag 0.5 dtk) dan memberi ruang di depan | `fokus`, `sampai` (detik / `sampai_kata`), `dx`, `lag`, `z` | wajib untuk adegan jalan/lari: latar bergeser parallax, tokoh tetap di sekitar tengah. Tutup dengan gerakan lain setelah `sampai` |
| `punch` | zoom "tendangan" lalu kembali | `kuat` 0.08–0.25, `dur` 0.45 | tepat pada kata/benturan; + bunyi *thud* otomatis |
| `goyang` | guncangan peluruh | `kuat` 4–16 (px), `dur` 0.4–1.0 | alarm, ledakan, marah, tabrakan, gempa; kecil (4–7) = gemetar cemas |
| `miring` | **dutch angle** (roll) | `r` derajat (2–6), `dur` | tidak nyaman, mabuk, mimpi, situasi "ada yang salah"; kembalikan dengan `miring` `r:0` |
| `fokus` | **rack focus**: latar blur | `blur` 4–9, `dur` | pisahkan tokoh dari latar saat momen batin; `blur:0` mengembalikan |
| `ayun` | **orbit semu**: kamera mengayun kiri-kanan, lapisan parallax bergeser | `kuat` 40–90, `periode` 4–7, `sampai` | adegan santai/dreamy, memperlihatkan kedalaman ruangan tanpa tokoh bergerak |

Efek layar pendamping (`efek[]`): `garis_kecepatan` (radial, untuk kejutan/ngebut), `flash`, `vinyet` (sudut menggelap: malam, fokus, sedih), `gelap`, `bar` (letterbox sinematik), `hujan`, `salju`. (Jangan pakai `konfeti` / partikel kecil.)

---

## 3. Waktu gerakan: taruh di **jeda & kata kunci**

1. **Gerakan besar di jeda napas** narator (antar kalimat/koma). Gerakan yang menimpa kata penting membuat kata itu hilang.
2. **Kata kunci = pemicu.** `{"kata": "tiba-tiba", "jenis": "punch"}`, `{"kata": "ternyata", "jenis": "pull"}`.
   Frasa yang umum (mis. "jadi") → pakai dua kata, atau `"urutan": 1` untuk kemunculan ke-2 (0 = pertama).
3. **Mulai sedikit sebelum kata** (`"geser": -0.2`) untuk gerak yang perlu tiba tepat saat kata diucapkan; mulai pada kata untuk reaksi.
4. **Ritme:** dalam 60 detik, ±12–18 perubahan kamera (gerak atau potong). Adegan emosional boleh jarang tapi dalam; adegan komedi rapat.
5. **Satu gerakan utama per ide.** Hindari push + pan + miring + goyang di kalimat yang sama kecuali klimaks.

---

## 4. Resep per momen cerita

| Momen | Resep kamera |
|---|---|
| **Pembuka / hook** | mulai `insert` benda kunci (jam 07:00, surat) `z 3.4` + `goyang` kecil → `terbang`/`pull` ke `lebar` memperlihatkan tokoh |
| **Memperkenalkan lokasi** | `sangat_lebar` + `ayun` pelan, atau `crane` dari lantai ke papan nama (SMP) |
| **Tokoh tiba/berjalan** | `lebar` + `ikut` (dx ±100) ; tiba: lepas `ikut`, `tilt`/`crane` ke tujuan |
| **Percakapan 2 orang** | bidikan dua tokoh `lebar` → `push` `sedang` dua tokoh → bergantian `dekat` per pembicara (`pan` pendek atau `potong`) |
| **Kejutan** | `zoom_cepat` ke `dekat` + `garis_kecepatan` + `flash` + ikon `tanda_seru`; setelahnya `pull` pelan |
| **Ide / "aha"** | `push` pelan → `punch` tepat di kata "ide" + ikon `bohlam` |
| **Sedih / sepi** | `pull` sangat pelan ke `lebar`/`sangat_lebar`, tokoh kecil di sudut, `vinyet` + latar malam/sore, tanpa goyang |
| **Tegang / ancaman** | `push` sangat lambat + `miring` 3° + `vinyet`; potong ke `sangat_dekat` mata di puncak |
| **Lucu / komedi** | `potong` cepat, `punch` di punchline, `whip` antar reaksi, diam sejenak (3–4 frame hold) sebelum punchline |
| **Marah / benturan** | `goyang` 10–14 + `punch` 0.2 + `garis_kecepatan` |
| **Mimpi / lamunan** | `ayun` + `fokus` blur 5 + transisi `fade` / `kedip` |
| **Waktu berlalu** | potong ke `insert` jam/matahari, atau transisi `fade`; perubahan `waktu` latar (pagi→sore→malam) |
| **Mengakhiri / emosi hangat** | `pull` panjang 4–5 dtk ke `lebar`, `miring` 2° opsional, `vinyet`, fade keluar |
| **Rangkuman** | adegan `komik` (grid panel) lalu `zoom` ke satu panel |
| **Perbandingan A vs B** | `lebar` dua tokoh, `pan` ke A saat A dibahas, `pan` ke B; atau dua panel komik berdampingan |

---

## 5. Transisi antar adegan (`transisi` di adegan **tujuan**)

| `jenis` | rasa | pakai saat |
|---|---|---|
| `potong` | tegas | lokasi sama, ritme cepat, dialog |
| `geser` (`arah` kiri/kanan/atas/bawah) | berpindah tempat | ganti lokasi; **default otomatis** bila `latar`/`waktu` berubah |
| `whip` | energik + blur | komedi, aksi, "tiba-tiba di sekolah!" |
| `iris` (`x`,`y` 0–1) | klasik kartun | ganti lokasi riang, fokus pada tokoh (`x,y` = posisi tokoh di layar) |
| `fade` | waktu berlalu | pagi→malam, akhir bab, sedih |
| `flash` | kejut | momen "aha"/kaget |
| `zoom` | masuk ke dalam | masuk ke pikiran/benda |
| `kedip` | kelopak menutup-membuka | tidur, bangun, pingsan |
| `wipe` | garis sapuan | rangkuman, daftar |
Durasi 0.35–0.7 dtk. Jangan memakai transisi berbeda di setiap adegan — pilih 2–3 jenis dan konsisten; sisanya `potong`.

---

## 6. Kamera & format

- **16:9 (1920×1080)** — bahasa bawaan seluruh tabel di atas.
- **9:16 (1080×1920)** — bidang pandang lebih sempit: naikkan satu tingkat (`lebar`→`penuh`, `sedang`→`dekat`), dua tokoh bersebelahan harus lebih dekat (`x` selisih ≤ 350), `pan` dipakai lebih sering daripada bidikan lebar; subtitle otomatis naik ke 80% tinggi.

## 7. Uji kamera sebelum render penuh
`python3 render.py <proyek> --strip N --draft` → deretan 9 frame adegan ke-N (`out/qc/strip_NN.jpg`). **Lihat gambarnya**: apakah tokoh tetap di dalam frame di setiap langkah? Apakah ada frame kosong, kepala terpotong, atau gerak yang menimpa kata penting? Perbaiki `kamera.gerak` lalu ulangi.
