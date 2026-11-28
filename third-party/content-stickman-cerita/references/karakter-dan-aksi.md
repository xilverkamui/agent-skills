# Tokoh stikman — rig, ekspresi, pose, casting

**Gaya:** kepala putih sangat besar bergaris hitam tebal, mata oval hitam berkilau, pipi merona, mulut huruf-D merah, badan kecil berseragam (kemeja putih + dasi), lengan-kaki garis tipis, tangan = bulatan putih, sepatu hitam. Mulut **bergerak mengikuti energi suara VO** pada tokoh yang `bicara`. Berkedip tiap ±3 dtk, bernapas pelan.
**Jangan mengubah gaya** ini kecuali user meminta. Lihat semuanya: `python3 scripts/galeri.py galeri.png --semua`.

## Tokoh bawaan (`tokoh` di proyek.json)
`raka` (pria, rambut jambul hitam, dasi biru) · `nadia` (hijab pink, dasi merah, rok hitam) · `bimo` (rambut keriting) · `dimas` (kacamata) · `sari` (hijab putih) · `tika` (kuncir) · `ayah` · `ibu` (hijab hijau) · `guru` (uban, kacamata, kumis) · `bu_guru` (hijab ungu) · `kakek` (peci, jenggot) · `adik` (kecil, skala 0.8).

Pemeran sendiri / modifikasi:
```json
"tokoh": { "raka": "raka",
           "andi":  {"dasar": "raka", "rambut": "keriting", "kemeja": "kuning", "dasi": null, "bawah_warna": "biru"},
           "wati":  {"dasar": "nadia", "hijab": "ungu", "hijab_tua": [140,100,200], "kacamata": true} }
```
Field: `rambut` (`jambul keriting rapi botak kuncir bob uban`) · `rambut_warna` · `hijab` + `hijab_tua` · `kemeja` · `kemeja_garis` · `dasi` (warna/null) · `bawah` (`celana`/`rok`) · `bawah_warna` · `sepatu` · `kacamata` · `kumis` · `jenggot` · `peci` · `topi` · `bulu_mata` · `skala`.
Warna: nama (`putih hitam merah biru pink kuning hijau ungu oranye coklat abu navy krem …`) atau `[r,g,b]`.
Tokoh yang **menjadi tokoh utama konsisten di semua adegan** (id sama, penampilan sama). Tokoh figuran: preset berbeda, jangan ganti-ganti warna.

## Ekspresi (`ekspresi`)
`senang` `tenang` `tertawa` `kaget` `marah` `mikir` · `sedih` `malu` `ngantuk` `menguap` `tidur` `semangat` `panik` `bangga` `jahil` `cemberut` `cemas` `lega` `terpana` `datar`
(alias: senyum=tenang, kecewa=sedih, bingung=mikir, ketawa=tertawa, heran=kaget, kesal=cemberut, takut=panik)
Ganti ekspresi di **setiap perubahan perasaan** (tiap ±2–3 dtk); wajah yang sama 8 detik terasa mati.
`lihat: [0.9, 0.2]` menggeser pupil/wajah (melirik kucing, melihat ke pembicara).

## Pose (`pose`)
- **Berdiri/gestur:** `diam` `santai` `lambai` `lambai2` `tunjuk` `tunjuk_kiri` `tunjuk_atas` `ide` `pinggang` `jempol` `silang` `sorak` `peregangan` `garuk` `mikir` `dagu` `kaget` `sedih` `marah` `kepal` `menyerahkan` `angkat_tangan` `angkat_bahu` `tepuk` `menguap` `pegang_dada` `hormat` `memeluk` `bersandar` `membungkuk` `hormat_bendera`
- **Bergerak:** `jalan` `lari` `berjinjit` (otomatis dipakai bila ada `ke_x` dengan gaya jalan/lari)
- **Duduk (badan turun, paha mendatar ke arah `hadap`):** `duduk` `duduk_santai` `duduk_hp` `duduk_nulis` `duduk_game` `duduk_sorak`
- **Memegang:** `pegang_hp` `pegang_buku` `menulis`
- **Rebah:** `tidur` (kepala di kiri) `tidur_kanan` — taruh `x,y` sehingga kepala jatuh di bantal; di latar `kamar` pakai `x:-158, y:-167` (tokoh tidur di kasur, selimut menutupi badan). Duduk di kasur: `x:-250, y:-30`, pose `peregangan`/`kaget`.

Posisi bantu per latar (lantai y=0; tokoh duduk memakai y lantai juga):
| situasi | x | catatan |
|---|---|---|
| duduk di meja belajar | `230` | `latar: ruang_belajar`, pose `duduk_nulis`, meja menutupi kaki |
| duduk di sofa | `-200` | `latar: ruang_tamu`, `duduk_game`/`duduk_hp` |
| tidur di kasur | `-158`, `y -167` | `latar: kamar`, pose `tidur`, `selimut: true` |
| berdiri depan gedung | `-100…200` | `sekolah_luar` papan SMP di x≈260 |
Jarak dua tokoh berdiri berdampingan ±300–400 satuan.

## Aksi & ikon di atas kepala
`"efek": "tanda_seru"` (kaget) · `tanya` (bingung) · `bohlam` (ide) · `hati` (suka) · `zzz` (tidur) · `keringat` (cemas) · `bintang` (pusing) · `kilau` (senang) · `not` (bersenandung). Pasangkan dengan ekspresi + gerak kamera agar terbaca.

## Dialog
- Satu pembicara per kalimat: `"bicara": true` (atau jendela waktu) pada pembicara; yang lain `lihat` ke arah pembicara.
- Pakai **balon** untuk dialog tanpa suara tokoh (narator membacakan cerita). Balon + mulut bergerak dalam adegan yang sama hanya jika VO memang suara tokoh itu.
