# Dari naskah ke cerita bergambar

## A. Hanya topik/ide → tulis naskah dulu
Tulis naskah cerita (narator + dialog singkat bila perlu), tampilkan, lalu dalam pesan yang sama minta **satu kali**: file voiceover dari naskah itu + rasio (16:9 atau 9:16). Tak ada mesin suara di skill ini; jangan mengarang suara. Boleh buat **draf bisu** (`"vo": null`) dengan jelas disebut draf.

### Bentuk cerita yang bekerja untuk konten stikman
1. **Hook (0–3 dtk):** tampilkan akibat/pertanyaan paling menarik, bukan perkenalan. ("Jam 07:00 — dan Raka belum bangun.") Frame pertama sudah berisi gerak + tokoh/benda utama.
2. **Tokoh & keinginan (3–10 dtk):** siapa, ingin apa, di mana (1 lokasi jelas).
3. **Hambatan → naik (tengah):** tiap adegan memberi **satu hal baru** (orang baru, masalah, keputusan). Selang-seling lebar/dekat, tenang/ramai.
4. **Titik balik:** satu momen yang dibayar kamera + musik + ikon (kaget, ide, salah paham terungkap).
5. **Akhir:** akibat + rasa (lega, lucu, hangat) + 1 kalimat pesan/pertanyaan. Tidak ada outro panjang.
Panjang adegan 3–8 detik (±8–20 kata). Kalimat narator pendek, lisan, ber-ritme; satu ide per kalimat.
Genre yang cocok: kisah harian siswa, cerita inspiratif/moral, kejadian lucu, dongeng modern, kisah "bagaimana kalau…", pelajaran hidup dari satu peristiwa, kisah sahabat/keluarga.

## B. Ada VO + naskah (zero-prompt)
1. `proyek_baru.py` menyalin VO, membersihkan tag (`[excited]`, `[short pause]`) dari naskah, mencetak `DURASI_VO`.
2. Pecah naskah menjadi adegan **berurutan, tanpa ada kalimat terlewat**; `narasi` = potongan persis (tanda baca boleh sama).
3. Untuk tiap adegan putuskan **berurutan**: (a) lokasi + waktu, (b) siapa di layar & posisinya, (c) aksi/ekspresi per kalimat, (d) **kamera** (ukuran awal → gerakan → alasan), (e) ikon/teks/efek, (f) transisi masuk, (g) suasana musik.
4. Tulis rencana adegan (satu baris per adegan) sebelum membuat JSON:
```
00:00–05:60 | HOOK   | kamar pagi, Raka tidur, weker 07:00 | insert jam z3.4 + goyang → terbang ke Raka → pull lebar | zzz | musik santai
05:60–10:10 | KAGET  | Raka duduk di kasur, "!"           | sedang + punch di "hari ini" → zoom_cepat dekat "SMP" | flash + garis kecepatan | semangat
```
5. Jadwal adegan ditempel ke jeda VO terdekat; kata dipetakan perkiraan dari panjang huruf di bagian bersuara. Jika user punya hasil alignment kata (`input/words.json`: `[{"w":"kata","s":1.2,"e":1.5}, …]` urut sesuai naskah), mesin memakainya otomatis → sinkron lebih presisi. Jujur ke user: tanpa itu sinkron kata ±0,2 dtk.

## C. Prinsip sutradara (wajib dipikirkan, bukan hiasan)
- **Tunjukkan, jangan hanya subtitle.** Tiap adegan harus mengandung aksi yang bisa dipahami dengan suara dimatikan.
- **Tokoh utama konsisten** (id, penampilan, ekspresi khasnya). Lawan bicara berbeda siluet (rambut/hijab/kacamata).
- **Variasi:** hindari 3 adegan beruntun dengan ukuran bidikan, latar, dan pose sama. Ganti ukuran atau lokasi atau tempo.
- **Ruang kosong:** tokoh kecil di tengah lantai kosong terlihat lemah → dekatkan kamera atau isi dengan figuran/benda.
- **Emosi lewat tubuh:** ekspresi + pose + ikon + kamera bersama-sama. Satu saja tidak cukup untuk momen penting.
- **Rasa waktu:** gunakan `waktu` (pagi→siang→sore→malam) dan label jam untuk lompatan waktu.
- **Hormati fakta:** cerita boleh fiksi, tetapi klaim fakta/angka di layar harus benar; tandai fiksi sebagai cerita bila perlu. Jangan menampilkan tokoh asli/merek nyata sebagai karikatur.
