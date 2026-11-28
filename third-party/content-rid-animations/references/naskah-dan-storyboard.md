# Menulis naskah & memecah jadi adegan

## Pola cerita (sama seperti contoh "Apa itu Inflasi?")

1. **Sapaan / hook** (`dialog` atau `judul`) — dua tokoh, satu menyapa dan memancing topik. 3–6 dtk.
2. **Pertanyaan** (`tanya`) — "Apa itu ___?" dengan kata kunci di pil biru. 2–3 dtk.
3. **Definisi** (`definisi`) — satu kalimat jelas, 1–3 kata kunci ditandai **merah**. 4–6 dtk.
4. **Contoh nyata** (`contoh` / `banding` / `angka`) — angka & benda sehari-hari (Rp, harga, warung). 5–8 dtk.
5. **Penyebab / jenis** (`ikon_grid`) — 3 ikon. 5–7 dtk.
6. **Dampak / fakta** (`daftar`) — 3 baris. 5–7 dtk.
7. **Solusi / tips** (`checklist`) — 3 poin centang. 5–7 dtk.
8. **Kesimpulan** (`sorak`) — satu kalimat semangat di balon kuning. 3–5 dtk.
9. **CTA** (`penutup`) — ajakan singkat. 2–4 dtk.

Tidak wajib persis 9 — topik pendek boleh 5–6 adegan, topik panjang boleh mengulang tipe
(misal 2× `daftar`). Hindari tipe yang sama berturut-turut; selang-seling tokoh pria & wanita
supaya terasa seperti percakapan.

## Aturan naskah

- Bahasa Indonesia santai-sopan ("kita", "teman-teman"), kalimat pendek, ±2,5 kata/detik.
- 45–90 dtk untuk satu konsep. Maksimal ±5 menit.
- Angka ditulis seperti diucapkan di VO ("sepuluh ribu"), tapi di layar pakai format "Rp10.000".
- Teks di layar = ringkasan narasi, bukan salinan seluruh kalimat. Maks ±12 kata per balon,
  ±6 kata per baris daftar.
- Fakta & angka harus benar. Kalau hanya ilustrasi, tulis "contoh" / "misalnya".

## Format naskah yang ditampilkan ke user (mode topik)

```
JUDUL: Apa itu Inflasi?   ·   ±45 detik   ·   16:9

[1] PRIA (senang, di kamar):  Halo teman-teman! Hari ini kita mau ngobrolin ...
[2] PRIA (tanya):             Sebenarnya, apa sih inflasi itu?
[3] WANITA (definisi):        Inflasi adalah kenaikan harga barang dan jasa ...
...
```
Nomor = adegan. Tag tokoh menentukan `tokoh`/`bicara`. Kalau VO dibuat satu narator saja,
tetap boleh: tokohnya tetap "berbicara" bergantian sesuai tag.

## Memecah VO + naskah yang sudah ada (mode zero-prompt)

- Bagi naskah per kalimat/ide → satu adegan per ide (2–8 dtk).
- `narasi` tiap adegan = potongan teks naskah persis (urutan sama). Jangan ada teks naskah yang
  hilang atau dobel — timing dihitung dari proporsi panjang teks lalu di-snap ke jeda di VO.
- Kalau naskah berlabel pembicara (mis. "A:", "B:", "Rid:", "Nisa:"), petakan pembicara
  pertama → `pria`, kedua → `wanita` (kecuali jelas sebaliknya dari nama/konteks).
- Tag ElevenLabs `[excited]`, `[short pause]` dsb. bukan teks — sudah dibuang otomatis.
- Item daftar/checklist muncul saat kata pertamanya diucapkan, jadi tulis teks item memakai
  kata yang benar-benar ada di narasi.
