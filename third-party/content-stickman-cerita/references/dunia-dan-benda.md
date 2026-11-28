# Latar (set) dan benda

Latar bergaya komik pastel dengan garis hitam; lantai `y=0`; tiap latar punya lapisan **belakang** (di belakang tokoh) dan **depan** (meja, selimut, semak yang menutupi tokoh bagian bawah) + lapisan jauh yang bergeser lebih lambat saat kamera bergerak.

| `latar` | isi | posisi penting |
|---|---|---|
| `kamar` | kasur + bantal + boneka kelinci, selimut, nakas + **jam digital** (`jam`), jendela dengan matahari/bulan, rak tanaman, lukisan, karpet | kasur x −640…50; jam x 185 y −214; jendela x 520 |
| `sekolah_luar` (`sekolah`) | gedung berpapan **SMP** (`papan`), pintu biru, bendera, semak, bukit | gedung x≈260; papan y≈−420 |
| `taman` (`halaman_sekolah`) | pohon, bangku, semak, bunga, bukit | bangku x 330 |
| `kelas` | papan tulis (`papan_tulis` isi teks), jendela, jam dinding, meja guru, meja siswa depan | papan x −520…220 |
| `ruang_belajar` (`meja_belajar`) | rak buku penuh, papan gabus + sticky note, meja + lampu menyala (cahaya hangat di malam), tumpukan buku | meja x −60…760, kursi x 230 |
| `ruang_tamu` (`ruang_keluarga`) | sofa biru + bantal, **kucing oranye** (ekor bergoyang), TV, tanaman | sofa x −200 |
| `jalan` (`komplek`, `kampung`) | deretan rumah + pohon berulang (cocok tracking panjang), trotoar, tiang lampu | tak terbatas ke kiri-kanan |
| `kantin` | kios beratap garis, makanan, meja-bangku | |
| `lapangan` | rumput berpola, garis, gawang | |
| `rumah_depan` | rumah, pintu, jendela, pagar, halaman | pintu x 0 |
| `meja_makan` (`dapur`) | meja dengan piring & susu, kursi, jendela | meja x −640…560 |
| `padang` (`luar`) | bukit hijau berlapis, bunga, pohon | |
| `polos` | gradasi pastel (`warna`) + lingkaran lembut (bersih, tanpa partikel kecil) | judul, penjelasan, bab baru |

`waktu`: `pagi` (kuning hangat) · `siang` (biru terang) · `sore` (oranye) · `malam` (biru tua, bintang, bulan, lampu menyala, tokoh diwarnai lembut).
Latar baru: tambahkan fungsi `xxx_b(c,t,o)` / `xxx_f(c,t,o)` di `scripts/dunia.py` (salinan proyek) lalu daftarkan di `SET` — hanya bila cerita benar-benar butuh tempat lain (rumah sakit, pasar, stasiun). Ikuti gaya: isian pastel, garis `OUT` 4 satuan, tanpa gradasi rumit.

## Benda
Genggam (`bawa` / `benda`): `hp buku pensil stik bola kertas gelas payung kado bunga uang laptop weker jam`.
Ikon komik (`benda`/`efek` aktor): `tanda_seru tanya hati bintang kilau zzz bohlam not keringat centang silang koin debu gerak awan_pikir awan`.
Onomatopoeia lewat `teks` gaya `seru` ("BRAK!", "TING!", "ZZZ…", "DUAR!").
